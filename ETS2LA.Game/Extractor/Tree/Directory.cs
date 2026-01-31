using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Extractor.Tree
{
    public class Directory
    {
        public string Path { get; set; }

        public Dictionary<string, Directory> Subdirectories { get; set; } = [];

        public List<string> Files { get; set; } = [];
    }
}
