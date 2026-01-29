using ETS2LA.Logging;
using ETS2LA.Settings;
using Velopack;
using Velopack.Sources;

namespace ETS2LA.Backend.Updates;

// NOTE FOR FUTURE DEV:
// ETS2LA itself is only "officially" hosted on GitHub, however if you want to support a 3rd party host
// (like those in China), then take a look at Velopack's documentation here for custom sources. You can
// add your sources in a file in this folder.
// https://docs.velopack.io/integrating/overview#configuring-updates
public class Updater
{
    private static readonly Lazy<Updater> _instance = new(() => new Updater());
    public static Updater Current => _instance.Value;

    public UpdateManager UpdateManager;
    private UpdaterSettings _settings = new();
    private SettingsHandler _settingsHandler;
    private UpdateInfo? _latestUpdateInfo;
    public List<UpdaterSource> AvailableSources => new()
    {
        new UpdaterSource(new GithubSource("https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist", null, true), "GitHub")
    };

    public Updater()
    {
        _settingsHandler = new SettingsHandler();
        _settings = _settingsHandler.Load<UpdaterSettings>("Updater.json");
        UpdateManager = new UpdateManager(GetSelectedSource().source, new UpdateOptions
        {
            #if DEBUG
            ExplicitChannel = "win-beta"
            #endif
        });
    }

    public UpdateInfo? CheckForUpdates()
    {
        if (_latestUpdateInfo != null)
        {
            Logger.Info("Update check skipped, using already cached result.");
            return _latestUpdateInfo;
        }

        try
        {
            var updateInfo = UpdateManager.CheckForUpdates();
            if (updateInfo != null) { Logger.Info($"Update available: {updateInfo.TargetFullRelease.Version}"); }
            else { Logger.Info("No updates available."); }
            _latestUpdateInfo = updateInfo;
            return updateInfo;
        }
        catch (Exception ex)
        {
            Logger.Error($"Error while checking for updates: {ex.Message}");
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
            Logger.Error($"Error while downloading update: {ex.Message}");
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
            Logger.Error($"Error while applying update: {ex.Message}");
        }
        return false;
    }

    public void ChangeSource(string sourceName)
    {
        var source = AvailableSources.FirstOrDefault(s => s.sourceName == sourceName);
        if (source == null)
        {
            Logger.Error($"Tried to change update source to '{sourceName}', but it was not found among available sources.");
            return;
        }
        _settings.SelectedSource = sourceName;
        _settingsHandler.Save("Updater.json", _settings);
        UpdateManager = new UpdateManager(source.source);
        Logger.Info($"Changed update source to '{sourceName}'.");
    }

    public UpdaterSource GetSelectedSource()
    {
        var source = AvailableSources.FirstOrDefault(s => s.sourceName == _settings.SelectedSource);
        if (source == null)
        {
            Logger.Warn($"Selected update source '{_settings.SelectedSource}' not found, defaulting to first available source.");
            source = AvailableSources[0];
            Logger.Warn($"> '{source.sourceName}'.");
        }
        return source;
    }
}