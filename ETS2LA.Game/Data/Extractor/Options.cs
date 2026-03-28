using Mono.Options;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using static Extractor.PathUtils;
using Extractor.Deep;
using Microsoft.Extensions.FileSystemGlobbing;

namespace Extractor
{
    public class Options
    {
        public OptionSet OptionSet { get; init; }

        /// <summary>
        /// User-supplied additional start paths for the path finder.
        /// </summary>
        public IList<string> AdditionalStartPaths { get; set; }

        /// <summary>
        /// The output directory to which extracted files are written.
        /// </summary>
        public string Destination { get; set; } = "./extracted";

        /// <summary>
        /// Don't write anything to disk.
        /// </summary>
        public bool DryRun { get; set; } = false;

        /// <summary>
        /// If true, the input path(s) are expected to be directories,
        /// and all .scs files in these directories are extracted.
        /// </summary>
        public bool ExtractAllInDir { get; set; } = false;

        /// <summary>
        /// Filters to test paths against. Files whose paths which don't match
        /// are not extracted.
        /// </summary>
        public IList<Regex> Filters { get; set; } = null;

        /// <summary>
        /// Whether the entry table should be read from the end of the file
        /// regardless of where the header says it is located.
        /// </summary>
        /// <remarks>Solves #1.</remarks>
        public bool ForceEntryTableAtEnd { get; set; } = false;

        /// <summary>
        /// The files or directories to extract.
        /// </summary>
        public List<string> InputPaths { get; set; }

        /// <summary>
        /// Instead of extracting, list all paths contained in the archive
        /// and all paths referenced by files within the archive.
        /// </summary>
        public bool ListAll { get; set; } = false;

        /// <summary>
        /// Instead of extracting, print the entries of the archive as a table.
        /// </summary>
        public bool ListEntries { get; set; } = false;

        /// <summary>
        /// Instead of extracting, list all paths contained in the archive.
        /// </summary>
        public bool ListPaths { get; set; } = false;

        /// <summary>
        /// Instead of extracting, print the program's version and usage information.
        /// </summary>
        public bool PrintHelp { get; set; } = false;

        /// <summary>
        /// Instead of extracting, print the directory tree of the archive.
        /// </summary>
        public bool PrintTree { get; set; } = false;

        /// <summary>
        /// Quiet mode, doesn't print on every extracted file.
        /// </summary>
        public bool Quiet { get; set; } = false;

        /// <summary>
        /// If not null, the salt to use for hashing paths instead of the one
        /// specified in the archive header.
        /// </summary>
        public ushort? Salt { get; set; } = null;

        /// <summary>
        /// Whether all archives should be extracted to a separate directory.
        /// </summary>
        public bool Separate { get; set; } = false;

        /// <summary>
        /// If true, existing files in the output directory are not overwritten.
        /// </summary>
        public bool SkipIfExists { get; set; } = false;

        /// <summary>
        /// Start paths for regular HashFS extraction, allowing for partial extraction
        /// or extracting known paths in an archive without directory listings.
        /// </summary>
        public IList<string> StartPaths { get; set; } = ["/"];

        /// <summary>
        /// Whether the archive should be extracted with <see cref="HashFsDeepExtractor"/>.
        /// </summary>
        public bool UseDeepExtractor { get; set; } = false;

        /// <summary>
        /// Whether the archive should be extracted with <see cref="HashFsRawExtractor"/>.
        /// </summary>
        public bool UseRawExtractor { get; set; } = false;

        public Options()
        {
            OptionSet = new OptionSet()
            {
                 { "additional=",
                    "[HashFS] When using --deep, specifies additional start paths to search. " +
                    "Expects a text file containing paths to extract, separated by line breaks.",
                    x => { AdditionalStartPaths = LoadPathsFromFile(x); } },
                { "a|all",
                    "Extract all .scs archives in the specified directory.",
                    x => { ExtractAllInDir = true; } },
                { "D|deep",
                    $"[HashFS] Scans contained files for paths before extracting. Use this option " +
                    $"to extract archives without a top level directory listing.",
                    x => { UseDeepExtractor = true; } },
                { "d=|dest=",
                    $"The output directory.\nDefault: {Destination}",
                    x => { Destination = x; } },
                 { "dry-run",
                    $"Don't write anything to disk.",
                    x => { DryRun = true; } },
                { "f=|filter=",
                    $"Limits extraction to files whose paths match one or more of the specified filter patterns. " +
                    $"See the readme for details.",
                    x => { Filters = ParseFilters(x); } },
                { "list",
                    "Lists paths contained in the archive.",
                    x => { ListPaths = true; } },
                { "list-all",
                    "Lists all paths referenced by files within the archive, " +
                    "even if they are not contained in it. Implicitly activates --deep.",
                    x => { ListPaths = true; ListAll = true; UseDeepExtractor = true;  } },
                { "list-entries",
                    "[HashFS] Lists entries contained in the archive.",
                    x => { ListEntries = true; } },
                { "p=|partial=",
                    "Limits extraction to the comma-separated list of files and/or " +
                    "directories specified, e.g.:\n" +
                    "-p=/locale\n" +
                    "-p=/def,/map\n" +
                    "-p=/def/world/road.sii",
                    x => { StartPaths = x.Split(","); } },
                 { "P=|paths=",
                    "Same as --partial, but expects a text file containing paths to extract, " +
                    "separated by line breaks.",
                    x => { StartPaths = LoadPathsFromFile(x); } },
                { "q|quiet",
                    "Don't print paths of extracted files.",
                    x => { Quiet = true; } },
                { "r|raw",
                    "[HashFS] Dumps the contained files with their hashed " +
                    "filenames rather than traversing the archive's directory tree.",
                    x => { UseRawExtractor = true; } },
                { "salt=",
                    "[HashFS] Overrides the salt specified in the archive header with the given one.",
                    x => { Salt = ushort.Parse(x); } },
                { "S|separate",
                    "When extracting multiple archives, extract each archive to a separate directory.",
                    x => { Separate = true; } },
                { "s|skip-existing",
                    "Don't overwrite existing files.",
                    x => { SkipIfExists = true; } },
                { "table-at-end",
                    "[HashFS v1] Ignores what the archive header says and reads " +
                    "the entry table from the end of the file.",
                    x => { ForceEntryTableAtEnd = true; } },
                { "tree",
                    "Prints the archive's directory tree.",
                    x => { PrintTree = true; } },
                { "?|h|help",
                    $"Prints this message and exits.",
                    x => { PrintHelp = true; } },
            };
        }

        public void Parse(string[] args)
        {
            var inputPaths = OptionSet.Parse(args);
            ProcessInputPaths(inputPaths);
        }

        private void ProcessInputPaths(List<string> inputPaths)
        {
            if (inputPaths.Count == 0 && ExtractAllInDir)
            {
                InputPaths = ["."];
            }
            else if (OperatingSystem.IsWindows() && inputPaths.Any(p => p.Contains('*')))
            {
                var matcher = new Matcher();
                matcher.AddIncludePatterns(inputPaths);
                InputPaths = matcher.GetResultsInFullPath(Environment.CurrentDirectory).ToList();
            }
            else
            {
                InputPaths = inputPaths;
            }
        }

        private static List<Regex> ParseFilters(string arg)
        {
            var patterns = arg.Split(",", StringSplitOptions.RemoveEmptyEntries);

            if (patterns.Length == 0)
                return null;

            List<Regex> filters = new(patterns.Length);
            foreach (var pattern in patterns)
            {
                var regex = IsRegexPattern(pattern) 
                    ? new Regex(pattern[2..^1]) 
                    : TextUtils.WildcardStringToRegex(pattern);
                filters.Add(regex);
            }
            return filters;

            static bool IsRegexPattern(string pattern) => 
                pattern.Length >= 3 && pattern.StartsWith("r/") && pattern.EndsWith('/');
        }

        private static List<string> LoadPathsFromFile(string file)
        {
            if (!File.Exists(file))
            {
                Console.Error.WriteLine($"File {file} does not exist.");
                Environment.Exit((int)ExitCode.PathFileNotFound);
            }

            List<string> paths = [];
            using var reader = new StreamReader(file);
            while (!reader.EndOfStream)
            {
                var path = reader.ReadLine();

                if (string.IsNullOrEmpty(path))
                    continue;

                EnsureHasInitialSlash(ref path);

                paths.Add(path);
            }

            return paths;
        }
    }
}
