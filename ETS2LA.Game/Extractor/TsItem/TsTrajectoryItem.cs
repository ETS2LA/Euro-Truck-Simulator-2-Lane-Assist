using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsTrajectoryItem : TsItem
    {
        public TsTrajectoryItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;
            if (Sector.Version < 846)
                TsTrajectoryItem834(startOffset);
            else if (Sector.Version >= 846 && Sector.Version < 895)
                TsTrajectoryItem846(startOffset);
            else if (Sector.Version >= 895)
                TsTrajectoryItem895(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsTrajectoryItem834(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            var accessRuleCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x08 * nodeCount) + 0x08); // 0x04(nodeCount) + nodeUids + 0x08(flags2 & count1)
            var routeRuleCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x08 * accessRuleCount)); // 0x04(accessRuleCount) + accessRules
            var checkpointCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x14 * routeRuleCount)); // 0x04(routeRuleCount) + routeRules
            fileOffset += 0x04 + (0x10 * checkpointCount) + 0x04; // 0x04(checkpointCount) + checkpoints + 0x04(padding2)
            BlockSize = fileOffset - startOffset;
        }
        public void TsTrajectoryItem846(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            var routeRuleCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x08 * nodeCount) + 0x0C); // 0x04(nodeCount) + nodeUids + 0x0C(flags2 & access_rule)
            var checkpointCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x1C * routeRuleCount)); // 0x04(routeRuleCount) + routeRules
            fileOffset += 0x04 + (0x10 * checkpointCount) + 0x04; // 0x04(checkpointCount) + checkpoints + 0x04(padding2)
            BlockSize = fileOffset - startOffset;
        }
        public void TsTrajectoryItem895(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            var routeRuleCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x08 * nodeCount) + 0x08); // 0x04(nodeCount) + nodeUids + 0x08(flags2)
            var checkpointCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x1C * routeRuleCount)); // 0x04(routeRuleCount) + routeRules
            var tagCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x10 * checkpointCount)); // 0x04(checkpointCount) + checkpoints
            fileOffset += 0x04 + (0x08 * tagCount); // 0x04(tagCount) + tags
            BlockSize = fileOffset - startOffset;
        }
    }
}
