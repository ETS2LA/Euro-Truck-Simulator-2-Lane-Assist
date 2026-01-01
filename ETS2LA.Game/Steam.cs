using System;
using ETS2LA.Logging;
using Microsoft.Win32;

namespace ETS2LA.Game.Steam;

class SteamHandler
{
    public static string GetLibraryPath()
    {
        string steamInstallFolder = Registry.GetValue(@"HKEY_CURRENT_USER\SOFTWARE\Valve\Steam", "SteamPath", null) as string ?? "C:\\Program Files (x86)\\Steam";
        return System.IO.Path.Combine(steamInstallFolder, "steamapps", "libraryfolders.vdf");
    }

    public static List<string> GetLibraryFolders()
    {
        string libraryPath = GetLibraryPath();
        if (!System.IO.File.Exists(libraryPath))
        {
            return new List<string>();
        }

        List<string> libraryFolders = new();
        foreach (string line in System.IO.File.ReadAllLines(libraryPath))
        {
            if (line.Trim().StartsWith("\"") && line.Contains("\"path\""))
            {
                string path = line.Split('"')[3];
                libraryFolders.Add(System.IO.Path.Combine(path, "steamapps", "common"));
            }
        }

        return libraryFolders;
    }

    public static List<string> FindGamesInLibraries(List<string> gameNames)
    {
        List<string> foundGames = new();
        List<string> libraryFolders = GetLibraryFolders();

        foreach (string library in libraryFolders)
        {
            foreach (string gameName in gameNames)
            {
                string gamePath = System.IO.Path.Combine(library, gameName);
                if (System.IO.Directory.Exists(gamePath))
                {
                    foundGames.Add(gamePath);
                }
            }
        }

        return foundGames;
    }
}