using ETS2LA.Settings;

namespace ETS2LA.UI.Settings
{
    [Serializable]
    public class UISettings
    {
        public int WindowWidth = 1280;
        public int WindowHeight = 720;
        public int WindowX = 200;
        public int WindowY = 200;
        public string Theme = "System";
        public string AccentColor = "Orange";
    }

    public class UISettingsHandler
    {
        private static readonly Lazy<UISettingsHandler> _instance = new(() => new UISettingsHandler());
        public static UISettingsHandler Instance => _instance.Value;

        private SettingsHandler _settingsHandler;
        private UISettings _settings;

        public UISettingsHandler()
        {
            _settingsHandler = new SettingsHandler();
            _settings = _settingsHandler.Load<UISettings>("UISettings.json");
            _settingsHandler.RegisterListener<UISettings>("UISettings.json", OnSettingsChanged);
        }

        public void Save()
        {
            _settingsHandler.Save<UISettings>("UISettings.json", _settings);
        }

        public UISettings GetSettings()
        {
            return _settings;
        }

        private void OnSettingsChanged(UISettings uISettings)
        {
            _settings = uISettings;
        }
    }
}