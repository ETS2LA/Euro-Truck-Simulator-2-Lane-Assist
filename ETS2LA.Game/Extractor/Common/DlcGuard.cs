namespace ETS2LA.Game.Extractor.Common
{
    public class DlcGuard
    {
        public string Name { get; }
        public byte Index { get; }

        public bool Enabled { get; set; }

        public DlcGuard(string name, byte index, bool enabled = true)
        {
            Name = name;
            Index = index;
            Enabled = enabled;
        }

        public override string ToString()
        {
            return $"{Name} - {Index}";
        }
    }
}