using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsGarageItem : TsItem
    {
        public TsGarageItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            if (Sector.Version < 855)
                TsGarageItem825(startOffset);
            else if (Sector.Version >= 855)
                TsGarageItem855(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }
        public void TsGarageItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            fileOffset += 0x05 + 0x1C; // 0x05(flags) + 0x1C(city_name & m_type & 2 uids)
            BlockSize = fileOffset - startOffset;
        }
        public void TsGarageItem855(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var subItemUidCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05 + 0x1C); // 0x05(flags) + 0x1C(city_name & m_type & 2 uids)
            fileOffset += 0x04 + (0x08 * subItemUidCount); // 0x04(subItemUidCount) + subItemUids
            BlockSize = fileOffset - startOffset;
        }
    }
}
