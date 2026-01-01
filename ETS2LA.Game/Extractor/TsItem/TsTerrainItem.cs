using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.TsItem.Shared;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsTerrainItem : TsItem
    {
        public TsTerrainItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version < 903)
                TsTerrainItem884(startOffset);
            else if (Sector.Version >= 903)
                TsTerrainItem903(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                                      $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsTerrainItem884(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var vegSphereCount =
                MemoryHelper.ReadInt32(Sector.Stream,
                    fileOffset += 0x05 + 0xEA); // 0x05(flags) + 0xE6(offset to veg sphere count)
            fileOffset += 0x04 + VegetationSphereBlockSize * vegSphereCount; // 0x04(vegSphereCount) + vegSpheres
            fileOffset += QuadInfo.Parse(Sector, fileOffset); // quad info 1
            fileOffset += QuadInfo.Parse(Sector, fileOffset); // quad info 2
            fileOffset += 0x20; // 0x20(right_edge + right_edge_look + left_edge + left_edge_look)
            BlockSize = fileOffset - startOffset;
        }

        public void TsTerrainItem903(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var vegSphereCount =
                MemoryHelper.ReadInt32(Sector.Stream,
                    fileOffset += 0x05 + 0xEE); // 0x05(flags) + 0xEE(offset to veg sphere count)
            fileOffset += 0x04 + VegetationSphereBlockSize * vegSphereCount; // 0x04(vegSphereCount) + vegSpheres
            fileOffset += QuadInfo.Parse(Sector, fileOffset); // quad info 1
            fileOffset += QuadInfo.Parse(Sector, fileOffset); // quad info 2
            fileOffset += 0x20; // 0x20(right_edge + right_edge_look + left_edge + left_edge_look)
            BlockSize = fileOffset - startOffset;
        }
    }
}
