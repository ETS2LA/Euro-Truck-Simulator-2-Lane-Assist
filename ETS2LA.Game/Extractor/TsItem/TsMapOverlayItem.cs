using System.Collections.Generic;
using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsMapOverlayItem : TsItem
    {
        private bool _isSecret;
        private string _overlayName;

        private OverlayType _type = OverlayType.Road;
        private byte _zoomLevelVisibility;

        public TsMapOverlayItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            if (Sector.Version < 898)
                TsMapOverlayItem825(startOffset);
            else if (Sector.Version >= 898)
                TsMapOverlayItem898(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsMapOverlayItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            _zoomLevelVisibility = MemoryHelper.ReadUint8(Sector.Stream, fileOffset);
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = _zoomLevelVisibility == 255;
            _isSecret = MemoryHelper.IsBitSet(MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02), 3);

            var type = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02);
            var overlayToken = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05);
            if (MemoryHelper.IsBitSet(type, 0) && overlayToken == 0)
            {
                _overlayName = "parking_ico"; // parking
                _type = OverlayType.Map;
            }
            else if (MemoryHelper.IsBitSet(type, 4))
            {
                _overlayName = "photo_sight_captured"; // Landmark
                _type = OverlayType.Map;
            }
            else
            {
                _overlayName = ScsToken.TokenToString(overlayToken);
            }

            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x08) // 0x08(overlayToken)
            };

            fileOffset += 0x08; // 0x08(nodeUid)
            BlockSize = fileOffset - startOffset;
        }

        public void TsMapOverlayItem898(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            _zoomLevelVisibility = MemoryHelper.ReadUint8(Sector.Stream, fileOffset);
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = _zoomLevelVisibility == 255;
            _isSecret = MemoryHelper.IsBitSet(MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02), 1);

            var type = MemoryHelper.ReadUint8(Sector.Stream, fileOffset) & 0x0F;
            var overlayToken = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05);
            if (type == 1)
            {
                _overlayName = "parking_ico"; // parking
                _type = OverlayType.Map;
            }
            else if (type == 4)
            {
                _overlayName = "photo_sight_captured"; // Landmark
                _type = OverlayType.Map;
            }
            else
            {
                _overlayName = ScsToken.TokenToString(overlayToken);
            }

            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x08) // 0x08(overlayToken)
            };

            fileOffset += 0x08; // 0x08(nodeUid)
            BlockSize = fileOffset - startOffset;
        }

        internal override void Update()
        {
            if (_overlayName == "") return;

            var node = Sector.Mapper.GetNodeByUid(Nodes[0]);

            if (node == null)
            {
                Logger.Error(
                    $"Could not find node ({Nodes[0]:X}) for item uid: 0x{Uid:X}, " +
                    $"in {Path.GetFileName(Sector.FilePath)} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
                return;
            }

            var overlay = Sector.Mapper.OverlayManager.CreateOverlay(_overlayName, _type);

            if (overlay == null)
            {
                Logger.Error(
                    $"Could not find Overlay: '{_overlayName}'({ScsToken.StringToToken(_overlayName):X}), item uid: 0x{Uid:X}, " +
                    $"in {Path.GetFileName(Sector.FilePath)} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
                return;
            }

            overlay.SetTypeName("Overlay");
            overlay.SetSecret(_isSecret);
            overlay.SetPosition(node.X, node.Z);
            overlay.SetZoomLevelVisibility(_zoomLevelVisibility);
            overlay.SetDlcGuard(DlcGuard);

            Sector.Mapper.OverlayManager.AddOverlay(overlay);
        }
    }
}
