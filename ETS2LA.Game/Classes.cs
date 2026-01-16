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

public class Installation
{
    public required GameType Type { get; set; }
    public required string Path { get; set; }
    public required string ExecutablePath { get; set; }
    public required string Version { get; set; }
    public required INotificationHandler? Window { get; set; }
    public bool IsParsed { get; set; } = false;
    public bool IsParsing { get; set; } = false;
    public List<string> FileExclusions = new List<string>
    {
        "dlc_winter.scs",
    };

    private AssetLoader? _assetLoader = null;
    private Map? _map = null;
    private List<Mod>? _selectedMods = null;

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

    public Map GetMap()
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
            _map = Map.Open(GetMapFilepath(), _assetLoader);
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
        Window?.SendNotification(new Notification
        {
            Id = "ETS2LA.Game.ParseInstallation",
            Title = "Parsing Game Files",
            Content = "Please wait, this process might take up to a few minutes depending on your selected mods.",
            IsProgressIndeterminate = true,
            CloseAfter = 0
        });
        
        GetMap();
        if (_map == null)
        {
            Logger.Error($"Failed to load map for installation at '{Path}'");
            IsParsing = false;
            Window?.CloseNotification("ETS2LA.Game.ParseInstallation");
            return;
        }

        int prefabs = _map.MapItems.Where(x => x.Value is Prefab).ToList().Count;
        int roads = _map.MapItems.Where(x => x.Value is Road).ToList().Count;
        int nodes = _map.Nodes.Count;

        if (prefabs == 0 && roads == 0 && nodes == 0)
        {
            Logger.Warn($"No map data found for installation at '{Path}'. Is the installation valid?");
            IsParsing = false;
            Window?.CloseNotification("ETS2LA.Game.ParseInstallation");
            return;
        }

        Logger.Success($"Finished parsing installation at '{Path}'");
        Logger.Success($"Found {prefabs} prefabs, {roads} roads and {nodes} nodes.");
        IsParsed = true;
        IsParsing = false;
        Window?.CloseNotification("ETS2LA.Game.ParseInstallation");
    }
}