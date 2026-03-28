using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection.PortableExecutable;
using System.Text;
using System.Threading.Tasks;
using TruckLib.HashFs;

namespace Extractor
{
    internal static class Extensions
    {
        public static void Traverse(this IHashFsReader reader, string path,
            Action<string> onVisitDirectory, Action<string> onVisitFile, 
            Action<string> onVisitNonexistent)
        {
            reader.Traverse(path,
                (path) => { onVisitDirectory(path); return true; },
                onVisitFile, onVisitNonexistent);
        }

        public static void Traverse(this IHashFsReader reader, string path, 
            Func<string, bool> onVisitDirectory, Action<string> onVisitFile, 
            Action<string> onVisitNonexistent)
        {
            switch (reader.EntryExists(path))
            {
                case EntryType.Directory:
                    var keepGoing = onVisitDirectory(path);

                    if (!keepGoing)
                        return;

                    var content = reader.GetDirectoryListing(path);
                    foreach (var dir in content.Subdirectories)
                    {
                        // Some dir entries don't have the directory flag set,
                        // so this needs to be fixed here
                        var type = reader.EntryExists(dir);
                        if (type == EntryType.File)
                        {
                            var entry = reader.GetEntry(dir);
                            entry.IsDirectory = true;
                        }
                        reader.Traverse(dir, onVisitDirectory, onVisitFile, onVisitNonexistent);
                    }
                    foreach (var file in content.Files)
                    {
                        reader.Traverse(file, onVisitDirectory, onVisitFile, onVisitNonexistent);
                    }
                    break;
                case EntryType.File:
                    onVisitFile(path);
                    break;
                case EntryType.NotFound:
                    onVisitNonexistent(path);
                    break;
            }
        }
    }
}
