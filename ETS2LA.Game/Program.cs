using ETS2LA.Logging;
using ETS2LA.Game.Steam;
using ETS2LA.Game.Extractor;
using System.Diagnostics;
using ETS2LA.Shared;

namespace ETS2LA.Game;

public enum GameType
{
    EuroTruckSimulator2,
    AmericanTruckSimulator
}

public class Installation
{
    public required GameType Type { get; set; }
    public required string Path { get; set; }
    public required string ExecutablePath { get; set; }
    public required string Version { get; set; }
    public required INotificationHandler? Window { get; set; }
    public bool IsParsed { get; set; } = false;

    private TsMapper _mapper = null!;
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
        return _selectedMods.Select(m => System.IO.Path.GetFileNameWithoutExtension(m.ModPath)).ToList();
    }

    public List<string> GetAvailableMods()
    {
        string modsPath = GetModsPath();
        if (!System.IO.Directory.Exists(modsPath))
        {
            return new List<string>();
        }

        List<string> mods = new();
        foreach (string file in System.IO.Directory.GetFiles(modsPath, "*.scs"))
        {
            mods.Add(System.IO.Path.GetFileNameWithoutExtension(file));
        }
        return mods;
    }

    public void SetSelectedMods(List<string> mods)
    {
        string modsPath = GetModsPath();
        _selectedMods = mods.Select(m => new Mod(System.IO.Path.Combine(modsPath, m + ".scs")){
            Load = true
        }).ToList();
        Logger.Info($"Selected {_selectedMods.Count} mods for installation at '{Path}'");
    }

    public TsMapper GetMapper()
    {
        if (_mapper == null)
        {
            _mapper = new TsMapper(Path, _selectedMods ?? new List<Mod>());
        }
        return _mapper;
    }

    public void Parse()
    {
        if (IsParsed)
        {
            Logger.Warn($"Installation at '{Path}' has already been parsed.");
            return;
        }

        Logger.Info($"Parsing installation at '{Path}' (version: {Version})");
        GetMapper().Parse(Window);
        if(_mapper.Prefabs.Count == 0)
        {
            Logger.Warn($"No map data found for installation at '{Path}'. Is the installation valid?");
            return;
        }

        Logger.Success($"Finished parsing installation at '{Path}'");
        Logger.Success($"Found {_mapper.Prefabs.Count} prefabs, {_mapper.Roads.Count} roads and {_mapper.Nodes.Count} nodes.");
        IsParsed = true;
    }
}

public class GameHandler
{
    public List<Installation> Installations { get; } = new();
    private INotificationHandler? window;

    public GameHandler(INotificationHandler? appWindow = null)
    {
        window = appWindow;
        FindInstallations();
    }

    private void FindInstallations()
    {
        if (Environment.OSVersion.Platform != PlatformID.Win32NT)
        {
            Logger.Warn("Game installation detection is only supported on Windows.");
            return;
        }

        List<string> games = SteamHandler.FindGamesInLibraries(new List<string>
        {
            "Euro Truck Simulator 2",
            "American Truck Simulator"
        });

        Logger.Info($"Found {games.Count} game installations.");
        games.ForEach(gamePath =>
        {
            GameType type = gamePath.EndsWith("Euro Truck Simulator 2") 
                            ? GameType.EuroTruckSimulator2 
                            : GameType.AmericanTruckSimulator;

            string executablePath = System.IO.Path.Combine(
                gamePath, "bin", "win_x64", type == GameType.EuroTruckSimulator2 
                                            ? "eurotrucks2.exe" 
                                            : "amtrucks.exe"
            );
            
            string version = "Unknown";
            try
            {
                var versionInfo = FileVersionInfo.GetVersionInfo(executablePath);
                version = versionInfo.FileVersion ?? "Unknown";
            }
            catch (Exception) { }

            Installations.Add(new Installation
            {
                Type = type,
                Path = gamePath,
                ExecutablePath = executablePath,
                Version = version,
                Window = window
            });
        });
    }
}