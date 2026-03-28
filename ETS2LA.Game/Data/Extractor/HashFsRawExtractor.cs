using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Extractor
{
    public class HashFsRawExtractor : HashFsExtractor
    {
        public HashFsRawExtractor(string scsPath, Options opt) : base(scsPath, opt)
        {
        }

        public override void Extract(string destination)
        {
            var scsName = Path.GetFileName(ScsPath);
            Console.Out.WriteLine($"Extracting {scsName} ...");

            var outputDir = Path.Combine(destination, scsName);
            if (!opt.DryRun)
            {
                Directory.CreateDirectory(outputDir);
            }

            foreach (var (key, entry) in Reader.Entries)
            {
                // subdirectory listings are useless because the file names are relative
                if (entry.IsDirectory) continue;

                var outputPath = Path.Combine(outputDir, key.ToString("x"));
                ExtractToDisk(entry, key.ToString("x"), outputPath);
            }
        }

        public override void PrintExtractionResult()
        {
            Console.WriteLine($"{numExtracted} extracted, {numSkipped} skipped, {numJunk} junk, {numFailed} failed");
        }

        public override void PrintPaths(bool includeAll)
        {
            Console.WriteLine("--list and --raw cannot be combined.");
        }
    }
}
