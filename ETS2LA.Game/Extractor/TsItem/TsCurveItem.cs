using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsCurveItem : TsItem
    {
        public TsCurveItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version >= 896)
                TsCurveItem896(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                                      $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsCurveItem896(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var heightOffsetCount =
                MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05 + 0x6C); // 0x05(flags) + 0x6C(offset to heightOffsetCount)
            fileOffset +=
                0x04 + 0x04 * heightOffsetCount; // 0x04(heightOffsetCount) + heightOffsets
            BlockSize = fileOffset - startOffset;
        }
    }
}
