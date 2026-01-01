namespace ETS2LA.Game.Extractor.FileSystem
{
    /// <summary>
    /// Contains the data of an entry in an <see cref="ArchiveFile"/>.
    /// Has location and size of the raw data of either a file or a directory
    /// </summary>
    public abstract class Entry
    {
        /// <summary>
        /// Offset in file to where the data starts
        /// </summary>
        internal ulong Offset { private get; set; }

        /// <summary>
        /// File/dir path hashed by CityHash64
        /// </summary>
        internal ulong Hash { private get; set; }

        /// <summary>
        /// Total size when inflated
        /// </summary>
        internal uint Size { private get; set; }

        /// <summary>
        /// Size in archive file
        /// </summary>
        internal uint CompressedSize { private get; set; }

        private readonly ArchiveFile _archiveFile;

        public Entry(ArchiveFile fsFile)
        {
            _archiveFile = fsFile;
        }

        /// <summary>
        /// Get's the <see cref="ArchiveFile"/> (.scs) where the current entry is located in.
        /// </summary>
        internal ArchiveFile GetArchiveFile()
        {
            return _archiveFile;
        }

        /// <summary>
        /// Reads the entry data from the archive file
        /// </summary>
        /// <returns>The data, inflating it if necessary.</returns>
        public abstract byte[] Read();

        /// <summary>
        /// Inflates the compressed data
        /// </summary>
        /// <returns>Inflated data</returns>
        protected abstract byte[] Inflate(byte[] buff);


        /// <returns>Given hash for hash files, CityHashed path for zip files</returns>
        public ulong GetHash()
        {
            return Hash;
        }

        public virtual uint GetSize()
        {
            return Size;
        }

        public virtual ulong GetOffset()
        {
            return Offset;
        }

        public virtual uint GetCompressedSize()
        {
            return CompressedSize;
        }

        public abstract bool IsCompressed();

        public abstract bool IsDirectory();

    }
}