using Extractor.Zip;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TruckLib;
using TruckLib.HashFs;

namespace Extractor.Deep
{
    internal class ZipPathFinder
    {
        /// <summary>
        /// File paths that are referenced by files in this archive.
        /// </summary>
        public HashSet<string> ReferencedFiles { get; init; } = [];

        /// <summary>
        /// The ZIP archive.
        /// </summary>
        private readonly ZipReader reader;

        public HashSet<string> ConsumedSuis { get; init; } = [];

        public ZipPathFinder(ZipReader reader) 
        {
            this.reader = reader;
        }

        /// <summary>
        /// Scans the archive for path references and writes the results to <see cref="ReferencedFiles"/>.
        /// </summary>
        public void Find(AssetLoader multiModWrapper = null)
        {
            IFileSystem fsToUse = multiModWrapper is null ? reader : multiModWrapper;
            var fpf = new FilePathFinder(fsToUse, [], ReferencedFiles, [], ConsumedSuis);

            foreach (var (_, entry) in reader.Entries)
            {
                // Directory metadata; ignore
                if (entry.FileName.EndsWith('/'))
                {
                    continue;
                }

                var fileType = FileTypeHelper.PathToFileType(entry.FileName);
                if (FilePathFinder.IgnorableFileTypes.Contains(fileType))
                {
                    continue;
                }

                try
                {
                    using var ms = new MemoryStream();
                    reader.GetEntry(entry, ms);
                    var buffer = ms.ToArray();

                    var path = '/' + entry.FileName;
                    var paths = fpf.FindPathsInFile(buffer, path, fileType);
                    ReferencedFiles.UnionWith(paths);
                }
                catch (Exception)
                {
                    Debugger.Break();
                }
            }
        }

    }
}
