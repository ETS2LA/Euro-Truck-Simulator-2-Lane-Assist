using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using JetBrains.Annotations;
using TruckLib;
using static Extractor.PathUtils;

namespace Extractor.Zip
{
    /// <summary>
    /// A ZIP archive reader which can handle archives with deliberately corrupted local file headers.
    /// </summary>
    public class ZipReader : IDisposable, IFileSystem
    {
        /// <summary>
        /// The entries in this archive.
        /// </summary>
        public Dictionary<string, CentralDirectoryFileHeader> Entries { get; private set; }

        char IFileSystem.DirectorySeparator => throw new NotImplementedException();

        private BinaryReader reader;
        private long endOfCentralDirOffset = -1;
        private EndOfCentralDirectory eocdRecord;

        private ZipReader() { }

        public static ZipReader Open(string path)
        {
            var zip = new ZipReader();
            zip.reader = new BinaryReader(File.OpenRead(path));
            zip.reader.BaseStream.Position = 0;

            zip.endOfCentralDirOffset = BinaryUtils.FindBytesBackwards(zip.reader, EndOfCentralDirectory.Signature);
            if (zip.endOfCentralDirOffset < 0)
            {
                throw new InvalidDataException("No End Of Central Directory record found - probably not a zip file.");
            }
            zip.ReadEndOfCentralDirectoryRecord();
            zip.ReadCentralDirectory();

            return zip;
        }

        /// <summary>
        /// Extracts the given entry from the archive to a stream.
        /// </summary>
        /// <param name="entry">The entry to extract.</param>
        /// <param name="outputStream">The stream to which the extracted file will be written.</param>
        /// <exception cref="NotSupportedException">Thrown if the compression method used 
        /// is not supported.</exception>
        public void GetEntry(CentralDirectoryFileHeader entry, Stream outputStream)
        {
            // Ignore the entire local file header, just like ETS2/ATS
            reader.BaseStream.Position = entry.LocalFileHeaderOffset + 26;
            var fileNameLength = reader.ReadUInt16();
            var extraFieldLength = reader.ReadUInt16();
            reader.BaseStream.Position += fileNameLength + extraFieldLength;

            switch (entry.CompressionMethod)
            {
                case CompressionMethod.Deflate:
                    var ds = new DeflateStream(reader.BaseStream, CompressionMode.Decompress);
                    BinaryUtils.CopyStream(ds, outputStream, entry.UncompressedSize);
                    break;

                case CompressionMethod.None:
                    BinaryUtils.CopyStream(reader.BaseStream, outputStream, entry.UncompressedSize);
                    break;

                default:
                    throw new NotSupportedException(
                        $"Unsupported compression method {(int)entry.CompressionMethod}.");
            }
        }

        /// <summary>
        /// Reads the End Of Central Directory record from the file.
        /// </summary>
        private void ReadEndOfCentralDirectoryRecord()
        {
            reader.BaseStream.Position = endOfCentralDirOffset + EndOfCentralDirectory.Signature.Length;
            eocdRecord = new EndOfCentralDirectory
            {
                DiskNr = reader.ReadUInt16(),
                CentralDirectoryDiskNr = reader.ReadUInt16(),
                DiskEntries = reader.ReadUInt16(),
                TotalEntries = reader.ReadUInt16(),
                CentralDirectorySize = reader.ReadUInt32(),
                CentralDirectoryOffset = reader.ReadUInt32(),
                CommentLength = reader.ReadUInt16()
            };
            eocdRecord.Comment = reader.ReadBytes(eocdRecord.CommentLength);
        }

        /// <summary>
        /// Reads the Central Directory file headers from a stream.
        /// </summary>
        private void ReadCentralDirectory()
        {
            reader.BaseStream.Position = eocdRecord.CentralDirectoryOffset;
            Entries = [];

            while (reader.BaseStream.Position < eocdRecord.CentralDirectoryOffset + eocdRecord.CentralDirectorySize)
            {
                var signature = reader.ReadBytes(4);
                if (!signature.SequenceEqual(CentralDirectoryFileHeader.Signature))
                {
                    return;
                }

                var file = new CentralDirectoryFileHeader
                {
                    VersionMadeBy = reader.ReadUInt16(),
                    VersionNeeded = reader.ReadUInt16(),
                    Flags = reader.ReadUInt16(),
                    CompressionMethod = (CompressionMethod)reader.ReadUInt16(),
                    FileModificationTime = reader.ReadUInt16(),
                    FileModificationDate = reader.ReadUInt16(),
                    Crc32 = reader.ReadUInt32(),
                    CompressedSize = reader.ReadUInt32(),
                    UncompressedSize = reader.ReadUInt32(),
                    FileNameLength = reader.ReadUInt16(),
                    ExtraFieldLength = reader.ReadUInt16(),
                    FileCommentLength = reader.ReadUInt16(),
                    DiskNr = reader.ReadUInt16(),
                    InternalAttribs = reader.ReadUInt16(),
                    ExternalAttribs = reader.ReadUInt32(),
                    LocalFileHeaderOffset = reader.ReadUInt32()
                };
                file.FileName = Encoding.UTF8.GetString(reader.ReadBytes(file.FileNameLength));
                file.ExtraField = reader.ReadBytes(file.ExtraFieldLength);
                file.FileComment = reader.ReadBytes(file.FileCommentLength);
                Entries.TryAdd(file.FileName, file);
            }
        }

        public void Dispose()
        {
            reader?.Dispose();
            GC.SuppressFinalize(this);
        }

        bool IFileSystem.FileExists(string path)
        {
            RemoveInitialSlash(ref path);
            return Entries.ContainsKey(path);
        }

        bool IFileSystem.DirectoryExists(string path)
        {
            RemoveInitialSlash(ref path);
            if (!path.EndsWith('/'))
                path += '/';

            return Entries.TryGetValue(path, out var entry) 
                && entry.UncompressedSize == 0;
        }

        // NOTE: This implementation is an addition to the original code.
        //       It's implemented to satisfy the IFileSystem interface.
        // - Tumppi066
        IList<string> IFileSystem.GetFiles(string path)
        {
            RemoveInitialSlash(ref path);
            return Entries.Keys
                .Where(x => x.StartsWith(path) && !x.EndsWith('/'))
                .Select(x => x.StartsWith('/') ? x : '/' + x)
                .ToList();
        }

        byte[] IFileSystem.ReadAllBytes(string path)
        {
            RemoveInitialSlash(ref path);
            var entry = Entries[path];
            using var ms = new MemoryStream();
            GetEntry(entry, ms);
            var buffer = ms.ToArray();
            return buffer;
        }

        string IFileSystem.ReadAllText(string path)
            => (this as IFileSystem).ReadAllText(path, Encoding.UTF8);

        string IFileSystem.ReadAllText(string path, Encoding encoding)
        {
            RemoveInitialSlash(ref path);
            return encoding.GetString((this as IFileSystem).ReadAllBytes(path));
        }

        Stream IFileSystem.Open(string path)
        {
            RemoveInitialSlash(ref path);
            var entry = Entries[path];
            var ms = new MemoryStream();
            GetEntry(entry, ms);
            ms.Position = 0;
            return ms;
        }

        string IFileSystem.GetParent(string path) 
            => GetParent(path);
    }

    /// <summary>
    /// Represents an End Of Central Directory record.
    /// </summary>
    public struct EndOfCentralDirectory
    {
        public static readonly byte[] Signature = [0x50, 0x4b, 0x05, 0x06];
        public ushort DiskNr;
        public ushort CentralDirectoryDiskNr;
        public ushort DiskEntries;
        public ushort TotalEntries;
        public uint CentralDirectorySize;
        public uint CentralDirectoryOffset;
        public ushort CommentLength;
        public byte[] Comment;
    }

    /// <summary>
    /// Represents a Central Directory file header.
    /// </summary>
    public struct CentralDirectoryFileHeader
    {
        public static readonly byte[] Signature = [0x50, 0x4b, 0x01, 0x02];
        public ushort VersionMadeBy;
        public ushort VersionNeeded;
        public ushort Flags;
        public CompressionMethod CompressionMethod;
        public ushort FileModificationTime;
        public ushort FileModificationDate;
        public uint Crc32;
        public uint CompressedSize;
        public uint UncompressedSize;
        public ushort FileNameLength;
        public ushort ExtraFieldLength;
        public ushort FileCommentLength;
        public ushort DiskNr;
        public ushort InternalAttribs;
        public uint ExternalAttribs;
        public uint LocalFileHeaderOffset;
        public string FileName;
        public byte[] ExtraField;
        public byte[] FileComment;
    }

    /// <summary>
    /// The compression method with which a file in a ZIP archive is compressed.
    /// </summary>
    public enum CompressionMethod
    {
        None = 0,
        Deflate = 8,
    }
}
