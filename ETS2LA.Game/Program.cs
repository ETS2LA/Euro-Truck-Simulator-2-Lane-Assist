using ETS2LA.Logging;
using ETS2LA.Game.Steam;
using ETS2LA.Shared;
using System.Diagnostics;

namespace ETS2LA.Game;

public class GameHandler
{
    private static readonly Lazy<GameHandler> _instance = new(() => new GameHandler());
    public static GameHandler Instance => _instance.Value;
    
    public List<Installation> Installations { get; } = new();
    private INotificationHandler? window;

    public GameHandler(INotificationHandler? appWindow = null)
    {
        window = appWindow;
        FindInstallations();
    }

    public void SetWindow(INotificationHandler appWindow)
    {
        window = appWindow;
        foreach (var installation in Installations)
        {
            installation.Window = window;
        }
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