using System;
using System.IO;

namespace ETS2LA.Game.Extractor
{
    [Flags]
    public enum RenderFlags : uint
    {
        None = 0,
        TextOverlay = 1 << 0, // 1
        Prefabs = 1 << 1, // 2
        Roads = 1 << 2, // 4
        MapAreas = 1 << 3, // 8
        MapOverlays = 1 << 4, // 16
        FerryConnections = 1 << 5, // 32
        CityNames = 1 << 6, // 64
        SecretRoads = 1 << 7, // 128
        BusStopOverlay = 1 << 8, // 256
        All = int.MaxValue
    }

    [Flags]
    public enum ExportFlags : uint
    {
        None = 0,
        TileMapInfo = 1 << 0, // 1
        CityList = 1 << 1, // 2
        CityDimensions = 1 << 2, // 4
        CityLocalizedNames = 1 << 3, // 8
        CountryList = 1 << 4, // 16
        CountryLocalizedNames = 1 << 5, // 32
        OverlayList = 1 << 6, // 64
        OverlayPNGs = 1 << 7, // 128
        All = int.MaxValue
    }

    public static class FlagMethods
    {
        public static bool IsActive(this RenderFlags self, RenderFlags value)
        {
            return (self & value) == value;
        }
        public static bool IsActive(this ExportFlags self, ExportFlags value)
        {
            return (self & value) == value;
        }
    }
    public class Mod
    {
        public string ModPath { get; set; }
        public bool Load { get; set; }

        public Mod(string path)
        {
            ModPath = path;
            Load = false;
        }

        public override string ToString()
        {
            return Path.GetFileName(ModPath);
        }
    }

    public enum TsItemType
    {
        Terrain = 1,
        Building = 2,
        Road = 3,
        Prefab = 4,
        Model = 5,
        Company = 6,
        Service = 7,
        CutPlane = 8,
        Mover = 9,
        ShadowMap = 10,
        NoWeather = 11,
        City = 12,
        Hinge = 13,
        Parking = 14,
        AnimatedModel = 15,
        Hq = 16,
        Lock = 17,
        MapOverlay = 18,
        Ferry = 19,
        MissionPoint = 20,
        Sound = 21,
        Garage = 22,
        CameraPoint = 23,
        ParkingPoint = 24,
        FixedCar = 25,
        TrailerStart = 26,
        TruckStart = 27,
        Walker = 28,
        YetdFinish = 29,
        YetdTriplet = 30,
        YetdFixable = 31,
        YetdBall = 32,
        YetdRod = 33,
        Trigger = 34,
        FuelPump = 35, // ets_garage_gas
        RoadSideItem = 36, // sign
        BusStop = 37,
        TrafficRule = 38, // traffic_area
        BezierPatch = 39,
        Compound = 40,
        TrajectoryItem = 41,
        MapArea = 42,
        FarModel = 43,
        Curve = 44,
        Camera = 45,
        Cutscene = 46,
        Hookup = 47,
        VisibilityArea = 48,
        Gate = 49,
    };


    // values from https://github.com/SCSSoftware/BlenderTools/blob/master/addon/io_scs_tools/consts.py
    public enum TsSpawnPointType
    {
        None = 0,
        TrailerPos = 1,
        UnloadEasyPos = 2,
        GasPos = 3,
        ServicePos = 4,
        TruckStopPos = 5,
        WeightStationPos = 6,
        TruckDealerPos = 7,
        Hotel = 8,
        Custom = 9,
        Parking = 10, // also shows parking in companies which don't work/show up in game
        Task = 11,
        MeetPos = 12,
        CompanyPos = 13,
        GaragePos = 14, // manage garage
        BuyPos = 15, // buy garage
        RecruitmentPos = 16,
        CameraPoint = 17,
        BusStation = 18,
        UnloadMediumPos = 19,
        UnloadHardPos = 20,
        UnloadRigidPos = 21,
        WeightCatPos = 22,
        CompanyUnloadPos = 23,
        TrailerSpawn = 24,
        LongTrailerPos = 25,
    }
}