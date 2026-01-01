using System.IO;

namespace ETS2LA.Game.Extractor.FileSystem
{
    /// <summary>
    /// Represents an archive file (*.scs, *.zip)
    /// </summary>
    public abstract class ArchiveFile
    {
        protected readonly string _path;

        public BinaryReader Br { get; protected set; }

        public ArchiveFile(string path)
        {
            _path = path;
        }

        // TODO: Figure out if this fileSystem param is necessary. I didn't know about
        // UberFileSystem.instance, so if that works I'll use it instead. (got errors in zip otherwise)
        // - Tumppi066
        public abstract bool Parse(UberFileSystem fileSystem);

        public string GetPath()
        {
            return _path;
        }

        ~ArchiveFile()
        {
            if (Br == null) return;
            Br.Close();
            Br = null;
        }
    }
}