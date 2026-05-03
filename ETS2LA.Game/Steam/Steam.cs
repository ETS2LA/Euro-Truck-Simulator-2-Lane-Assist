#if WINDOWS
using Microsoft.Win32;
#endif

namespace ETS2LA.Game.Steam;

// TODO: Switch from names to IDs. Those are stored in libraryfolders.vdf directly.

/// <summary>
///  This class is used by ETS2LA to discover and manage Steam library folders.
///  We use it to find all ETS2 and ATS installations automatically.
/// </summary>
class SteamHandler
{
    /// <summary>
    ///  Gets the path of the current libraryfolders.vdf file.
    ///  This file includes information about where Steam games are installed.
    /// </summary>
    /// <returns>Location of libraryfolders.vdf.</returns>
    public static string GetLibraryVdfPath()
    {
        #if WINDOWS
            string steamInstallFolder = Registry.GetValue(@"HKEY_CURRENT_USER\SOFTWARE\Valve\Steam", "SteamPath", null) as string ?? "C:\\Program Files (x86)\\Steam";
            return Path.Combine(steamInstallFolder, "steamapps", "libraryfolders.vdf");
        #else
            return Path.Combine(Environment.GetEnvironmentVariable("HOME"), ".steam", "root", "steamapps", "libraryfolders.vdf");
        #endif
    }

    /// <summary>
    ///  Gets a list of all current steam library folders.
    ///  This includes both default and user added libraries.
    /// </summary>
    /// <returns>Libraries as a string List.</returns>
    public static List<string> GetLibraryFolders()
    {
        string vdfPath = GetLibraryVdfPath();
        if (!File.Exists(vdfPath))
            return new List<string>();

        List<string> libraryFolders = new();
        foreach (string line in File.ReadAllLines(vdfPath))
        {
            # if WINDOWS
                if (line.Trim().StartsWith("\"") && line.Contains("\"path\""))
                {
                    string path = line.Split('"')[3];
                    libraryFolders.Add(Path.Combine(path, "steamapps", "common"));
                }
            # else
                if (line.Contains("\"path\""))
                {
                    string path = line.Split('"')[3];
                    libraryFolders.Add(Path.Combine(path, "steamapps", "common"));
                }
            #endif
        }

        return libraryFolders;
    }

    /// <summary>
    ///  Finds the specified games in all library folders. Game names
    ///  should be the names of the game folder.
    /// </summary>
    /// <param name="gameNames">List of games to search for.</param>
    /// <returns>List of found game paths.</returns>
    public static List<string> FindGamesInLibraries(List<string> gameNames)
    {
        List<string> foundGames = new();
        List<string> libraryFolders = GetLibraryFolders();

        foreach (string library in libraryFolders)
        {
            foreach (string gameName in gameNames)
            {
                string gamePath = Path.Combine(library, gameName);
                if (Directory.Exists(gamePath))
                {
                    foundGames.Add(gamePath);
                }
            }
        }

        return foundGames;
    }
}