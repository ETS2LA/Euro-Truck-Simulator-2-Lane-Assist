using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsServiceItem : TsItem
    {
        public TsServiceItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;
            if (Sector.Version < 855)
                TsServiceItem825(startOffset);
            else if (Sector.Version >= 855)
                TsServiceItem855(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsServiceItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            fileOffset += 0x15;
            BlockSize = fileOffset - startOffset;
        }
        public void TsServiceItem855(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var subItemUidCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05 + 0x10); // 0x05(flags) + 0x10(2 uids)
            fileOffset += 0x04 + (0x08 * subItemUidCount); // 0x04(subItemUidCount) + subItemUids
            BlockSize = fileOffset - startOffset;
        }
    }
}
