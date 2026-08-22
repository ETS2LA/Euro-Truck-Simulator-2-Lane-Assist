using Velopack;
using Velopack.Sources;
using ETS2LA.Settings;

namespace ETS2LA.Networking.Updates;

public class UpdaterSource
{
    public IUpdateSource source;
    public string sourceName;

    public UpdaterSource(IUpdateSource source, string sourceName)
    {
        this.source = source;
        this.sourceName = sourceName;
    }
}

[Serializable]
public class UpdaterSettings
{
    public string? SelectedSource { get; set; }
    public bool IsSourceSelectedByUser { get; set; } = false;
    public string SelectedChannel { get; set; } = "release";

    [NonSerialized]
    private static readonly Lazy<UpdaterSettings> _instance = new(() => new UpdaterSettings(loadSettings: true));
    public static UpdaterSettings Current => _instance.Value;

    [NonSerialized]
    private SettingsHandler? _settingsHandler;

    public UpdaterSettings(bool loadSettings = false)
    {
        if (loadSettings)
        {
            _settingsHandler = new SettingsHandler();
            var loadedSettings = _settingsHandler.Load<UpdaterSettings>("UpdaterSettings.json");
            if (loadedSettings != null)
            {
                SelectedSource = loadedSettings.SelectedSource;
                IsSourceSelectedByUser = loadedSettings.IsSourceSelectedByUser;
            }
            _settingsHandler.RegisterListener<UpdaterSettings>("UpdaterSettings.json", OnSettingsChanged);
        }
    }

    public UpdaterSettings() { }

    public void Save()
    {
        _settingsHandler?.Save<UpdaterSettings>("UpdaterSettings.json", this);
    }

    public void OnSettingsChanged(UpdaterSettings newSettings)
    {
        SelectedSource = newSettings.SelectedSource;
        IsSourceSelectedByUser = newSettings.IsSourceSelectedByUser;
    }
}