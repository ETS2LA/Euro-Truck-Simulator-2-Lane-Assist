using ETS2LA.Settings;

namespace ETS2LA.ML;

[Serializable]
public class MLSettings
{
    [NonSerialized]
    private static readonly Lazy<MLSettings> _instance = new(() => new MLSettings(loadSettings: true));
    public static MLSettings Current => _instance.Value;

    public bool RenderVisionCameras { get; set; } = false;

    [NonSerialized]
    private SettingsHandler? _settingsHandler;

    public MLSettings(bool loadSettings = false)
    {
        if (loadSettings)
        {
            _settingsHandler = new SettingsHandler();
            var loadedSettings = _settingsHandler.Load<MLSettings>("MLSettings.json");
            if (loadedSettings != null)
            {
                RenderVisionCameras = loadedSettings.RenderVisionCameras;
            }
        }
    }

    public MLSettings() { }

    public void Save()
    {
        _settingsHandler?.Save<MLSettings>("MLSettings.json", this);
    }
}
