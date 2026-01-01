using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsModelItem : TsItem
    {
        public TsModelItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version >= 895)
                TsModelItem895(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsModelItem895(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var addPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05 + 0x18); // 0x05(flags) + 0x18(modelToken, model_look, model_variant)
            fileOffset += 0x04 + (0x08 * addPartsCount) + 0x24; // 0x04(addPartsCount) + partTokens + 0x24(node_uid + vec3 scale + terrain_mat + terrain_col + terrain_rot)
            BlockSize = fileOffset - startOffset;
        }
    }
}
