namespace ETS2LA.Game.Extractor.FileSystem
{
    /// <summary>
    /// Represents a directory in the filesystem
    /// <para>Is unaware of it's own location/path</para>
    /// </summary>
    public class UberDirectory
    {
        /// <summary>
        /// All the entries (hash or zip) for the current directory
        /// </summary>
        private readonly List<Entry> _entries = new List<Entry>();
        /// <summary>
        /// Names of subdirectories in the current directory, name does NOT include it's absolute path
        /// </summary>
        private readonly List<string> _subDirectoryNames = new List<string>();
        /// <summary>
        /// Names of subfiles in the current directory, name does NOT include it's absolute path
        /// </summary>
        private readonly List<string> _subFilesNames = new List<string>();

        public UberDirectory() { }

        /// <summary>
        /// Adds a new <see cref="Entry"/> for the current directory
        /// </summary>
        public void AddNewEntry(Entry entry)
        {
            _entries.Add(entry);
        }

        /// <summary>
        /// Adds the name of a subdirectory to the current directory
        /// </summary>
        /// <param name="name">Name of the directory. Just the name, not the path</param>
        public void AddSubDirName(string name)
        {
            _subDirectoryNames.Add(name);
        }

        /// <summary>
        /// Adds the name of a subfile to the current directory
        /// </summary>
        /// <param name="name">Name of the file. Just the name, not the path</param>
        public void AddSubFileName(string name)
        {
            _subFilesNames.Add(name);
        }

        /// <summary>
        /// Returns the files in the folder
        /// </summary>
        /// <param name="filter">Optional filter to only return files that contain the filter</param>
        public List<string> GetFiles(string filter = "")
        {
            if (filter == "")
            {
                return _subFilesNames;
            }
            else
            {
                return _subFilesNames.Where(f => f.Contains(filter))
                                     .ToList();
            }
        }

        /// <summary>
        /// Get files for the specified extensions with a path added to the start.
        /// </summary>
        /// <param name="path">Path to be prefixed to the file names</param>
        /// <param name="extensionFilter">One or more extensions to get files for. Should start with a dot(.) (eg. ".sii")</param>
        public List<string> GetFilesByExtension(string path, params string[] extensionFilter)
        {
            if (path.Length > 0 && !path.EndsWith("/")) path += "/";
            if (extensionFilter == null)
            {
                return _subFilesNames.Select(f => $"{path}{f}")
                                     .ToList();
            }
            else
            {
                return _subFilesNames.Where(f => extensionFilter.Contains(Path.GetExtension(f)))
                                     .Select(f => $"{path}{f}")
                                     .ToList();
            }
        }

        public List<string> GetSubDirectoryNames()
        {
            return _subDirectoryNames;
        }
    }
}