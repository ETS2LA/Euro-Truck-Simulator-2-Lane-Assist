using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsCutPlaneItem : TsItem
    {
        public TsCutPlaneItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;
            TsCutPlaneItem825(startOffset);
        }

        public void TsCutPlaneItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05);
            fileOffset += 0x04 + (0x08 * nodeCount);
            BlockSize = fileOffset - startOffset;
        }
    }
}
