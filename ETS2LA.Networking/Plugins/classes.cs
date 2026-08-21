// These classes HAVE to be matching with the classes in the backend.
// Do not change them in any way, they're handled by the ETS2LA team!
using ETS2LA.Logging;

namespace ETS2LA.Networking.Plugins;

[Serializable]
public enum Region
{
    Global,
    China
}

[Serializable]
public enum OperatingSystem
{
    Windows,
    Linux,
    MacOS
}

[Serializable]
public enum NetworkPluginTags
{
    Plugin,
    Library,
    AIAssisted,
    OpenSource,
    ClosedSource
}

[Serializable]
public class NetworkPlugin
{
    // Plugin ID, in the format of "author.pluginname.somethingelseifneeded"
    public string Id { get; set; } = string.Empty;

    public string Author { get; set; } = string.Empty; // has to match the db username for the author
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string WebsiteUrl { get; set; } = string.Empty;

    public List<NetworkPluginVersion> Versions { get; set; } = new();
    public List<NetworkPluginTags> Tags { get; set; } = new();

    public NetworkPluginVersion? GetLatestCompatibleVersion(string appVersion, OperatingSystem os)
    {
        var compatibleVersions = Versions
            .Where(v => IsCompatible(Version.Parse(appVersion), v.AppVersion))
            .Where(v => v.SupportedOperatingSystems.Contains(os))
            .OrderByDescending(v => Version.TryParse(v.Version, out var parsed) ? parsed : new Version(0, 0, 0))
            .ToList();
        return compatibleVersions.FirstOrDefault();
    }

    private bool IsCompatible(Version currentVersion, string constraint)
    {
        if (string.IsNullOrEmpty(constraint)) return true;

        switch (constraint)
        {
            case var c when c.StartsWith("*"):
                return true;
            case var c when c.StartsWith("=="):
                return currentVersion.ToString() == constraint.Substring(2);
            case var c when c.StartsWith(">="):
                if (Version.TryParse(constraint.Substring(2), out var minVersion))
                    return currentVersion >= minVersion;
                break;
            case var c when c.StartsWith(">"):
                if (Version.TryParse(constraint.Substring(1), out var minVersion2))
                    return currentVersion > minVersion2;
                break;
            case var c when c.StartsWith("<="):
                if (Version.TryParse(constraint.Substring(2), out var maxVersion))
                    return currentVersion <= maxVersion;
                break;
            case var c when c.StartsWith("<"):
                if (Version.TryParse(constraint.Substring(1), out var maxVersion2))
                    return currentVersion < maxVersion2;
                break;
            default:
                return System.Text.RegularExpressions.Regex.IsMatch(currentVersion.ToString(), constraint);
        }

        return false;
    }

    public bool IsCompatible(NetworkPluginVersion version, string appVersion, OperatingSystem os)
    {
        return IsCompatible(Version.Parse(appVersion), version.AppVersion) && version.SupportedOperatingSystems.Contains(os);
    }
}

[Serializable]
public class NetworkPluginVersion
{
    public string Version { get; set; } = string.Empty;
    public string AppVersion { get; set; } = string.Empty;

    public string Changelog { get; set; } = string.Empty;
    public string DllPath { get; set; } = string.Empty;
    
    public List<string> Dependencies { get; set; } = new(); // Targets other Plugin.Id values
    public List<OperatingSystem> SupportedOperatingSystems { get; set; } = new();
    public Dictionary<Region, string> DownloadUrl { get; set; } = new();
}