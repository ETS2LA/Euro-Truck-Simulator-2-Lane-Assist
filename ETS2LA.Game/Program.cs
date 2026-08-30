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
using static ETS2LA.Translations.T;

using TruckLib.HashFs;

using System.Text;
using System.Text.RegularExpressions;


namespace ETS2LA.Game;

public class GameHandler
{
    private static readonly Lazy<GameHandler> _instance = new(() => new GameHandler());
    public static GameHandler Current => _instance.Value;
    
    // Copy the list whenever its modified so other threads can
    // enum without crashes
    public List<Installation> Installations { get; private set; } = new();

    public GameHandler()
    {
        PopulateInstallations();

        // Spawn all the SDK readers. They'll start
        // sending out events as they read the game.
        var camera = CameraProvider.Current;
        var navigation = NavigationProvider.Current;
        var semaphores = SemaphoreProvider.Current;
        var traffic = TrafficProvider.Current;
        var parkedVehicles = ParkedVehiclesProvider.Current;

        // Spawn the game output handler as well.
        var output = GameOutput.Current;
    }

    private void PopulateInstallations()
    {
        var games = SteamHandler.FindGamesInLibraries(new List<string>
        {
            SteamHandler.EuroTruckSimulator2AppId,
            SteamHandler.AmericanTruckSimulatorAppId
        });

        Logger.Info(_n("Found {0} game installation.", "Found {0} game installations.", games.Count, games.Count));
        foreach ((string appId, string gamePath) in games)
        {
            GameType type = appId == SteamHandler.EuroTruckSimulator2AppId
                            ? GameType.EuroTruckSimulator2
                            : GameType.AmericanTruckSimulator;

            CreateInstallation(type, gamePath, isManual: false);
        }

        foreach (string gamePath in GameSettings.Current.ManualGamePaths)
        {
            GameType? type = DetectGameType(gamePath);
            if (type == null)
            {
                Logger.Warn(_("Manually added game at '{0}' no longer contains a game executable, skipping.", gamePath));
                continue;
            }

            CreateInstallation(type.Value, gamePath, isManual: true);
        }
    }

    private static string GetExecutablePath(string gamePath, GameType type)
    {
        return Path.Combine(
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
    }

    /// <summary>Checks which game executable exists in the folder, null if neither.</summary>
    public static GameType? DetectGameType(string gamePath)
    {
        if (File.Exists(GetExecutablePath(gamePath, GameType.EuroTruckSimulator2)))
            return GameType.EuroTruckSimulator2;
        if (File.Exists(GetExecutablePath(gamePath, GameType.AmericanTruckSimulator)))
            return GameType.AmericanTruckSimulator;
        return null;
    }

    /// <summary>Builds an installation for the folder and adds it to the list, skipping duplicates.</summary>
    private Installation CreateInstallation(GameType type, string gamePath, bool isManual)
    {
        Installation? existing = Installations.FirstOrDefault(
            i => Path.GetFullPath(i.Path) == Path.GetFullPath(gamePath));
        if (existing != null)
            return existing;

        string executablePath = GetExecutablePath(gamePath, type);
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

        string version = "Unknown";
        # if WINDOWS
            try
            {
                FileVersionInfo info = FileVersionInfo.GetVersionInfo(executablePath);
                version = info.FileVersion != null ? (info.FileVersion.Split(".")[0] + "." + info.FileVersion.Split(".")[1]) : version;
            }
            catch (FileNotFoundException ex)
            {
                Logger.Warn(_("Executable not found at '{0}': {1}", executablePath, ex.Message));
            }
        # endif

        if (version == "Unknown")
            version = GetVersionFromGameFiles(gamePath)
                      ?? GetVersionFromLogs(documentsPath)
                      ?? version;

        // TRANSLATORS: Example: Found Euro Truck Simulator 2 (version: 1.45) at 'C:\Games\ETS2'
        Logger.Info(_("Found {0} (version: {1}) at '{2}'", gameName, version, gamePath));

        Installation installation = new Installation
        {
            Type = type,
            Path = gamePath,
            DocumentsPath = documentsPath,
            ExecutablePath = executablePath,
            Version = version,
            IsManuallyAdded = isManual
        };

        Installations = new List<Installation>(Installations) { installation };
        return installation;
    }

    /// <summary>Adds a game installation from a selected folder and remembers
    /// it for future sessions. Returns null if the folder doesn't contain a game.</summary>
    public Installation? AddManualInstallation(string gamePath)
    {
        gamePath = Path.TrimEndingDirectorySeparator(gamePath);

        GameType? type = DetectGameType(gamePath);
        if (type == null)
        {
            Logger.Warn(_("No game executable found in '{0}', not adding it as an installation.", gamePath));
            return null;
        }

        Installation installation = CreateInstallation(type.Value, gamePath, isManual: true);

        if (installation.IsManuallyAdded && !GameSettings.Current.ManualGamePaths.Contains(gamePath))
        {
            GameSettings.Current.ManualGamePaths.Add(gamePath);
            GameSettings.Current.Save();
        }

        return installation;
    }

    /// <summary>Removes a manually added installation and forgets it for future sessions.</summary>
    public void RemoveManualInstallation(Installation installation)
    {
        if (!installation.IsManuallyAdded)
            return;

        Logger.Info(_("Removing manually added installation at '{0}'", installation.Path));
        Installations = Installations.Where(i => i != installation).ToList();

        GameSettings.Current.ManualGamePaths.RemoveAll(
            p => Path.GetFullPath(p) == Path.GetFullPath(installation.Path));
        GameSettings.Current.Save();
    }

    /// <summary>Reads the game version from the version.scs archive.</summary>
    private static string? GetVersionFromGameFiles(string gamePath)
    {
        string versionScs = Path.Combine(gamePath, "version.scs");
        if (!File.Exists(versionScs))
            return null;

        try
        {
            using var reader = HashFsReader.Open(versionScs);
            if (reader.EntryExists("/version.sii") != EntryType.File)
                return null;

            string content = Encoding.UTF8.GetString(reader.Extract("/version.sii")[0]);
            Match match = Regex.Match(content, "version:\\s*\"(\\d+\\.\\d+)");
            return match.Success ? match.Groups[1].Value : null;
        }
        catch (Exception ex)
        {
            Logger.Warn(_("Failed to read version from '{0}': {1}", versionScs, ex.Message));
            return null;
        }
    }

    /// <summary>Reads the game version from the game's log file.
    /// Only works if the game has been run at least once.</summary>
    private static string? GetVersionFromLogs(string documentsPath)
    {
        string logFile = Path.Combine(documentsPath, "game.log.txt");
        if (!File.Exists(logFile))
            return null;

        try
        {
            // The game holds the log file open, so allow shared access.
            using var stream = new FileStream(logFile, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var reader = new StreamReader(stream);

            string? line;
            int linesRead = 0;
            while ((line = reader.ReadLine()) != null && linesRead++ < 2000)
            {
                Match match = Regex.Match(line, "init ver\\.(\\d+\\.\\d+)");
                if (match.Success)
                    return match.Groups[1].Value;
            }
        }
        catch (IOException ex)
        {
            Logger.Warn(_("Failed to read version from '{0}': {1}", logFile, ex.Message));
        }

        return null;
    }
}