using Extractor.Deep;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using TruckLib;
using static Extractor.ConsoleUtils;
using static Extractor.PathUtils;
using static Extractor.TextUtils;

[assembly: InternalsVisibleTo("Extractor.Tests")]
namespace Extractor.Zip
{
    /// <summary>
    /// A ZIP extractor which can handle archives with deliberately corrupted local file headers.
    /// </summary>
    public class ZipExtractor : Extractor
    {
        /// <summary>
        /// The underlying ZIP reader.
        /// </summary>
        public ZipReader Reader { get; init; }

        public override IFileSystem FileSystem => Reader;

        /// <summary>
        /// Paths which will need to be renamed.
        /// </summary>
        private Dictionary<string, string> substitutions;

        /// <summary>
        /// The number of files which have been extracted successfully.
        /// </summary>
        private int numExtracted;

        /// <summary>
        /// The number of files which have been skipped because the output path
        /// already exists and <see cref="Options.SkipIfExists"/> is set.
        /// </summary>
        private int numSkipped;

        /// <summary>
        /// The number of files which failed to extract.
        /// </summary>
        private int numFailed;

        public ZipExtractor(string scsPath, Options opt) : base(scsPath, opt)
        {
            Reader = ZipReader.Open(scsPath);
            PrintContentSummary();
        }

        /// <inheritdoc/>
        public override void Extract(string outputRoot)
        {
            var entriesToExtract = GetEntriesToExtract(Reader, opt.StartPaths, opt.Filters);
            substitutions = DeterminePathSubstitutions(entriesToExtract);

            var scsName = Path.GetFileName(ScsPath);
            foreach (var entry in entriesToExtract)
            {
                try
                {
                    if (!opt.Quiet)
                    {
                        PrintExtractionMessage(entry.FileName, scsName);
                    }
                    if (!substitutions.TryGetValue(entry.FileName, out string fileName))
                    {
                        fileName = entry.FileName;
                    }
                    ExtractEntry(entry, outputRoot, fileName);
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Unable to extract {ReplaceControlChars(entry.FileName)}:");
                    Console.Error.WriteLine(ex.Message);
                    numFailed++;
                }
            }

            WriteRenamedSummary(outputRoot);
            WriteModifiedSummary(outputRoot);
        }

        internal static Dictionary<string, string> DeterminePathSubstitutions(
            List<CentralDirectoryFileHeader> entriesToExtract)
        {
            Dictionary<string, string> substitutions = [];
            foreach (var entry in entriesToExtract)
            {
                var sanitized = SanitizePath(entry.FileName);
                if (sanitized != entry.FileName)
                {
                    substitutions.Add(entry.FileName, sanitized);
                    substitutions.Add("/" + entry.FileName, "/" + sanitized);
                }
            }
            return substitutions;
        }

        internal static List<CentralDirectoryFileHeader> GetEntriesToExtract(
            ZipReader zip, IList<string> startPaths, IList<Regex> filters)
        {
            bool startPathsUsed = !startPaths.SequenceEqual(["/"]);
            if (startPathsUsed)
                RemoveInitialSlash(startPaths);

            List<CentralDirectoryFileHeader> entriesToExtract = [];
            foreach (var (_, entry) in zip.Entries)
            {
                // Directory metadata; ignore
                if (entry.FileName.EndsWith('/'))
                    continue;

                if (startPathsUsed && !startPaths.Any(entry.FileName.StartsWith))
                    continue;

                if (!MatchesFilters(filters, entry.FileName))
                    continue;

                entriesToExtract.Add(entry);
            }

            return entriesToExtract;
        }

        /// <summary>
        /// Extracts the given file from the archive to the destination directory.
        /// </summary>
        /// <param name="entry">The file to extract.</param>
        /// <param name="destination">The directory to extract the file to.</param>
        private void ExtractEntry(CentralDirectoryFileHeader entry, string outputRoot, string fileName)
        {
            var outputPath = Path.Combine(outputRoot, fileName);
            if (File.Exists(outputPath) && !Overwrite)
            {
                numSkipped++;
                return;
            }

            if (fileName != entry.FileName)
            {
                renamedFiles.Add((entry.FileName, fileName));
            }

            using var ms = new MemoryStream();
            Reader.GetEntry(entry, ms);
            var buffer = ms.ToArray();
            var wasModified = PerformSubstitutionIfRequired(entry.FileName, ref buffer, substitutions);

            if (!opt.DryRun)
            {
                var outputDir = Path.GetDirectoryName(outputPath);
                if (outputDir != null)
                {
                    Directory.CreateDirectory(outputDir);
                }
                File.WriteAllBytes(outputPath, buffer);
            }

            numExtracted++;
            if (wasModified)
                modifiedFiles.Add(entry.FileName);
        }

        public override void PrintContentSummary()
        {
            Console.Error.WriteLine($"Opened {Path.GetFileName(ScsPath)}: " +
                $"ZIP archive; {Reader.Entries.Count} entries");
        }

        public override void PrintExtractionResult()
        {
            Console.Error.WriteLine($"{numExtracted} extracted " +
                $"({renamedFiles.Count} renamed, {modifiedFiles.Count} modified), " +
                $"{numSkipped} skipped, {numFailed} failed");
            PrintRenameSummary(renamedFiles.Count, modifiedFiles.Count);
        }

        public override void PrintPaths(bool includeAll)
        {
            if (includeAll)
            {
                Console.Error.WriteLine("Searching for paths ...");
                var finder = new ZipPathFinder(Reader);
                finder.Find();
                var all = finder.ReferencedFiles.Union(Reader.Entries.Keys.Select(p => '/' + p)).Order();
                PrintPathsMatchingFilters(all, opt.StartPaths, opt.Filters);
            }
            else
            {
                PrintPathsMatchingFilters(
                    Reader.Entries.Select(x => '/' + x.Value.FileName).Order(), 
                    opt.StartPaths, opt.Filters);
            }
        }

        public override List<Tree.Directory> GetDirectoryTree()
        {
            RemoveInitialSlash(opt.StartPaths);

            var paths = Reader.Entries
                .Where(e => e.Value.UncompressedSize > 0) // filter out directory metadata
                .Select(e => e.Value.FileName);
            var trees = opt.StartPaths
                .Select(startPath => PathListToTree(startPath, paths))
                .ToList();
            return trees;
        }

        private static void RemoveInitialSlash(IList<string> startPaths)
        {
            for (int i = 0; i < startPaths.Count; i++)
            { 
                startPaths[i] = PathUtils.RemoveInitialSlash(startPaths[i]);
            }
        }

        public override void Dispose()
        {
            Reader?.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}
