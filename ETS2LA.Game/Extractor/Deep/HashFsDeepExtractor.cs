using Sprache;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data;
using TruckLib.HashFs;
using static Extractor.PathUtils;
using static Extractor.ConsoleUtils;
using static Extractor.TextUtils;

namespace Extractor.Deep
{
    /// <summary>
    /// A HashFS extractor which scans entry contents for paths before extraction to simplify
    /// the extraction of archives which lack dictory listings.
    /// </summary>
    public class HashFsDeepExtractor : HashFsExtractor
    {
        /// <summary>
        /// The directory to which files whose paths were not discovered
        /// will be written.
        /// </summary>
        private const string DumpDirectory = "_unknown";

        /// <summary>
        /// The directory to which decoy files will be written.
        /// </summary>
        private const string DecoyDirectory = "_decoy";

        /// <summary>
        /// The number of files whose paths were not discovered and therefore have been
        /// dumped to <see cref="DumpDirectory"/>.
        /// </summary>
        private int numDumped;

        private HashFsPathFinder finder;

        private bool hasSearchedForPaths;

        public HashFsDeepExtractor(string scsPath, Options opt) : base(scsPath, opt)
        {
            IdentifyJunkEntries();
        }

        /// <inheritdoc/>
        public override void Extract(string outputRoot)
        {
            Console.Error.WriteLine("Searching for paths ...");
            FindPaths();
            Extract(finder.FoundFiles.Order().ToArray(), outputRoot, false);
        }

        public void Extract(IList<string> foundFiles, string outputRoot, bool ignoreMissing)
        {
            bool startPathsSet = !opt.StartPaths.SequenceEqual(["/"]);

            substitutions = DeterminePathSubstitutions(foundFiles);

            // Extract regular files
            var filteredFoundFiles = foundFiles
                .Where(p =>
                {
                    if (startPathsSet && !opt.StartPaths.Any(p.StartsWith))
                        return false;
                    return MatchesFilters(opt.Filters, p);
                })
                .Order()
                .ToArray();
            ExtractFiles(filteredFoundFiles, outputRoot, ignoreMissing);

            // Extract decoy files
            var foundDecoyFiles = finder.FoundDecoyFiles
                .Where(p =>
                {
                    if (startPathsSet && !opt.StartPaths.Any(p.StartsWith))
                        return false;
                    return MatchesFilters(opt.Filters, p);
                })
                .Order()
                .ToArray();
            var decoyDestination = Path.Combine(outputRoot, DecoyDirectory);
            foreach (var decoyFile in foundDecoyFiles)
            {
                ExtractFile(decoyFile, decoyDestination);
            }

            // Extract files whose paths could not be recovered
            if (!(startPathsSet || opt.Filters?.Count > 0))
            {
                DumpUnrecovered(outputRoot, foundFiles.Concat(foundDecoyFiles));
            }

            WriteRenamedSummary(outputRoot);
            WriteModifiedSummary(outputRoot);
        }

        public (HashSet<string> FoundFiles, HashSet<string> ReferencedFiles) FindPaths()
        {
            if (!hasSearchedForPaths)
            {
                finder = new HashFsPathFinder(Reader, opt.AdditionalStartPaths, junkEntries);
                finder.Find();
                hasSearchedForPaths = true;
            }
            return (finder.FoundFiles, finder.ReferencedFiles);
        }

        public HashFsPathFinder FindPaths(AssetLoader multiModWrapper)
        {
            finder = new HashFsPathFinder(Reader, opt.AdditionalStartPaths, junkEntries, multiModWrapper);
            finder.Find();
            hasSearchedForPaths = true;
            return finder;
        }

        /// <summary>
        /// Extracts files whose paths were not discovered.
        /// </summary>
        /// <param name="destination">The root output directory.</param>
        /// <param name="foundFiles">All discovered paths.</param>
        private void DumpUnrecovered(string destination, IEnumerable<string> foundFiles)
        {
            var notRecovered = Reader.Entries.Values
                .Where(e => !e.IsDirectory)
                .Except(foundFiles.Select(f =>
                {
                    if (Reader.EntryExists(f) != EntryType.NotFound)
                    {
                        return Reader.GetEntry(f);
                    }
                    // junkEntries.TryGetValue(Reader.HashPath(f), out var retval);
                    return null;
                }));

            HashSet<ulong> visitedOffsets = [];

            var outputDir = Path.Combine(destination, DumpDirectory);

            foreach (var entry in notRecovered)
            {
                if (junkEntries.ContainsKey(entry.Hash) ||
                    maybeJunkEntries.ContainsKey(entry.Hash))
                {
                    continue;
                }

                var fileBuffer = Reader.Extract(entry, "")[0];
                var fileType = FileTypeHelper.Infer(fileBuffer);
                var extension = FileTypeHelper.FileTypeToExtension(fileType);
                var fileName = entry.Hash.ToString("x16") + extension;
                var outputPath = Path.Combine(outputDir, fileName);
                Console.WriteLine($"Dumping {fileName} ...");
                if (!Overwrite && File.Exists(outputPath))
                {
                    numSkipped++;
                }
                else
                {
                    ExtractToDisk(entry, $"/{DumpDirectory}/{fileName}", outputPath);
                    numDumped++;
                }
            }
        }

        public override void PrintPaths(bool includeAll)
        {
            var finder = new HashFsPathFinder(Reader);
            finder.Find();
            var paths = (includeAll 
                ? finder.FoundFiles.Union(finder.ReferencedFiles) 
                : finder.FoundFiles).Order();

            PrintPathsMatchingFilters(paths, opt.StartPaths, opt.Filters);
        }

        public override void PrintExtractionResult()
        {
            Console.WriteLine($"{numExtracted} extracted " +
                $"({renamedFiles.Count} renamed, {modifiedFiles.Count} modified, {numDumped} dumped), " +
                $"{numSkipped} skipped, {numJunk} junk, {numFailed} failed");
            PrintRenameSummary(renamedFiles.Count, modifiedFiles.Count);
        }

        public override List<Tree.Directory> GetDirectoryTree()
        {
            var finder = new HashFsPathFinder(Reader);
            finder.Find();

            var trees = opt.StartPaths
                .Select(startPath => PathListToTree(startPath, finder.FoundFiles))
                .ToList();
            return trees;
        }
    }
}
