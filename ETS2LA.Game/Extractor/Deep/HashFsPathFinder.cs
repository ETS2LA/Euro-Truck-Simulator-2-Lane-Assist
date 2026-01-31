using Avalonia.Controls.Converters;
using Extractor.Properties;
using Sprache;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TruckLib;
using TruckLib.HashFs;
using static Extractor.PathUtils;

namespace Extractor.Deep
{
    /// <summary>
    /// Searches the entries of a HashFS archive for paths contained in it.
    /// </summary>
    public class HashFsPathFinder
    {
        /// <summary>
        /// File paths that were discovered by <see cref="Find"/>.
        /// </summary>
        public HashSet<string> FoundFiles { get; private set; }

        /// <summary>
        /// Decoy file paths that were discovered by <see cref="Find"/>.
        /// Since decoy files typically contain junk data, they are kept separate
        /// from all other discovered paths.
        /// </summary>
        public HashSet<string> FoundDecoyFiles { get; private set; }

        /// <summary>
        /// File paths that are referenced by files in this archive.
        /// </summary>
        public HashSet<string> ReferencedFiles { get; private set; }

        /// <summary>
        /// This is used to find the absolute path of tobj files that are referenced in 
        /// mat files for which the mat path was not found and the tobj is referenced as
        /// relative path only.
        /// </summary>
        private static readonly string[] RootsToSearchForRelativeTobj = [
            "/material", "/model", "/model2", "/prefab", "/prefab2", "/vehicle"
        ];
        
        /// <summary>
        /// The HashFS reader.
        /// </summary>
        private readonly IHashFsReader reader;

        /// <summary>
        /// Additional start paths which the user specified with the <c>--additional</c> parameter.
        /// </summary>
        private readonly IList<string> additionalStartPaths;

        /// <summary>
        /// Paths that have been visited so far.
        /// </summary>
        private readonly HashSet<string> visited;

        /// <summary>
        /// Entries that have been visited so far.
        /// </summary>
        private readonly HashSet<IEntry> visitedEntries;

        /// <summary>
        /// Entries which have been identified as containing junk data.
        /// </summary>
        private readonly Dictionary<ulong, IEntry> junkEntries;

        /// <summary>
        /// The <see cref="FilePathFinder"/> instance.
        /// </summary>
        private readonly FilePathFinder fpf;

        public HashSet<string> ConsumedSuis { get; init; } = [];

        /// <summary>
        /// Directories discovered during the first phase which might contain tobj files.
        /// This is used to find the absolute path of tobj files that are referenced in 
        /// mat files for which the mat path was not found and the tobj is referenced as
        /// relative path only.
        /// </summary>
        private readonly HashSet<string> dirsToSearchForRelativeTobj;

        public HashFsPathFinder(IHashFsReader reader, IList<string> additionalStartPaths = null, 
            Dictionary<ulong, IEntry> junkEntries = null, AssetLoader multiModWrapper = null)
        {
            this.reader = reader;
            this.additionalStartPaths = additionalStartPaths;
            this.junkEntries = junkEntries ?? [];

            visited = [];
            visitedEntries = [];
            FoundFiles = [];
            dirsToSearchForRelativeTobj = [];
            ReferencedFiles = [];

            IFileSystem fsToUse = multiModWrapper is null ? reader : multiModWrapper;
            fpf = new FilePathFinder(fsToUse, visited, ReferencedFiles, 
                dirsToSearchForRelativeTobj, ConsumedSuis);
        }

        /// <summary>
        /// Scans the archive for paths and writes the results to <see cref="FoundFiles"/> 
        /// and <see cref="FoundDecoyFiles"/>.
        /// </summary>
        public void Find()
        {
            var potentialPaths = LoadStartPaths();
            if (additionalStartPaths is not null)
                potentialPaths.UnionWith(additionalStartPaths);
            ExplorePotentialPaths(potentialPaths);

            var morePaths = FindPathsInUnvisited();
            ExplorePotentialPaths(morePaths);

            VisitMapSectorPaths("europe");
            VisitMapSectorPaths("usa");

            FoundDecoyFiles = FindDecoyPaths();
        }

        /// <summary>
        /// Loads the set of initial paths which the path finder will check for.
        /// </summary>
        /// <returns>The initial paths.</returns>
        private static PotentialPaths LoadStartPaths()
        {
            using var inMs = new MemoryStream(Resources.DeepStartPaths);
            using var ds = new GZipStream(inMs, CompressionMode.Decompress);
            using var outMs = new MemoryStream();
            ds.CopyTo(outMs);
            var lines = Encoding.UTF8.GetString(outMs.ToArray());
            return LinesToHashSet(lines);
        }

        private void ExplorePotentialPaths(PotentialPaths potentialPaths)
        {
            do
            {
                potentialPaths = FindPaths(potentialPaths);
                potentialPaths.ExceptWith(visited);
            }
            while (potentialPaths.Count > 0);
        }

        /// <summary>
        /// Scans entries which were not visited in the first phase.
        /// </summary>
        /// <returns>Newly discovered paths.</returns>
        private PotentialPaths FindPathsInUnvisited()
        {
            PotentialPaths potentialPaths = [];

            var unvisited = reader.Entries.Values.Except(visitedEntries);
            foreach (var entry in unvisited)
            {
                visitedEntries.Add(entry);
                
                if (junkEntries.ContainsKey(entry.Hash))
                {
                    continue;
                }

                if (entry.IsDirectory)
                {
                    continue;
                }
                if (entry is EntryV2 v2 && v2.TobjMetadata is not null)
                {
                    continue;
                }

                byte[] fileBuffer;
                try
                {
                    fileBuffer = reader.Extract(entry, "")[0];
                }
                catch (InvalidDataException)
                {
                    #if DEBUG
                        Console.WriteLine($"Unable to decompress, likely junk: {entry.Hash:X16}");
                    #endif
                    junkEntries.TryAdd(entry.Hash, entry);
                    continue;
                }
                catch (Exception)
                {
                    #if DEBUG
                        Debugger.Break();
                    #endif
                    continue;
                }

                var type = FileTypeHelper.Infer(fileBuffer);
                if (type == FileType.Material)
                {
                    // The file path of automats is derived from the CityHash64 of its content,
                    // so we add this automat path to the set of paths to check
                    var contentHash = CityHash.CityHash64(fileBuffer, (ulong)fileBuffer.Length);
                    var contentHashStr = contentHash.ToString("x16");
                    var automatPath = $"/automat/{contentHashStr[..2]}/{contentHashStr}.mat";
                    potentialPaths.Add(automatPath);
                }
                try
                {
                    var paths = fpf.FindPathsInFile(fileBuffer, null, type);
                    foreach (var path in paths)
                    {
                        potentialPaths.Add(path, visited);
                    }
                }
                catch (Exception ex)
                {
                    #if DEBUG
                        var extension = FileTypeHelper.FileTypeToExtension(type);
                        Console.Error.WriteLine($"Unable to parse {entry.Hash:X16}{extension}: " +
                            $"{ex.GetType().Name}: {ex.Message}");
                    #endif
                    continue;
                }
            }

            return potentialPaths;
        }

        /// <summary>
        /// Finds decoy variants of paths that have been discovered.
        /// </summary>
        /// <returns>The decoy paths.</returns>
        private HashSet<string> FindDecoyPaths()
        {
            HashSet<string> decoyPaths = [];

            foreach (var path in FoundFiles)
            {
                var cleaned = RemoveNonAsciiOrInvalidChars(path);
                if (cleaned != path)
                {
                    // TODO: Fix this if need be, had to comment out because of .HashPath().
                    // - Tumppi066
                    // if (junkEntries.ContainsKey(reader.HashPath(cleaned)))
                    // {
                    //     decoyPaths.Add(cleaned);
                    // }
                    // else if (reader.FileExists(cleaned))
                    // {
                    //     var entry = reader.GetEntry(cleaned);
                    //     visited.Add(cleaned);
                    //     visitedEntries.Add(entry);
                    //     decoyPaths.Add(cleaned);
                    // }
                }
            }

            return decoyPaths;
        }

        /// <summary>
        /// Searches for potential paths in the given files and directories.
        /// All visited paths are added to <see cref="visited"/>, all visited paths that exist
        /// in the archive are added to <see cref="FoundFiles"/>, and all new potential paths
        /// that have been discovered are returned.
        /// </summary>
        /// <param name="inputPaths">The files and directories to search.</param>
        /// <returns>The discovered potential paths.</returns>
        private PotentialPaths FindPaths(PotentialPaths inputPaths)
        {
            PotentialPaths potentialPaths = [];
            foreach (var path in inputPaths)
            {
                if (visited.Contains(path))
                    continue;

                reader.Traverse(path,
                    (dir) => 
                    {
                        var isNew = visited.Add(dir);
                        if (isNew)
                        {
                            visitedEntries.Add(reader.GetEntry(dir));
                        }
                        return isNew;
                    },
                    (file) =>
                    {
                        try
                        {
                            var paths = FindPathsInFile(file);
                            potentialPaths.UnionWith(paths);
                            ReferencedFiles.UnionWith(paths);
                        }
                        catch (Exception ex)
                        {
                            #if DEBUG
                            Console.Error.WriteLine($"Unable to parse {ReplaceControlChars(file)}: " +
                                $"{ex.GetType().Name}: {ex.Message.Trim()}");
                            #endif
                        }
                    },
                    (_) => { }
                    );
            }
            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in the given file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <returns>Paths referenced in the file. If the file does not exist, an empty
        /// set is returned.</returns>
        private HashSet<string> FindPathsInFile(string filePath)
        {
            visited.Add(filePath);

            // TODO: Fix this if need be, had to comment out because of .HashPath().
            // - Tumppi066
            // if (junkEntries.ContainsKey(reader.HashPath(filePath)))
            // {
            //     return [];
            // }

            if (!reader.FileExists(filePath))
            {
                return [];
            }

            FoundFiles.Add(filePath);
            var fileEntry = reader.GetEntry(filePath);
            visitedEntries.Add(fileEntry);
            AddDirToDirsToSearchForRelativeTobj(filePath);

            // Skip HashFS v2 tobj/dds entries because we don't need to scan those
            if (fileEntry is EntryV2 v2 && v2.TobjMetadata is not null)
            {
                return [];
            }

            var fileType = FileTypeHelper.PathToFileType(filePath);
            if (FilePathFinder.IgnorableFileTypes.Contains(fileType))
            {
                return [];
            }

            var fileBuffer = reader.Extract(fileEntry, filePath)[0];
            if (fileType == FileType.Unknown)
            {
                fileType = FileTypeHelper.Infer(fileBuffer);
            }
            return fpf.FindPathsInFile(fileBuffer, filePath, fileType);
        }

        private void VisitMapSectorPaths(string mapName)
        {
            const int extent = 70;
            for (int z = -extent; z < extent + 1; z++)
            {
                for (int x = -extent; x < extent + 1; x++)
                {
                    VisitSector(x, z, mapName);
                }
            }

            void VisitSector(int x, int z, string mapName)
            {
                var sectorName = $"sec{x:+0000;-0000;+0000}{z:+0000;-0000;+0000}";
                var basePath = $"/map/{mapName}/{sectorName}.base";

                if (!visited.Add(basePath))
                {
                    return;
                }

                if (reader.TryGetEntry(basePath, out var baseEntry) != EntryType.File)
                {
                    return;
                }

                visitedEntries.Add(baseEntry);
                FoundFiles.Add(basePath);

                string[] extensions = ["aux", "snd", "data", "desc", "layer"];
                foreach (var extension in extensions)
                {
                    var path = Path.ChangeExtension(basePath, extension);
                    visited.Add(path);
                    if (reader.TryGetEntry(path, out var entry) == EntryType.File)
                    {
                        visitedEntries.Add(entry);
                        FoundFiles.Add(path);
                    }
                }
            }
        }

        private void AddDirToDirsToSearchForRelativeTobj(string filePath)
        {
            foreach (var root in RootsToSearchForRelativeTobj)
            {
                if (filePath.StartsWith(root))
                {
                    dirsToSearchForRelativeTobj.Add(GetParent(filePath));
                }
            }
        }
    }
}
