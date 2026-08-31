using ETS2LA.Logging;
using ETS2LA.Settings;
using static ETS2LA.Translations.T;

using Velopack;
using Velopack.Sources;

namespace ETS2LA.Networking.Updates;

// NOTE FOR FUTURE DEV:
// ETS2LA itself is only "officially" hosted on GitHub, however if you want to support a 3rd party host
// (like those in China), then take a look at Velopack's documentation here for custom sources. You can
// add your sources in a file in this folder.
// https://docs.velopack.io/integrating/overview#configuring-updates
public class Updater
{
    private const string FallbackSource = "GitHub";
    // This is used to determine the default source for updates. It's set at build time 
    // and bundled with the application. If it's missing we fallback to the FallbackSource.
    private const string DistributionSourceFile = "Assets/DistributionSource.txt";

    private static readonly Lazy<Updater> _instance = new(() => new Updater());
    public static Updater Current => _instance.Value;

    public static string[] AvailableChannels => new string[] { "release", "nightly" };

    public UpdateManager UpdateManager;
    private UpdaterSettings settings = new();
    private UpdateInfo? latestUpdateInfo;
    private string latestUpdateInfoChannel;
    
    public List<UpdaterSource> AvailableSources => new()
    {
        new UpdaterSource(
            new GithubSource("https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist", null, true),
            "GitHub"
        ),
        new UpdaterSource(
            new SimpleWebSource("https://cnb.cool/ETS2LA-CN/Euro-Truck-Simulator-2-Lane-Assist/-/releases/latest/download/"),
            "CNB"
        )
    };

    public Updater()
    {
        settings = UpdaterSettings.Current;
        UpdateManager = CreateUpdateManager(GetSelectedSource().source);
    }

    public UpdateInfo? CheckForUpdates()
    {
        if (latestUpdateInfo != null && latestUpdateInfoChannel == settings.SelectedChannel)
        {
            Logger.Info(_("Update check skipped, using already cached result."));
            return latestUpdateInfo;
        }

        try
        {
            var updateInfo = UpdateManager.CheckForUpdates();
            if (updateInfo != null) { Logger.Info(_("Update available: {0}", updateInfo.TargetFullRelease.Version)); }
            else { Logger.Info(_("No updates available.")); }
            latestUpdateInfo = updateInfo;
            return updateInfo;
        }
        catch (Exception ex)
        {
            Logger.Error(_("Error while checking for updates: {0}", ex.Message));
            return null;
        }
    }

    public void DownloadUpdates(UpdateInfo updateInfo, Action<int>? progressCallback = null)
    {
        try
        {
            UpdateManager.DownloadUpdates(updateInfo, progressCallback);
        }
        catch (Exception ex)
        {
            Logger.Error(_("Error while downloading update: {0}", ex.Message));
        }
    }

    public bool ApplyUpdatesAndRestart(UpdateInfo updateInfo)
    {
        try
        {
            UpdateManager.ApplyUpdatesAndRestart(updateInfo);
            return true;
        }
        catch (Exception ex)
        {
            Logger.Error(_("Error while applying update: {0}", ex.Message));
        }
        return false;
    }

    public void ChangeSource(string sourceName)
    {
        var source = AvailableSources.FirstOrDefault(s => s.sourceName == sourceName);
        if (source == null)
        {
            Logger.Error(_("Tried to change update source to '{0}', but it was not found among available sources.", sourceName));
            return;
        }
        
        settings.SelectedSource = sourceName;
        settings.IsSourceSelectedByUser = true;
        settings.Save();

        UpdateManager = CreateUpdateManager(source.source);
        latestUpdateInfo = null;
        Logger.Info(_("Changed update source to '{0}'.", sourceName));
    }

    public string GetSelectedChannelName()
    {
        #if WINDOWS
        return "win-" + settings.SelectedChannel;
        #else
        return "linux-" + settings.SelectedChannel;
        #endif
    }

    public UpdaterSource GetSelectedSource()
    {
        var selectedSource = settings.IsSourceSelectedByUser && !string.IsNullOrWhiteSpace(settings.SelectedSource)
            ? settings.SelectedSource
            : GetBundledDefaultSourceName();

        var source = AvailableSources.FirstOrDefault(s => s.sourceName == selectedSource);
        if (source == null)
        {
            Logger.Warn(_("Selected update source '{0}' not found, defaulting to first available source.", selectedSource));
            source = AvailableSources[0];
            settings.SelectedSource = source.sourceName;
            Logger.Warn($"> '{source.sourceName}'.");
        }
        return source;
    }

    private UpdateManager CreateUpdateManager(IUpdateSource source)
    {
        UpdateOptions options = new UpdateOptions();
        options.AllowVersionDowngrade = true;
        options.ExplicitChannel = GetSelectedChannelName();

        return new UpdateManager(source, options);
    }

    private string GetBundledDefaultSourceName()
    {
        var sourceFile = Path.Combine(AppContext.BaseDirectory, DistributionSourceFile);
        if (!File.Exists(sourceFile))
        {
            settings.SelectedSource = FallbackSource;
            return FallbackSource;
        }

        try
        {
            var sourceName = File.ReadAllText(sourceFile).Trim();
            settings.SelectedSource = string.IsNullOrWhiteSpace(sourceName) ? FallbackSource : sourceName;
            return settings.SelectedSource;
        }
        catch (Exception ex)
        {
            Logger.Warn(_("Failed to read bundled update source marker: {0}", ex.Message));
            settings.SelectedSource = FallbackSource;
            return FallbackSource;
        }
    }
}