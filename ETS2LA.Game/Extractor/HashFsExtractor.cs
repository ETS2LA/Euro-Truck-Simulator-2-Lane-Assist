using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TruckLib.HashFs;
using System.IO.Compression;
using TruckLib;
using System.Text.RegularExpressions;
using static Extractor.PathUtils;
using static Extractor.ConsoleUtils;
using static Extractor.TextUtils;

namespace Extractor
{
    /// <summary>
    /// A HashFS extractor which wraps TruckLib's HashFsReader.
    /// </summary>
    public class HashFsExtractor : Extractor
    {
        /// <summary>
        /// The underlying HashFsReader.
        /// </summary>
        public IHashFsReader Reader { get; private set; }

        public override IFileSystem FileSystem => Reader;

        /// <summary>
        /// Whether a "not found" message should be printed if a start path
        /// does not exist in the archive.
        /// </summary>
        public bool PrintNotFoundMessage { get; set; } = true;

        /// <summary>
        /// Junk entries identified by DeleteJunkEntries.
        /// </summary>
        protected Dictionary<ulong, IEntry> junkEntries = [];

        /// <summary>
        /// Entries idenfitied by DeleteJunkEntries which are likely to be junk, but may not be.
        /// </summary>
        protected Dictionary<ulong, IEntry> maybeJunkEntries = [];

        private bool hasIdentifiedJunk;

        /// <summary>
        /// Paths which will need to be renamed.
        /// </summary>
        protected Dictionary<string, string> substitutions;

        /// <summary>
        /// The number of files which have been extracted successfully.
        /// </summary>
        protected int numExtracted;

        /// <summary>
        /// The number of files which have been skipped because the output path
        /// already exists and <see cref="Options.SkipIfExists"/> is set.
        /// </summary>
        protected int numSkipped;

        /// <summary>
        /// The number of files which failed to extract.
        /// </summary>
        protected int numFailed;

        /// <summary>
        /// The number of paths passed by the user which were not found in the archive.
        /// </summary>
        protected int numNotFound;

        /// <summary>
        /// The number of files which were skipped because they have been identified
        /// as junk data.
        /// </summary>
        protected int numJunk;

        public HashFsExtractor(string scsPath, Options opt) : base(scsPath, opt)
        {
            PrintNotFoundMessage = !opt.ExtractAllInDir;

            Reader = HashFsReader.Open(scsPath, opt.ForceEntryTableAtEnd);
            PrintContentSummary();

            if (opt.Salt is not null)
                Reader.Salt = opt.Salt.Value;
            else
                FixSaltIfNecessary();

            IdentifyJunkEntries();
        }

        /// <inheritdoc/>
        public override void Extract(string outputRoot)
        {
            if (opt.StartPaths.Count == 1 && opt.StartPaths[0] == "/")
            {
                AssertRootNotMissingOrEmpty();
            }

            var pathsToExtract = GetPathsToExtract(Reader, opt.StartPaths, opt.Filters,
                (nonexistent) =>
                {
                    if (PrintNotFoundMessage)
                    {
                        Console.Error.WriteLine($"Path {ReplaceControlChars(nonexistent)} " +
                            $"was not found");
                        numNotFound++;
                    }
                }
            );
            substitutions = DeterminePathSubstitutions(pathsToExtract);

            ExtractFiles(pathsToExtract, outputRoot);

            WriteRenamedSummary(outputRoot);
            WriteModifiedSummary(outputRoot);
        }

        private void AssertRootNotMissingOrEmpty()
        {
            if (Reader.EntryExists("/") == EntryType.Directory)
            {
                var listing = Reader.GetDirectoryListing("/");
                if (listing.Subdirectories.Count == 0 && listing.Files.Count == 0)
                {
                    throw new RootEmptyException();
                }
            }
            else
            {
                throw new RootMissingException();
            }
        }

        protected void ExtractFiles(IList<string> pathsToExtract, string outputRoot, bool ignoreMissing = false)
        {
            foreach (var archivePath in pathsToExtract)
            {
                ExtractFile(archivePath, outputRoot, ignoreMissing);
            }
        }

        internal static Dictionary<string, string> DeterminePathSubstitutions(IList<string> pathsToExtract)
        {
            Dictionary<string, string> substitutions = [];
            foreach (var path in pathsToExtract)
            {
                var sanitized = SanitizePath(path);
                if (sanitized != path)
                {
                    substitutions.Add(path, sanitized);
                }
            }
            return substitutions;
        }

        internal static List<string> GetPathsToExtract(IHashFsReader reader, IList<string> startPaths, 
            IList<Regex> filters, Action<string> onVisitNonexistent)
        {
            List<string> pathsToExtract = [];
            foreach (var path in startPaths)
            {
                reader.Traverse(path, 
                    (_) => { }, 
                    (file) =>
                    {
                        if (file != "/" && MatchesFilters(filters, file))
                        {
                            pathsToExtract.Add(file);
                        }
                    },
                    onVisitNonexistent);
            }
            return pathsToExtract;
        }

        protected void ExtractFile(string archivePath, string outputRoot, bool ignoreMissing = false)
        {
            if (!Reader.FileExists(archivePath))
            {
                if (ignoreMissing)
                    return;
                else
                    throw new FileNotFoundException();
            }

            if (!substitutions.TryGetValue(archivePath, out string filePath))
            {
                filePath = archivePath;
            }
            var outputPath = Path.Combine(outputRoot, RemoveInitialSlash(filePath));
            if (archivePath != filePath)
            {
                renamedFiles.Add((archivePath, filePath));
            }

            if (!opt.Quiet)
            {
                var scsName = Path.GetFileName(ScsPath);
                PrintExtractionMessage(archivePath, scsName);
            }

            if (!Overwrite && File.Exists(outputPath))
            {
                numSkipped++;
                return;
            }

            ExtractToDisk(archivePath, outputPath);
        }

        protected void ExtractToDisk(string archivePath, string outputPath)
        {
            Reader.TryGetEntry(archivePath, out var entry);
            ExtractToDisk(entry, archivePath, outputPath);       
        }

        protected void ExtractToDisk(IEntry entry, string archivePath, string outputPath)
        {
            try
            {
                var buffers = Reader.Extract(entry, archivePath);

                var wasModified = PerformSubstitutionIfRequired(archivePath, ref buffers[0], substitutions);
                if (!opt.DryRun)
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(outputPath));
                    File.WriteAllBytes(outputPath, buffers[0]);
                }

                if (!opt.DryRun && entry is EntryV2 v2 && v2.TobjMetadata is not null)
                {
                    var ddsPath = Path.ChangeExtension(outputPath, "dds");
                    if (Overwrite || !File.Exists(ddsPath))
                    {
                        try
                        {
                            File.WriteAllBytes(ddsPath, buffers[1]);
                        }
                        catch (IOException ioex)
                        {
                            PrintExtractionFailure(Path.ChangeExtension(archivePath, "dds"),
                                ioex.Message);
                        }
                    }
                }

                numExtracted++;
                if (wasModified)
                    modifiedFiles.Add(archivePath);
            }
            catch (InvalidDataException idex)
            {
                PrintExtractionFailure(archivePath, idex.Message);
            }
            catch (AggregateException agex)
            {
                PrintExtractionFailure(archivePath, agex.ToString());
            }
            catch (IOException ioex)
            {
                PrintExtractionFailure(archivePath, ioex.Message);
            }
            catch (Exception ex)
            {
                PrintExtractionFailure(archivePath, ex.ToString());
            }
        }

        protected void IdentifyJunkEntries()
        {
            if (hasIdentifiedJunk)
                return;

            // Find all entries with duplicate offsets and group them by offset.
            var visitedOffsets = new Dictionary<ulong, IEntry>();
            var junk = new Dictionary<ulong, List<IEntry>>();
            foreach (var (_, entry) in Reader.Entries)
            {
                if (!visitedOffsets.TryAdd(entry.Offset, entry))
                {
                    if (!junk.TryGetValue(entry.Offset, out var list))
                    {
                        list = [visitedOffsets[entry.Offset]];
                        junk.Add(entry.Offset, list);
                    }
                    list.Add(entry);
                }
            }

            // At most one of these files may contain actual data, so let's try
            // to figure out which of these entries it could be.
            // Entries which are guaranteed to be junk are added to `junkEntries`;
            // entries which could potentially contain the actual file are added
            // to `maybeJunkEntries`.
            // Nothing in `junkEntries` is ever extracted. An entry in `maybeJunkEntries` 
            // is extracted if a path pointing to it exists.
            if (junk.Count > 0)
            {
                var allOffsets = Reader.Entries.Select(x => x.Value.Offset).Distinct().Order().ToList();
                foreach (var (offset, list) in junk)
                {
                    var idx = allOffsets.BinarySearch(offset);
                    var nextOffset = idx == allOffsets.Count - 1
                        ? (ulong)Reader.BaseReader.BaseStream.Length
                        : allOffsets[idx + 1];

                    Reader.BaseReader.BaseStream.Position = (long)offset;
                    var firstByte = Reader.BaseReader.ReadByte();
                    var isZlibCompressed = firstByte == 0x78; // probably good enough

                    long decompressedLength = -1;
                    if (isZlibCompressed)
                    {
                        try
                        {
                            Reader.BaseReader.BaseStream.Position = (long)offset;
                            var buffer = Reader.BaseReader.ReadBytes((int)(nextOffset - offset));
                            using var inMs = new MemoryStream(buffer);
                            using var zlibStream = new ZLibStream(inMs, CompressionMode.Decompress);
                            using var outMs = new MemoryStream();
                            zlibStream.CopyTo(outMs);
                            decompressedLength = outMs.Length;
                            var newPos = (ulong)Reader.BaseReader.BaseStream.Position;
                        }
                        catch 
                        {
                            isZlibCompressed = false;
                        }
                    }

                    foreach (var entry in list)
                    {
                        if (entry.IsCompressed != isZlibCompressed)
                        {
                            MarkAsConfirmedJunk(entry);
                        }
                        else if (nextOffset - entry.Offset < entry.CompressedSize)
                        {
                            MarkAsConfirmedJunk(entry);
                        }
                        else if (nextOffset - entry.Offset - entry.CompressedSize > 32)
                        {
                            MarkAsConfirmedJunk(entry);
                        }
                        else if (entry.IsCompressed)
                        {
                            if (entry.Size == decompressedLength)
                                MarkAsMaybeJunk(entry);
                            else
                                MarkAsConfirmedJunk(entry);
                        }
                        else
                        {
                            MarkAsMaybeJunk(entry);
                        }
                    }
                }
            }

            hasIdentifiedJunk = true;

            void MarkAsConfirmedJunk(IEntry entry)
            {
                junkEntries.Add(entry.Hash, entry);
                numJunk++;
            }

            void MarkAsMaybeJunk(IEntry entry)
            {
                maybeJunkEntries.Add(entry.Hash, entry);
                numJunk++;
            }
        }

        protected void FixSaltIfNecessary()
        {
            const string fileToTest = "manifest.sii";

            if (Reader.TryGetEntry(fileToTest, out var _) == EntryType.NotFound)
            {
                // No manifest => don't need to run this
                return;
            }

            try
            {
                // Decompresses correctly => no change needed
                Reader.Extract(fileToTest);
                return;
            }
            catch
            {
                // Otherwise, iterate all salts until we find the good one
                Console.Error.WriteLine("Salt may be incorrect; attempting to fix ...");
                for (int i = 0; i < ushort.MaxValue; i++)
                {
                    Reader.Salt = (ushort)i;
                    if (Reader.EntryExists(fileToTest) == EntryType.File)
                    {
                        try
                        {
                            Reader.Extract(fileToTest);
                            Console.Error.WriteLine($"Salt set to {i}");
                            return;
                        }
                        catch { /* Failed to decompress => continue */ }
                    }
                }
                Console.Error.WriteLine("Unable to find true salt");
            }
        }

        public override void PrintContentSummary()
        {
            var dirCount = Reader.Entries.Count(x => x.Value.IsDirectory);
            Console.Error.WriteLine($"Opened {Path.GetFileName(ScsPath)}: " +
                $"HashFS v{Reader.Version} archive; {Reader.Entries.Count} entries " +
                $"({Reader.Entries.Count - dirCount} files, {dirCount} directory listings)");
        }

        public override void PrintExtractionResult()
        {
            Console.Error.WriteLine($"{numExtracted} extracted " +
                $"({renamedFiles.Count} renamed, {modifiedFiles.Count} modified), " +
                $"{numSkipped} skipped, {numNotFound} not found, {numJunk} junk, {numFailed} failed");
            PrintRenameSummary(renamedFiles.Count, modifiedFiles.Count);
        }

        private void PrintExtractionFailure(string archivePath, string errorMessage)
        {
            Console.Error.WriteLine($"Unable to extract {ReplaceControlChars(archivePath)}:");
            Console.Error.WriteLine(errorMessage);
            numFailed++;
        }

        public override void PrintPaths(bool includeAll)
        {
            foreach (var path in opt.StartPaths)
            {
                Reader.Traverse(path,
                    (dir) => 
                    {
                        if (MatchesFilters(opt.Filters, dir))
                        {
                            Console.WriteLine(ReplaceControlChars(dir));
                        }
                    },
                    (file) =>
                    {
                        if (MatchesFilters(opt.Filters, file))
                        {
                            Console.WriteLine(ReplaceControlChars(file));
                        }
                    },
                    (nonexistent) =>
                    {
                        if (nonexistent == "/")
                        {
                            PrintRootMissingError();
                        }
                        else if (PrintNotFoundMessage)
                        {
                            Console.Error.WriteLine($"Path {ReplaceControlChars(nonexistent)} " +
                                $"was not found");
                        }
                    });
            }
        }

        public override List<Tree.Directory> GetDirectoryTree()
        {
            var trees = opt.StartPaths
                .Select(GetDirectoryTree)
                .ToList();
            return trees;
        }

        private Tree.Directory GetDirectoryTree(string root)
        {
            if (Reader.EntryExists(root) == EntryType.NotFound)
            {
                return null;
            }

            var dir = new Tree.Directory();
            dir.Path = root;
            var entry = Reader.GetEntry(root);
            entry.IsDirectory = true;

            var content = Reader.GetDirectoryListing(root);
            foreach (var subdir in content.Subdirectories)
            {
                var type = Reader.EntryExists(subdir);
                if (type == EntryType.File)
                {
                    var subentry = Reader.GetEntry(root);
                    subentry.IsDirectory = true;
                }
                else if (type == EntryType.NotFound)
                {
                    continue;
                }
                dir.Subdirectories.Add(Path.GetFileName(subdir), GetDirectoryTree(subdir));
            }
            foreach (var file in content.Files)
            {
                // if (!junkEntries.ContainsKey(Reader.HashPath(file)))
                // {
                //     dir.Files.Add(file);
                // }
                dir.Files.Add(file);
            }
            return dir;
        }

        public override void Dispose()
        {
            Reader.Dispose();
            GC.SuppressFinalize(this);
        }
    }

    internal class RootMissingException : Exception { }

    internal class RootEmptyException : Exception { }
}
