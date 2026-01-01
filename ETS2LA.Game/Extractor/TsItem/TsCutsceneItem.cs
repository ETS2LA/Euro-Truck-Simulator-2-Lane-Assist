using System.Collections.Generic;
using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsCutsceneItem : TsItem
    {
        private bool _isSecret;

        public TsCutsceneItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version >= 884)
                TsCutsceneItem844(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsCutsceneItem844(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            _isSecret = MemoryHelper.IsBitSet(MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02), 4);
            var isViewpoint = MemoryHelper.ReadUint8(Sector.Stream, fileOffset) == 0;

            if (isViewpoint)
            {
                Valid = true;
            }
            var tagsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)

            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x04 + (0x08 * tagsCount)), // 0x04(tagsCount) + tags
            };

            var actionCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x08); // 0x08(node_uid)
            fileOffset += 0x04; // 0x04(actionCount)
            for (var i = 0; i < actionCount; ++i)
            {
                var numParamCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
                var stringParamCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (0x04 * numParamCount)); // 0x04
                fileOffset += 0x04; // 0x04(stringParamCount)
                for (var s = 0; s < stringParamCount; ++s)
                {
                    var textLength = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
                    fileOffset += 0x04 + 0x04 + textLength; // 0x04(textLength, could be Uint64) + 0x04(padding) + textLength
                }
                var targetTagCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
                fileOffset += 0x04 + (targetTagCount * 0x08) + 0x08; // 0x04(targetTagCount) + targetTags + 0x08(target_range + action_flags)
            }
            BlockSize = fileOffset - startOffset;
        }

        internal override void Update()
        {
            var node = Sector.Mapper.GetNodeByUid(Nodes[0]);

            if (node == null)
            {
                Logger.Error(
                    $"Could not find node ({Nodes[0]:X}) for item uid: 0x{Uid:X}, " +
                    $"in {Path.GetFileName(Sector.FilePath)} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
                return;
            }

            Sector.Mapper.OverlayManager.AddOverlay("viewpoint", OverlayType.Map,
                node.X, node.Z, "Viewpoint", DlcGuard, _isSecret);

        }
    }
}
