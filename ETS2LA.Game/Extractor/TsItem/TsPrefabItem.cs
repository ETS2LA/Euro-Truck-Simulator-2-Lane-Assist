using System;
using System.Collections.Generic;
using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsPrefabItem : TsItem
    {
        private const int NodeLookBlockSize = 0x3A;
        private const int NodeLookBlockSize825 = 0x38;
        private const int PrefabVegetationBlockSize = 0x20;
        public int Origin { get; private set; }
        public TsPrefab Prefab { get; private set; }
        private List<TsPrefabLook> _looks;

        public bool IsSecret { get; private set; }

        public void AddLook(TsPrefabLook look)
        {
            _looks.Add(look);
        }

        public List<TsPrefabLook> GetLooks()
        {
            return _looks;
        }

        public bool HasLooks()
        {
            return _looks != null && _looks.Count != 0;
        }

        public TsPrefabItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            _looks = new List<TsPrefabLook>();
            Nodes = new List<ulong>();
            if (Sector.Version < 829)
                TsPrefabItem825(startOffset);
            else if (Sector.Version >= 829 && Sector.Version < 831)
                TsPrefabItem829(startOffset);
            else if (Sector.Version >= 831 && Sector.Version < 846)
                TsPrefabItem831(startOffset);
            else if (Sector.Version >= 846 && Sector.Version < 854)
                TsPrefabItem846(startOffset);
            else if (Sector.Version == 854)
                TsPrefabItem854(startOffset);
            else if (Sector.Version >= 855)
                TsPrefabItem855(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                    $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsPrefabItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x18); // 0x18(id & look & variant)
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }

            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            var prefabVegetationCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x01 + 0x01 + (NodeLookBlockSize825 * nodeCount)); // 0x01(origin) + 0x01(padding) + nodeLooks
            var vegetationSphereCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x04 + (PrefabVegetationBlockSize * prefabVegetationCount) + 0x04); // 0x04(prefabVegCount) + prefabVegs + 0x04(padding2)
            fileOffset += 0x04 + (VegetationSphereBlockSize825 * vegetationSphereCount); // 0x04(vegSphereCount) + vegSpheres


            BlockSize = fileOffset - startOffset;
        }

        public void TsPrefabItem829(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }

            var additionalPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x18); // 0x18(id & look & variant)
            var nodeCount = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * additionalPartsCount)); // 0x04(addPartsCount) + additionalParts
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }

            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            var prefabVegetationCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x01 + 0x01 + (NodeLookBlockSize825 * nodeCount)); // 0x01(origin) + 0x01(padding) + nodeLooks
            var vegetationSphereCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x04 + (PrefabVegetationBlockSize * prefabVegetationCount) + 0x04); // 0x04(prefabVegCount) + prefabVegs + 0x04(padding2)
            fileOffset += 0x04 + (VegetationSphereBlockSize * vegetationSphereCount); // 0x04(vegSphereCount) + vegSpheres


            BlockSize = fileOffset - startOffset;
        }

        public void TsPrefabItem831(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }

            var additionalPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x18); // 0x18(id & look & variant)
            var nodeCount = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * additionalPartsCount)); // 0x04(addPartsCount) + additionalParts
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }

            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            var prefabVegetationCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x01 + 0x01 + (NodeLookBlockSize825 * nodeCount)); // 0x01(origin) + 0x01(padding) + nodeLooks
            var vegetationSphereCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x04 + (PrefabVegetationBlockSize * prefabVegetationCount) + 0x04); // 0x04(prefabVegCount) + prefabVegs + 0x04(padding2)
            fileOffset += 0x04 + (VegetationSphereBlockSize * vegetationSphereCount) + (0x18 * nodeCount); // 0x04(vegSphereCount) + vegSpheres + padding
            BlockSize = fileOffset - startOffset;
        }
        public void TsPrefabItem846(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }

            var additionalPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x18); // 0x18(id & look & variant)
            var nodeCount = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * additionalPartsCount)); // 0x04(addPartsCount) + additionalParts
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }

            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            var prefabVegetationCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x01 + 0x01 + (NodeLookBlockSize * nodeCount)); // 0x01(origin) + 0x01(padding) + nodeLooks
            var vegetationSphereCount = MemoryHelper.ReadInt32(Sector.Stream,
                fileOffset += 0x04 + (PrefabVegetationBlockSize * prefabVegetationCount) + 0x04); // 0x04(prefabVegCount) + prefabVegs + 0x04(padding2)
            fileOffset += 0x04 + (VegetationSphereBlockSize * vegetationSphereCount) + (0x18 * nodeCount); // 0x04(vegSphereCount) + vegSpheres + padding
            BlockSize = fileOffset - startOffset;
        }

        public void TsPrefabItem854(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }
            var additionalPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x08 + 0x08); // 0x08(prefabId) + 0x08(m_variant)
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (additionalPartsCount * 0x08)); // 0x04(addPartsCount) + additionalParts
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }
            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            fileOffset += 0x02 + nodeCount * 0x0C; // 0x02(origin & padding) + nodeLooks

            BlockSize = fileOffset - startOffset;
        }
        public void TsPrefabItem855(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);
            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x02) & 0x02) != 0;
            IsSecret = MemoryHelper.IsBitSet(MemoryHelper.ReadUint8(Sector.Stream, fileOffset), 5);

            var prefabId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            Prefab = Sector.Mapper.LookupPrefab(prefabId);
            if (Prefab == null)
            {
                Valid = false;
                Logger.Error($"Could not find Prefab: '{ScsToken.TokenToString(prefabId)}'({prefabId:X}), item uid: 0x{Uid:X}, " +
                        $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }
            var additionalPartsCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x08 + 0x08); // 0x08(prefabId) + 0x08(m_variant)
            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x04 + (additionalPartsCount * 0x08)); // 0x04(addPartsCount) + additionalParts
            fileOffset += 0x04; // set cursor after nodeCount
            for (var i = 0; i < nodeCount; i++)
            {
                Nodes.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }
            var connectedItemCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset);
            Origin = MemoryHelper.ReadUint8(Sector.Stream, fileOffset += 0x04 + (0x08 * connectedItemCount) + 0x08); // 0x04(connItemCount) + connItemUids + 0x08(m_some_uid)
            fileOffset += 0x02 + nodeCount * 0x0C + 0x08; // 0x02(origin & padding) + nodeLooks + 0x08(padding2)

            BlockSize = fileOffset - startOffset;
        }

        internal override void Update()
        {
            var originNode = Sector.Mapper.GetNodeByUid(Nodes[0]);
            if (Prefab?.PrefabNodes == null) return;

            var mapPointOrigin = Prefab.PrefabNodes[Origin];

            var rot = (float)(originNode.Rotation - Math.PI -
                Math.Atan2(mapPointOrigin.RotZ, mapPointOrigin.RotX) + Math.PI / 2);

            var prefabstartX = originNode.X - mapPointOrigin.X;
            var prefabStartZ = originNode.Z - mapPointOrigin.Z;
            foreach (var spawnPoint in Prefab.SpawnPoints)
            {
                var newPoint = RenderHelper.RotatePoint(prefabstartX + spawnPoint.X, prefabStartZ + spawnPoint.Z, rot,
                    originNode.X, originNode.Z);

                var overlayName = "";
                var displayName = "";

                if (spawnPoint.Type == TsSpawnPointType.GasPos)
                {
                    overlayName = "gas_ico";
                    displayName = "Fuel";
                }

                else if (spawnPoint.Type == TsSpawnPointType.ServicePos)
                {
                    overlayName = "service_ico";
                    displayName = "Service";
                }
                else if (spawnPoint.Type == TsSpawnPointType.WeightStationPos)
                {
                    overlayName = "weigh_station_ico";
                    displayName = "WeightStation";
                }
                else if (spawnPoint.Type == TsSpawnPointType.TruckDealerPos)
                {
                    overlayName = "dealer_ico";
                    displayName = "TruckDealer";
                }
                else if (spawnPoint.Type == TsSpawnPointType.BuyPos)
                {
                    overlayName = "garage_large_ico";
                    displayName = "Garage";
                }
                else if (spawnPoint.Type == TsSpawnPointType.RecruitmentPos)
                {
                    overlayName = "recruitment_ico";
                    displayName = "Recruitment";
                }

                Sector.Mapper.OverlayManager.AddOverlay(overlayName, OverlayType.Map, newPoint.X, newPoint.Y,
                    displayName, DlcGuard, IsSecret);
            }

            var lastId = -1;
            foreach (var triggerPoint in Prefab.TriggerPoints) // trigger points in prefabs: garage, hotel, ...
            {
                var newPoint = RenderHelper.RotatePoint(prefabstartX + triggerPoint.X, prefabStartZ + triggerPoint.Z,
                    rot,
                    originNode.X, originNode.Z);

                if (triggerPoint.TriggerId == lastId) continue;
                lastId = (int)triggerPoint.TriggerId;

                if (triggerPoint.TriggerActionToken == ScsToken.StringToToken("hud_parking")) // parking trigger
                {
                    Sector.Mapper.OverlayManager.AddOverlay("parking_ico", OverlayType.Map, newPoint.X, newPoint.Y,
                        "Parking", DlcGuard, IsSecret);
                }
            }
        }
    }
}
