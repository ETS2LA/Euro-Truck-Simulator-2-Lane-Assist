// TODO: Refactor ETS2LA.Game data loading.
//       Currently it's not up to the standards I want.

#if WINDOWS
using Microsoft.Win32;
using System.Diagnostics;
#endif

using ETS2LA.Logging;
using ETS2LA.Game.SDK;
using ETS2LA.Game.Steam;
using ETS2LA.Game.Output;
using ETS2LA.Shared;


namespace ETS2LA.Game;

public class GameHandler
{
    private static readonly Lazy<GameHandler> _instance = new(() => new GameHandler());
    public static GameHandler Current => _instance.Value;
    
    public List<Installation> Installations { get; } = new();

    public GameHandler()
    {
        PopulateInstallations();

        // Spawn all the SDK readers. They'll start
        // sending out events as they read the game.
        var camera = CameraProvider.Current;
        var navigation = NavigationProvider.Current;
        var semaphores = SemaphoreProvider.Current;
        var traffic = TrafficProvider.Current;

        // Spawn the game output handler as well.
        var output = GameOutput.Current;
    }

    private void PopulateInstallations()
    {
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

            string executablePath = Path.Combine(
                # if WINDOWS
                    gamePath, 
                    "bin", 
                    "win_x64", 
                    type == GameType.EuroTruckSimulator2 ? "eurotrucks2.exe" 
                                                         : "amtrucks.exe"
                # else
                    gamePath, 
                    "bin", 
                    "linux_x64", 
                    type == GameType.EuroTruckSimulator2 ? "eurotrucks2" 
                                                         : "amtrucks"
                # endif
            );

            string gameName = type == GameType.EuroTruckSimulator2 ? "Euro Truck Simulator 2" 
                                                                   : "American Truck Simulator";
            string documentsPath = Path.Combine(
                #if WINDOWS
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), 
                    gameName
                #else
                    Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    ".local", "share", gameName
                #endif
            );

            Installations.Add(new Installation
            {
                Type = type,
                Path = gamePath,
                DocumentsPath = documentsPath,
                ExecutablePath = executablePath,
            });

            Installation installation = Installations[^1];
        });
    }
}