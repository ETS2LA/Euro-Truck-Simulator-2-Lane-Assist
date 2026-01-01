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

    private TsMapper _mapper = null!;

    public string GetModsPath()
    {
        string gameName = Type == GameType.EuroTruckSimulator2 ? "Euro Truck Simulator 2" : "American Truck Simulator";
        string documentsPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
        return System.IO.Path.Combine(documentsPath, gameName, "mod");
    }

    public TsMapper GetMapper()
    {
        if (_mapper == null)
        {
            _mapper = new TsMapper(Path, new List<Mod>());
        }
        return _mapper;
    }

    public void Parse()
    {
        Logger.Info($"Parsing installation at '{Path}' (version: {Version})");
        GetMapper().Parse(Window);
        Logger.Success($"Finished parsing installation at '{Path}'");
        Logger.Success($"Found {_mapper.Prefabs.Count} prefabs, {_mapper.Roads.Count} roads and {_mapper.Nodes.Count} nodes.");
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
        Installations.First().Parse();
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