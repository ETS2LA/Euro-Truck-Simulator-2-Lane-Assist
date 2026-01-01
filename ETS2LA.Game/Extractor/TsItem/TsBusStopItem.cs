using System.Collections.Generic;
using System.IO;
using System.Linq;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsBusStopItem : TsItem
    {
        private ulong _prefabUid;

        public TsBusStopItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            if (Sector.Version < 836 || Sector.Version >= 847)
                TsBusStopItem825(startOffset);
            else if (Sector.Version >= 836 || Sector.Version < 847)
                TsBusStopItem836(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsBusStopItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            _prefabUid = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05 + 0x08); // 0x05(flags) + 0x08(city_name)
            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x08), // 0x08(prefab_uid)
            };
            fileOffset += 0x08; // 0x08(node_uid)
            BlockSize = fileOffset - startOffset;
        }
        public void TsBusStopItem836(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            _prefabUid = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05 + 0x08); // 0x05(flags) + 0x08(city_name)
            Nodes = new List<ulong>(1)
            {
                MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x08), // 0x08(prefab_uid)
            };
            fileOffset += 0x0C; // 0x0C(node_uid & padding2)
            BlockSize = fileOffset - startOffset;
        }

        internal override void Update()
        {
            var prefab = Sector.Mapper.Prefabs.FirstOrDefault(x => x.Uid == _prefabUid);

            if (prefab == null) return; // invalid or hidden prefab

            var node = Sector.Mapper.GetNodeByUid(Nodes[0]);
            if (node == null)
            {
                Logger.Error(
                    $"Could not find node ({Nodes[0]:X}) for item uid: 0x{Uid:X}, " +
                    $"in {Path.GetFileName(Sector.FilePath)} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
                return;
            }

            Sector.Mapper.OverlayManager.AddOverlay("bus_stop", OverlayType.BusStop,
                node.X, node.Z, "Bus Stop", DlcGuard);
        }
    }
}
