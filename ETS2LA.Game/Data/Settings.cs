using ETS2LA.Settings;

namespace ETS2LA.Game.Data;

public enum DataFidelity
{
    Low,
    Medium,
    High,
    Extreme
}

public enum CurveQuality
{
    Low,
    MatchGame,
    High
}

[Serializable]
public class DataSettings
{
    public DataFidelity DataFidelity { get; set; } = DataFidelity.Medium;
    public CurveQuality CurveQuality { get; set; } = CurveQuality.MatchGame;

    [NonSerialized]
    private static readonly Lazy<DataSettings> _instance = new(() => new DataSettings(loadSettings: true));
    public static DataSettings Current => _instance.Value;

    [NonSerialized]
    private SettingsHandler? _settingsHandler;

    public DataSettings(bool loadSettings = false)
    {
        if (loadSettings)
        {
            _settingsHandler = new SettingsHandler();
            var loadedSettings = _settingsHandler.Load<DataSettings>("DataSettings.json");
            if (loadedSettings != null)
            {
                DataFidelity = loadedSettings.DataFidelity;
                CurveQuality = loadedSettings.CurveQuality;
            }
            _settingsHandler.RegisterListener<DataSettings>("DataSettings.json", OnSettingsChanged);
        }
    }

    public DataSettings() { }

    public void Save()
    {
        _settingsHandler?.Save<DataSettings>("DataSettings.json", this);
    }

    public void OnSettingsChanged(DataSettings newSettings)
    {
        DataFidelity = newSettings.DataFidelity;
        CurveQuality = newSettings.CurveQuality;
    }
}