using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsBuildingItem : TsItem
    {
        public TsBuildingItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version >= 858)
                TsBuildingItem858(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                                      $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsBuildingItem858(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var buildingHeightOffsetCount =
                MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05 + 0x2C); // 0x05(flags) + 0x2C(offset to buildingHeightOffsetCount)
            fileOffset +=
                0x04 + 0x04 * buildingHeightOffsetCount; // 0x04(buildingHeightOffsetCount) + buildingHeightOffsets
            BlockSize = fileOffset - startOffset;
        }
    }
}
