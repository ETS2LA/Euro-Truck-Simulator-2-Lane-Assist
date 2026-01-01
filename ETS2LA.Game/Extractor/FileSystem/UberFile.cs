namespace ETS2LA.Game.Extractor.FileSystem
{
    /// <summary>
    /// Represents a file in the filesystem
    /// <para>Currently nothing more than just an <see cref="FileSystem.Entry"/> with how the workings of the filesystem changed,
    /// just keeping this in case I want to add something specific to files</para>
    /// <para>Is unaware of it's own location/path</para>
    /// </summary>
    public class UberFile
    {
        public Entry Entry { get; }

        public UberFile(Entry entry)
        {
            Entry = entry;
        }
    }
}