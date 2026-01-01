using System;
using System.IO;
using ETS2LA.Game.Extractor.FileSystem;
using ETS2LA.Game.Extractor.TsItem;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor
{
    public class TsSector
    {
        public string FilePath { get; }
        public TsMapper Mapper { get; }


        public int Version { get; private set; }
        private bool _empty;

        public byte[] Stream { get; private set; }

        private readonly UberFile _file;

        public TsSector(TsMapper mapper, string filePath)
        {
            Mapper = mapper;
            FilePath = filePath;
            _file = UberFileSystem.Instance.GetFile(FilePath);
            if (_file == null)
            {
                _empty = true;
                return;
            }

            Stream = _file.Entry.Read();
        }

        public void Parse()
        {
            Version = BitConverter.ToInt32(Stream, 0x0);

            if (Version < 825)
            {
                Logger.Error($"{FilePath} version ({Version}) is too low, min. is 825");
                return;
            }

            var itemCount = BitConverter.ToUInt32(Stream, 0x10);
            if (itemCount == 0) _empty = true;
            if (_empty) return;

            var lastOffset = 0x14;

            for (var i = 0; i < itemCount; i++)
            {
                var type = (TsItemType)MemoryHelper.ReadUInt32(Stream, lastOffset);
                if (Version <= 825) type++; // after version 825 all types were pushed up 1

                TsItem.TsItem item = null;

                switch (type)
                {
                    case TsItemType.Terrain: // used to all be in .aux files, not sure why some are now in .base files
                    {
                        item = new TsTerrainItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Building: // used to all be in .aux files, not sure why some are now in .base files
                    {
                        item = new TsBuildingItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Road:
                    {
                        item = new TsRoadItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        if (item.Valid && !item.Hidden) Mapper.Roads.Add((TsRoadItem) item);
                        break;
                    }
                    case TsItemType.Prefab:
                    {
                        item = new TsPrefabItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        if (item.Valid && !item.Hidden) Mapper.Prefabs.Add((TsPrefabItem) item);
                        break;
                    }
                    case TsItemType.Model: // used to all be in .aux files, not sure why some are now in .base files
                    {
                        item = new TsModelItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Company:
                    {
                        item = new TsCompanyItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Service:
                    {
                        item = new TsServiceItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.CutPlane:
                    {
                        item = new TsCutPlaneItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.City:
                    {
                        item = new TsCityItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        if (item.Valid && !item.Hidden) Mapper.Cities.Add((TsCityItem) item);
                        break;
                    }
                    case TsItemType.MapOverlay:
                    {
                        item = new TsMapOverlayItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Ferry:
                    {
                        item = new TsFerryItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        if (item.Valid && !item.Hidden) Mapper.FerryConnections.Add((TsFerryItem) item);
                        break;
                    }
                    case TsItemType.Garage:
                    {
                        item = new TsGarageItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Trigger:
                    {
                        item = new TsTriggerItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.FuelPump:
                    {
                        item = new TsFuelPumpItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.RoadSideItem:
                    {
                        item = new TsRoadSideItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.BusStop:
                    {
                        item = new TsBusStopItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.TrafficRule:
                    {
                        item = new TsTrafficRuleItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.BezierPatch: // used to all be in .aux files, not sure why some are now in .base files
                        {
                            item = new TsBezierPatchItem(this, lastOffset);
                            lastOffset += item.BlockSize;
                            break;
                        }
                    case TsItemType.TrajectoryItem:
                    {
                        item = new TsTrajectoryItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.MapArea:
                    {
                        item = new TsMapAreaItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        if (item.Valid && !item.Hidden) Mapper.MapAreas.Add((TsMapAreaItem) item);
                        break;
                    }
                    case TsItemType.Curve: // used to all be in .aux files, not sure why some are now in .base files
                    {
                        item = new TsCurveItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.Cutscene:
                    {
                         item = new TsCutsceneItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    case TsItemType.VisibilityArea:
                    {
                        item = new TsVisibilityAreaItem(this, lastOffset);
                        lastOffset += item.BlockSize;
                        break;
                    }
                    default:
                    {
                        Logger.Warn($"Unknown Type: {type} in {Path.GetFileName(FilePath)} @ {lastOffset}");
                        break;
                    }
                }

                 if (item != null && item.Valid && !item.Hidden) Mapper.MapItems.Add(item);
            }

            var nodeCount = MemoryHelper.ReadInt32(Stream, lastOffset);
            for (var i = 0; i < nodeCount; i++)
            {
                TsNode node = new TsNode(this, lastOffset += 0x04);
                Mapper.UpdateEdgeCoords(node);
                if (!Mapper.Nodes.ContainsKey(node.Uid))
                    Mapper.Nodes.Add(node.Uid, node);
                lastOffset += 0x34;
            }

            lastOffset += 0x04;
            if (Version >= 891)
            {
                var visAreaChildCount = BitConverter.ToInt32(Stream, lastOffset);
                lastOffset += 0x04 + (0x08 * visAreaChildCount); // 0x04(visAreaChildCount) + (visAreaChildUids)
            }
            if (lastOffset != Stream.Length)
            {
                Logger.Warn($"File '{Path.GetFileName(FilePath)}' from '{GetUberFile().Entry.GetArchiveFile().GetPath()}' was not read correctly. " +
                    $"Read offset was at 0x{lastOffset:X} while file is 0x{Stream.Length:X} bytes long.");
            }
        }

        internal UberFile GetUberFile()
        {
            return _file;
        }

        public void ClearFileData()
        {
            Stream = null;
        }
    }
}