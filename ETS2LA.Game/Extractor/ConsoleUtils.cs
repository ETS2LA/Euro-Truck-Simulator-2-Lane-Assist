using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using static Extractor.PathUtils;

namespace Extractor
{
    internal class ConsoleUtils
    {
        public static void PrintRenameSummary(int renamed, int modified)
        {
            if (renamed > 0)
            {
                Console.WriteLine($"WARN: {renamed} {(renamed == 1 ? "file" : "files")} had to be renamed and " +
                    $"{modified} file{(renamed == 1 ? " was" : "s were")} modified accordingly.");
            }
        }

        public static void PrintExtractionMessage(string path, string scsName)
        {
            Console.WriteLine($"Extracting {ReplaceControlChars(Combine(scsName, path))} ...");
        }

        public static void PrintRootMissingError()
        {
            Console.Error.WriteLine("Top level directory is missing; " +
                "use --deep to scan contents for paths before extraction " +
                "or --partial to extract known paths");
        }

        public static void PrintRootEmptyError()
        {
            Console.Error.WriteLine("Top level directory is empty; " +
                "use --deep to scan contents for paths before extraction " +
                "or --partial to extract known paths");
        }

        public static void PrintPathsMatchingFilters(IEnumerable<string> paths, IList<string> startPaths, 
            IList<Regex> filters)
        {
            bool startPathsSet = !startPaths.SequenceEqual(["/"]);
            foreach (var path in paths)
            {
                if (startPathsSet && !startPaths.Any(path.StartsWith))
                    continue;

                if (!TextUtils.MatchesFilters(filters, path))
                    continue;

                Console.WriteLine(ReplaceControlChars(path));
            }
        }
    }
}
