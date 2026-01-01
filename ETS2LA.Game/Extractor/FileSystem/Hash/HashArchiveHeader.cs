namespace ETS2LA.Game.Extractor.FileSystem.Hash
{
    internal class HashArchiveHeader
    {
        internal uint Magic { get; set; }
        internal ushort Version { get; set; }
        internal ushort Salt { get; set; }
        internal uint HashMethod { get; set; }
        internal uint EntryCount { get; set; }
        internal uint StartOffset { get; set; }

        public override string ToString()
        {
            return $"Magic {Magic}\n" +
                   $"Version {Version}\n" +
                   $"Salt {Salt}\n" +
                   $"HashMethod {HashMethod}\n" +
                   $"EntryCount {EntryCount}\n" +
                   $"StartOffset {StartOffset}";
        }
    }
}