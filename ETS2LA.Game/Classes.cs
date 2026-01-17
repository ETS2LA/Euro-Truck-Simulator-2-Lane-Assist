using ETS2LA.Logging;
using ETS2LA.Shared;
using TruckLib.HashFs;
using TruckLib.ScsMap;
using TruckLib;

namespace ETS2LA.Game;

public enum GameType
{
    EuroTruckSimulator2,
    AmericanTruckSimulator
}

public class Mod
{
    public required string Path { get; set; }
    public required bool Load { get; set; }
}

public enum IgnoredItemTypes
{
    Terrain = 0x01,
    Buildings = 0x02,
    Model = 0x05,
    Company = 0x06,
    Service = 0x07,
    CutPlane = 0x08,
    Mover = 0x09,
    EnvironmentArea = 0x0B,
    CityArea = 0x0C,
    Hinge = 0x0D,
    AnimatedModel = 0x0F,
    MapOverlay = 0x12,
    Sound = 0x15,
    Garage = 0x16,
    CameraPoint = 0x17,
    Walker = 0x1C,
    Trigger = 0x22,
    Sign = 0x24,
    TrafficArea = 0x26,
    BezierPatch = 0x27,
    Compound = 0x28,
    Trajectory = 0x29,
    MapArea = 0x2A,
    FarModel = 0x2B,
    Curve = 0x2C,
    CameraPath = 0x2D,
    Cutscene = 0x2E,
    Hookup = 0x2F,
    VisibilityArea = 0x30,
};

public class MapData : Map
{
    INotificationHandler? _notificationHandler = null;
    public void SetNotificationHandler(INotificationHandler? handler)
    {
        _notificationHandler = handler;
    }

    protected override bool PostProcessItem(MapItem item) 
    {
        // Items ETS2LA doesn't need.
        if (typeof(IgnoredItemTypes).GetEnumNames().Contains(item.ItemType.ToString()))
        {
            return false;
        }
        
        // Additionally drop terrain data of prefabs and roads;
        // also saves some memory.
        if (item is Prefab p)
        {
            foreach (var node in p.PrefabNodes)
            {
                node.Terrain = null;
            }
        }
        else if (item is Road r)
        {
            r.Left.Terrain = null;
            r.Right.Terrain = null;
        }         
        return true;
    }

    protected override void OnSectorLoading(Sector sector, int index, int total)
    {
        _notificationHandler?.SendNotification(new Notification
        {
            Id = "ETS2LA.Game.Parsing",
            Title = "Parsing Map Data",
            Content = $"Parsing sector {index + 1} of {total}...",
            IsProgressIndeterminate = false,
            Progress = ((index + 1) / (float)total) * 100f,
            CloseAfter = 0
        });
    }
}

public class Installation
{
    public required GameType Type { get; set; }
    public required string Path { get; set; }
    public required string ExecutablePath { get; set; }
    public required string Version { get; set; }
    public bool IsParsed { get; set; } = false;
    public bool IsParsing { get; set; } = false;
    public List<string> FileExclusions = new List<string>
    {
        "dlc_winter.scs",
    };

    private AssetLoader? _assetLoader = null;
    private MapData? _map = null;
    private List<Mod>? _selectedMods = null;
    private INotificationHandler? _notificationHandler = null;

    public void SetNotificationHandler(INotificationHandler? handler)
    {
        _notificationHandler = handler;
    }

    public string GetModsPath()
    {
        string gameName = Type == GameType.EuroTruckSimulator2 ? "Euro Truck Simulator 2" : "American Truck Simulator";
        string documentsPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
        return System.IO.Path.Combine(documentsPath, gameName, "mod");
    }

    public List<string> GetSelectedMods()
    {
        if (_selectedMods == null)
        {
            return new List<string>();
        }
        return _selectedMods
            .Select(m => System.IO.Path.GetFileNameWithoutExtension(m.Path))
            .ToList();
    }

    public List<string> GetAvailableMods()
    {
        string modsPath = GetModsPath();
        if (!Directory.Exists(modsPath))
            return new List<string>();

        List<string> mods = Directory.GetFiles(modsPath, "*.scs").ToList();
        mods = mods
            .Select(m => System.IO.Path.GetFileNameWithoutExtension(m))
            .ToList();
        return mods;
    }

    public void SetSelectedMods(List<string> mods)
    {
        string modsPath = GetModsPath();
        _selectedMods = mods.Select(m => new Mod
        {
            Path = System.IO.Path.Combine(modsPath, m + ".scs"),
            Load = true
        }).ToList();
        Logger.Info($"Selected {_selectedMods.Count} mods for installation at '{Path}'");
    }

    private void GetSCSFilesInRootDirectory(List<string> scsFiles)
    {
        foreach (string file in Directory.GetFiles(Path, "*.scs"))
        {
            if (FileExclusions.Contains(System.IO.Path.GetFileName(file)))
                continue;
            scsFiles.Add(file);
        }
    }

    private string GetMapFilepath()
    {
        return Type == GameType.EuroTruckSimulator2 ? "/map/europe.mbd" : "/map/usa.mbd";
    }

    public MapData GetMapData()
    {
        if (_map == null)
        {
            List<string> scsFiles = new List<string>();
            GetSCSFilesInRootDirectory(scsFiles);
            foreach (Mod mod in _selectedMods ?? new List<Mod>())
            {
                if (mod.Load && File.Exists(mod.Path))
                {
                    Logger.Info($"Adding mod: {mod.Path}");
                    scsFiles.Add(mod.Path);
                }
            }

            IFileSystem[] hashFsReaders = scsFiles
                .Select(file => HashFsReader.Open(file) as IFileSystem)
                .ToArray();

            _assetLoader = new AssetLoader(hashFsReaders);
            _map = new MapData();
            _map.SetNotificationHandler(_notificationHandler);
            _map.Read(GetMapFilepath(), _assetLoader);
        }
        return _map;
    }

    public void Parse()
    {
        if (IsParsed)
        {
            Logger.Warn($"Installation at '{Path}' has already been parsed.");
            return;
        }

        IsParsing = true;
        Logger.Info($"Parsing installation at '{Path}' (version: {Version})");
        _notificationHandler?.SendNotification(new Notification
        {
            Id = "ETS2LA.Game.Parsing",
            Title = "Parsing Map Data",
            Content = "Initializing...",
            IsProgressIndeterminate = true,
            CloseAfter = 0
        });
        
        GetMapData();
        if (_map == null)
        {
            Logger.Error($"Failed to load map for installation at '{Path}'");
            IsParsing = false;
            _notificationHandler?.CloseNotification("ETS2LA.Game.Parsing");
            return;
        }

        int prefabs = _map.MapItems.Where(x => x.Value is Prefab).ToList().Count;
        int roads = _map.MapItems.Where(x => x.Value is Road).ToList().Count;
        int nodes = _map.Nodes.Count;

        if (prefabs == 0 && roads == 0 && nodes == 0)
        {
            Logger.Warn($"No map data found for installation at '{Path}'. Is the installation valid?");
            IsParsing = false;
            _notificationHandler?.CloseNotification("ETS2LA.Game.Parsing");
            return;
        }

        Logger.Success($"Finished parsing installation at '{Path}'");
        Logger.Success($"Found {prefabs} prefabs, {roads} roads and {nodes} nodes.");
        IsParsed = true;
        IsParsing = false;
        _notificationHandler?.CloseNotification("ETS2LA.Game.Parsing");
        _notificationHandler?.SendNotification(new Notification
        {
            Id = "ETS2LA.Game.Parsing.Complete",
            Title = "Map Data Parsed",
            Content = $"Found {prefabs} prefabs, {roads} roads and {nodes} nodes.",
            IsProgressIndeterminate = false,
            CloseAfter = 5
        });
    }
}