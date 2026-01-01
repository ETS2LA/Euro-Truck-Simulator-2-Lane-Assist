using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsTrafficRuleItem : TsItem
    {
        public TsTrafficRuleItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;
            if (Sector.Version < 834)
                TsTrafficRuleItem825(startOffset);
            else if (Sector.Version >= 834)
                TsTrafficRuleItem834(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsTrafficRuleItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            fileOffset += 0x04 + 0x08 * nodeCount + 0x0C; // 0x04(nodeCount) + nodeUids + 0x0C(traffic_rule_id & range)
            BlockSize = fileOffset - startOffset;
        }
        public void TsTrafficRuleItem834(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var tagCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x08 * tagCount)); // 0x04(tagCount) + tags;
            fileOffset += 0x04 + 0x08 * nodeCount + 0x0C; // 0x04(nodeCount) + nodeUids + 0x0C(traffic_rule_id & range)
            BlockSize = fileOffset - startOffset;
        }
    }
}
