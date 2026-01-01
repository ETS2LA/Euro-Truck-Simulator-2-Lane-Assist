using System.Collections.Generic;
using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsFerryItem : TsItem
    {
        public ulong FerryPortId { get; private set; }

        private bool _train;

        public TsFerryItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            TsFerryItem825(startOffset);
        }

        public void TsFerryItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            _train = MemoryHelper.ReadUint8(Sector.Stream, fileOffset) != 0;

            FerryPortId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05);

            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x08 + 0x08) // 0x08(FerryPortId) + 0x08(prefab_link_uid)
            };
            Sector.Mapper.AddFerryPortLocation(FerryPortId, X, Z);
            fileOffset += 0x08 + 0x0C; // 0x08(node_uid) + 0x0C(unloadoffset)
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

            var overlayName = _train ? "train_ico" : "port_overlay";
            if (!Sector.Mapper.OverlayManager.AddOverlay(overlayName, OverlayType.Road, node.X, node.Z, _train ? "Train" : "Ferry", DlcGuard))
            {
                // Logger.Error(
                //     $"Could not find Overlay: '{overlayName}'({ScsToken.StringToToken(overlayName):X}), item uid: 0x{Uid:X}, " +
                //     $"in {Path.GetFileName(Sector.FilePath)} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }
        }
    }
}
