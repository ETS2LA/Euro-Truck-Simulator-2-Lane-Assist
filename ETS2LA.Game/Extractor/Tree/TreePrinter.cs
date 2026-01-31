using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TruckLib.HashFs;
using static Extractor.PathUtils;

namespace Extractor.Tree
{
    internal static class TreePrinter
    {
        public static void Print(List<Directory> roots, string scsName)
        {
            PrintWithColor(scsName, ConsoleColor.White);
            foreach (Directory root in roots)
            {
                if (root is null)
                    continue;

                var indentLevel = root.Path.Count(c => c == '/');
                if (root.Path != "/")
                {
                    WriteIndent(indentLevel);
                    PrintDirectoryPath(root.Path);
                    indentLevel++;
                }
                Print(root, indentLevel);
            }
        }

        public static void Print(Directory root, int indent = 0)
        {
            var parts = root.Path.Split("/", StringSplitOptions.RemoveEmptyEntries);

            var sortedSubdirs = root.Subdirectories.OrderBy(s => s.Key).ToArray();
            for (int i = 0; i < sortedSubdirs.Length; i++)
            {
                var (_, subdir) = sortedSubdirs[i];
                WriteIndent(indent);
                PrintDirectoryPath(subdir.Path);
                Print(subdir, indent + 1);
            }

            var sortedFiles = root.Files.Order().ToArray();
            for (int i = 0; i < sortedFiles.Length; i++)
            {
                var file = sortedFiles[i];
                WriteIndent(indent, i == root.Files.Count - 1);
                PrintFilePath(file);
            }
        }

        private static void PrintFilePath(string path)
        {
            var fileName = path[(path.LastIndexOf('/') + 1)..];
            Console.WriteLine(ReplaceControlChars(fileName));
        }

        private static void PrintDirectoryPath(string path)
        {
            RemoveTrailingSlash(ref path);
            var name = path[(path.LastIndexOf('/') + 1)..];
            PrintDirectoryName(name);
        }

        private static void PrintDirectoryName(string name)
        {
            PrintWithColor($"[{ReplaceControlChars(name)}]", ConsoleColor.Yellow);
        }

        private static void PrintWithColor(string str, ConsoleColor color)
        {
            var prevConsoleColor = Console.ForegroundColor;
            Console.ForegroundColor = color;
            Console.WriteLine(str);
            Console.ForegroundColor = prevConsoleColor;
        }

        private static void WriteIndent(int level, bool isLastLine = false)
        {
            for (int i = 0; i < level; i++)
            {
                if (i == level - 1)
                {
                    if (isLastLine)
                    {
                        Console.Write(" └╴");
                    }
                    else
                    {
                        Console.Write(" ├╴");
                    }
                }
                else
                {
                    Console.Write(" │ ");
                }
            }
        }
    }
}
