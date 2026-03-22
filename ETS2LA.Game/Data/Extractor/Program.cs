using Extractor.Deep;
using Extractor.Zip;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using TruckLib.HashFs;
using static Extractor.PathUtils;

namespace Extractor
{
    class Program
    {
        private const string Version = "2025-12-11";
        private static bool launchedByExplorer = false;
        private static Options opt;

        public static int Main(string[] args)
        {
            if (OperatingSystem.IsWindows())
            {
                // Detect whether the extractor was launched by Explorer to pause at the end
                // so that people who just want to drag and drop a file onto it can read the
                // error message if one occurs.
                // This works for both conhost and Windows Terminal.
                launchedByExplorer = !Debugger.IsAttached &&
                    Path.TrimEndingDirectorySeparator(Path.GetDirectoryName(Console.Title)) ==
                    Path.TrimEndingDirectorySeparator(AppContext.BaseDirectory);
            }

            Console.OutputEncoding = Encoding.UTF8;

            opt = new Options();
            opt.Parse(args);

            if (opt.PrintHelp || args.Length == 0)
            {
                PrintUsage();
                return (int)ExitCode.Success;
            }

            ValidateOptions();

            var exitCode = Run();
            PauseIfNecessary();
            return (int)exitCode;
        }

        private static void PrintUsage()
        {
            Console.WriteLine($"Extractor {Version}\n");
            Console.WriteLine("Usage:\n  extractor path... [options]\n");
            Console.WriteLine("Options:");
            opt.OptionSet.WriteOptionDescriptions(Console.Out);
            PauseIfNecessary();
        }

        private static void ValidateOptions()
        {
            if (opt.InputPaths is null || opt.InputPaths.Count == 0)
            {
                Console.Error.WriteLine("No input paths specified.");
                PauseIfNecessary();
                Environment.Exit((int)ExitCode.NoInput);
            }

            Dictionary<string, bool> modeSwitches = new()
            {
                { "list", opt.ListPaths },
                { "list-entries", opt.ListEntries },
                { "raw", opt.UseRawExtractor },
                { "tree", opt.PrintTree },
            };
            var combinations = modeSwitches.SelectMany(
                (x, i) => modeSwitches.Skip(i + 1), 
                (x, y) => (X: x, Y: y)
            );
            foreach (var (X, Y) in combinations)
            {
                if (X.Value && Y.Value)
                {
                    Console.Error.WriteLine($"--{X.Key} and --{Y.Key} cannot be combined.");
                    Environment.Exit((int)ExitCode.IncompatibleOptions);
                }
            }
        }

        private static ExitCode Run()
        {
            var scsPaths = GetScsPathsFromArgs();
            if (scsPaths.Length == 0)
            {
                Console.Error.WriteLine("No .scs files were found.");
                return ExitCode.NoInput;
            }

            if (opt.UseDeepExtractor && scsPaths.Length > 1)
            {
                return DoMultiDeepExtraction(scsPaths);
            }

            List<ExtractionResult> results = new(scsPaths.Length);
            foreach (var scsPath in scsPaths)
            {
                Extractor extractor;
                try
                {
                    extractor = CreateExtractor(scsPath);
                }
                catch (FileNotFoundException)
                {
                    results.Add(ExtractionResult.NotFound);
                    continue;
                }
                catch (InvalidDataException)
                {
                    results.Add(ExtractionResult.FailedToOpen);
                    continue;
                }
                catch (Exception)
                {
                    results.Add(ExtractionResult.FailedToOpen);
                    continue;
                }

                if (opt.ListEntries)
                {
                    if (extractor is HashFsExtractor hEx)
                    {
                        ListEntries(hEx);
                        results.Add(ExtractionResult.Success);
                    }
                    else
                    {
                        Console.Error.WriteLine("--list-entries can only be used with HashFS archives.");
                        results.Add(ExtractionResult.IncompatibleOptions);
                    }
                }
                else if (opt.ListPaths)
                {
                    extractor.PrintPaths(opt.ListAll);
                    results.Add(ExtractionResult.Success);
                }
                else if (opt.PrintTree)
                {
                    var trees = extractor.GetDirectoryTree();
                    var scsName = Path.GetFileName(extractor.ScsPath);
                    Tree.TreePrinter.Print(trees, scsName);
                    results.Add(ExtractionResult.Success);
                }
                else
                {
                    try
                    {
                        extractor.Extract(GetDestination(scsPath));
                        results.Add(ExtractionResult.Success);
                    }
                    catch (RootMissingException)
                    {
                        ConsoleUtils.PrintRootMissingError();
                        results.Add(ExtractionResult.RootMissing);
                    }
                    catch (RootEmptyException)
                    {
                        ConsoleUtils.PrintRootEmptyError();
                        results.Add(ExtractionResult.RootEmpty);
                    }
                    extractor.PrintExtractionResult();
                }
            }

            return DetermineExitCode(results);
        }

        private static ExitCode DetermineExitCode(List<ExtractionResult> results)
        {
            if (results.All(x => x == ExtractionResult.Success))
            {
                return ExitCode.Success;
            }
            if (results.Any(x => x == ExtractionResult.Success))
            {
                return ExitCode.PartialSuccess;
            }
            else if (results.All(x => x == ExtractionResult.NotFound))
            {
                return ExitCode.NotFound;
            }
            else if (results.All(x => x is ExtractionResult.RootEmpty
                or ExtractionResult.RootMissing))
            {
                return ExitCode.NoRoot;
            }
            else if (results.All(x => x == ExtractionResult.FailedToOpen))
            {
                return ExitCode.FailedToOpen;
            }
            else if (results.All(x => x == ExtractionResult.IncompatibleOptions))
            {
                return ExitCode.IncompatibleOptions;
            }
            return ExitCode.AllFailed;
        }

        private static string GetDestination(string scsPath)
        {
            if (opt.Separate)
            {
                var scsName = Path.GetFileNameWithoutExtension(scsPath);
                var destination = Path.Combine(opt.Destination, scsName);
                return destination;
            }
            return opt.Destination;
        }

        private static Extractor CreateExtractor(string scsPath)
        {
            if (!File.Exists(scsPath))
            {
                Console.Error.WriteLine($"{scsPath} is not a file or does not exist.");
                throw new FileNotFoundException();
            }

            Extractor extractor;
            try
            {
                // Check if the file begins with "SCS#", the magic bytes of a HashFS file.
                // Anything else is assumed to be a ZIP file because simply checking for "PK"
                // would miss ZIP files with invalid local file headers.
                char[] magic;
                using (var fs = File.OpenRead(scsPath))
                using (var r = new BinaryReader(fs, Encoding.ASCII))
                {
                    magic = r.ReadChars(4);
                }

                if (magic.SequenceEqual(['S', 'C', 'S', '#']))
                {
                    extractor = CreateHashFsExtractor(scsPath);
                }
                else
                {
                    extractor = new ZipExtractor(scsPath, opt);
                }
            }
            catch (InvalidDataException)
            {
                Console.Error.WriteLine($"Unable to open {scsPath}: Not a HashFS or ZIP archive");
                throw;
            }
            catch (Exception ex)
            {
                // In case this is actually a ZIP file that has been modified
                // to start with "SCS#", we'll try to create a ZIP extractor first.
                // If that also fails, print the original HashFS error message.
                try
                {
                    extractor = new ZipExtractor(scsPath, opt);
                }
                catch
                {
                    Console.Error.WriteLine($"Unable to open {scsPath}: {ex.Message}");
                    throw;
                }
            }
            return extractor;
        }

        private static Extractor CreateHashFsExtractor(string scsPath)
        {
            if (opt.UseRawExtractor)
                return new HashFsRawExtractor(scsPath, opt);
            else if (opt.UseDeepExtractor)
                return new HashFsDeepExtractor(scsPath, opt);
            else
                return new HashFsExtractor(scsPath, opt);
        }

        private static ExitCode DoMultiDeepExtraction(string[] scsPaths)
        {
            // If you're reading this ... maybe don't.

            List<ExtractionResult> results = new(scsPaths.Length);
            List<Extractor> extractors = new(scsPaths.Length);
            foreach (var scsPath in scsPaths)
            {
                try
                {
                    var extractor = CreateExtractor(scsPath);
                    extractors.Add(extractor);
                }
                catch (FileNotFoundException)
                {
                    results.Add(ExtractionResult.NotFound);
                    continue;
                }
                catch (InvalidDataException)
                {
                    results.Add(ExtractionResult.FailedToOpen);
                    continue;
                }
                catch (Exception)
                {
                    results.Add(ExtractionResult.FailedToOpen);
                    continue;
                }
            }

            if (extractors.Count == 0)
                return DetermineExitCode(results);

            var multiModWrapper = new AssetLoader(extractors.Select(x => x.FileSystem).ToArray());

            HashSet<string> everything = [];
            HashSet<string> consumedSuis = [];
            foreach (var extractor in extractors)
            {
                Console.Error.WriteLine($"Searching for paths in {Path.GetFileName(extractor.ScsPath)} ...");
                if (extractor is HashFsDeepExtractor hashFs)
                {
                    var finder = hashFs.FindPaths(multiModWrapper);
                    everything.UnionWith(finder.FoundFiles);
                    everything.UnionWith(finder.ReferencedFiles);
                    consumedSuis.UnionWith(finder.ConsumedSuis);
                }
                else if (extractor is ZipExtractor zip)
                {
                    var finder = new ZipPathFinder(zip.Reader);
                    finder.Find(multiModWrapper);
                    var paths = finder.ReferencedFiles
                        .Union(zip.Reader.Entries.Keys.Select(p => '/' + p));
                    everything.UnionWith(paths);
                    consumedSuis.UnionWith(finder.ConsumedSuis);
                }
                else
                {
                    throw new ArgumentException("Unhandled extractor type");
                }
            }

            SiiPathFinder.FindPathsInUnconsumedSuis(consumedSuis, everything, multiModWrapper);

            foreach (var extractor in extractors)
            {
                var existing = everything.Where(extractor.FileSystem.FileExists);

                if (opt.ListPaths)
                {
                    ConsoleUtils.PrintPathsMatchingFilters(existing.Order(), opt.StartPaths, opt.Filters);
                }
                else if (opt.PrintTree)
                {
                    var trees = opt.StartPaths
                        .Select(startPath => PathListToTree(startPath, existing))
                        .ToList();
                    Tree.TreePrinter.Print(trees, Path.GetFileName(extractor.ScsPath));
                }
                else
                {
                    if (extractor is HashFsDeepExtractor deep)
                    {
                        deep.Extract(existing.ToArray(), GetDestination(extractor.ScsPath), true);
                    }
                    else
                    {
                        extractor.Extract(GetDestination(extractor.ScsPath));
                    }
                }

                results.Add(ExtractionResult.Success);
            }

            if (!opt.ListPaths && !opt.PrintTree)
            {
                foreach (var extractor in extractors)
                {
                    Console.Write($"{Path.GetFileName(extractor.ScsPath)}: ");
                    extractor.PrintExtractionResult();
                }
            }

            return DetermineExitCode(results);
        }

        private static void ListEntries(HashFsExtractor hExt)
        {
            Console.WriteLine($"  {"Offset",-10}  {"Hash",-16}  {"Cmp. Size",-10}  {"Uncmp.Size",-10}");
            foreach (var (_, entry) in hExt.Reader.Entries)
            {
                Console.WriteLine($"{(entry.IsDirectory ? "*" : " ")} " +
                    $"{entry.Offset,10}  {entry.Hash,16:x}  {entry.CompressedSize,10}  {entry.Size,10}");
            }
        }

        private static string[] GetScsPathsFromArgs()
        {
            List<string> scsPaths;
            if (opt.ExtractAllInDir)
            {
                scsPaths = [];
                foreach (var inputPath in opt.InputPaths)
                {
                    if (!Directory.Exists(inputPath))
                    {
                        Console.Error.WriteLine($"{inputPath} is not a directory or does not exist.");
                        continue;
                    }
                    scsPaths.AddRange(GetAllScsFiles(inputPath));
                }
            }
            else
            {
                scsPaths = opt.InputPaths;
            }
            return scsPaths.Distinct().ToArray();
        }

        private static void PauseIfNecessary()
        {
            if (launchedByExplorer)
            {
                Console.WriteLine("Press any key to continue ...");
                Console.Read();
            }
        }
    }
}
