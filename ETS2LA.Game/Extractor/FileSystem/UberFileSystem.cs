using System;
using System.Collections.Generic;
using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.FileSystem.Hash;
using ETS2LA.Game.Extractor.FileSystem.Zip;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.FileSystem
{
    public class UberFileSystem
    {
        private static readonly Lazy<UberFileSystem> _instance = new Lazy<UberFileSystem>(() => new UberFileSystem());
        public static UberFileSystem Instance => _instance.Value;

        internal Dictionary<ulong, UberFile> Files { get; } = new Dictionary<ulong, UberFile>();
        internal Dictionary<ulong, UberDirectory> Directories { get; } = new Dictionary<ulong, UberDirectory>();
        private readonly List<ArchiveFile> _archiveFiles = new List<ArchiveFile>();

        /// <summary>
        /// Reads and adds a single file to the filesystem
        /// Checks if file is an SCS Hash file, if not, assumes it's a zip file
        /// </summary>
        /// <param name="path">Path for the archive file to add</param>
        /// <returns>Whether or not the file was parsed correctly</returns>
        public bool AddSourceFile(string path)
        {
            if (!File.Exists(path))
            {
                Logger.Error($"Could not find file '{path}'");
                return false;
            }
            var buff = new byte[4];
            using (var f = File.OpenRead(path))
            {
                f.Seek(0, SeekOrigin.Begin);
                f.Read(buff, 0, 4); // read magic bytes (first 4 bytes of file)
            }
            if (BitConverter.ToUInt32(buff, 0) == Consts.ScsMagic)
            {
                var hashFile = new HashArchiveFile(path);
                if (hashFile.Parse(this))
                {
                    _archiveFiles.Add(hashFile);
                    return true;
                }
                else
                {
                    Logger.Error($"Could not load hash file '{path}'");
                    return false;
                }
            }
            else
            {
                var zipFile = new ZipArchiveFile(path);
                if (zipFile.Parse(this))
                {
                    _archiveFiles.Add(zipFile);
                    return true;
                }
                else
                {
                    Logger.Error($"Could not load zip file '{path}'");
                    return false;
                }
            }

        }

        /// <summary>
        /// Adds all files from the specified directory matching the filter to the filesystem
        /// </summary>
        /// <param name="path">Path to the directory where to find the files to include</param>
        /// <param name="searchPattern">Search pattern to select specific files eg. "*.scs"</param>
        /// <returns>Whether or not all files were added successfully</returns>
        public bool AddSourceDirectory(string path, string searchPattern = "*.scs")
        {
            if (!Directory.Exists(path))
            {
                Logger.Error($"Could not find directory '{path}'");
                return false;
            }
            var scsFilesPaths = Directory.GetFiles(path, searchPattern);

            var result = true;

            foreach (var scsFilePath in scsFilesPaths)
            {
                var fileResult = AddSourceFile(scsFilePath);
                if (!fileResult) result = false;
            }
            return result;
        }

        /// <summary>
        /// Tries to find the directory by the given path
        /// </summary>
        /// <param name="path">Path for the wanted directory</param>
        /// <returns>
        /// <see cref="UberDirectory"/> for the given path
        /// <para>Null if path was not found</para>
        /// </returns>
        public UberDirectory GetDirectory(string path)
        {
            return GetDirectory(CityHash.CityHash64(PathHelper.EnsureLocalPath(path)));
        }

        /// <summary>
        /// Tries to find the directory by the given hash
        /// </summary>
        /// <param name="pathHash">Hash for the wanted directory</param>
        /// <returns>
        /// <see cref="UberDirectory"/> for the given hash
        /// <para>Null if hash was not found</para>
        /// </returns>
        public UberDirectory GetDirectory(ulong pathHash)
        {
            if (Directories.ContainsKey(pathHash))
            {
                return Directories[pathHash];
            }
            return null;
        }

        /// <summary>
        /// Tries to find the file by a given path
        /// </summary>
        /// <param name="path">Path for the wanted file</param>
        /// <returns>
        /// <see cref="UberFile"/> for the given path
        /// <para>Null if path was not found</para>
        /// </returns>
        public UberFile GetFile(string path)
        {
            return GetFile(CityHash.CityHash64(PathHelper.EnsureLocalPath(path)));
        }

        /// <summary>
        /// Tries to find the file by a given hash
        /// </summary>
        /// <param name="pathHash">Hash for the wanted file</param>
        /// <returns>
        /// <see cref="UberFile"/> for the given hash
        /// <para>Null if hash was not found</para>
        /// </returns>
        public UberFile GetFile(ulong pathHash)
        {
            if (Files.ContainsKey(pathHash))
            {
                return Files[pathHash];
            }
            return null;
        }
    }
}