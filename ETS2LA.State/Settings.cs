using ETS2LA.Settings;
using ETS2LA.Translations;

namespace ETS2LA.State;


[Serializable]
public class StateSettings
{
    public Units DisplayUnits = Units.Metric;
    public Language DisplayLanguage = Languages.SupportedLanguages[0];
    public int SpeedControlStepSize = 2;
    public bool SnapTo10s = true;
}

public class StateSettingsHandler
{
    private static readonly Lazy<StateSettingsHandler> _instance = new(() => new StateSettingsHandler());
    public static StateSettingsHandler Current => _instance.Value;

    private SettingsHandler _settingsHandler;
    private StateSettings _settings;

    public event Action<StateSettings> OnSettingsChanged;

    public StateSettingsHandler()
    {
        _settingsHandler = new SettingsHandler();
        _settings = _settingsHandler.Load<StateSettings>("StateSettings.json");
        _settingsHandler.RegisterListener<StateSettings>("StateSettings.json", OnSettingsChangedInternal);
    }

    public void Save()
    {
        _settingsHandler.Save("StateSettings.json", _settings);
    }

    public StateSettings GetSettings()
    {
        return _settings;
    }

    private void OnSettingsChangedInternal(StateSettings stateSettings)
    {
        _settings = stateSettings;
        OnSettingsChanged?.Invoke(_settings);
    }
}
