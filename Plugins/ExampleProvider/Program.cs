using System;
using ETS2LA.Shared;
using ETS2LA.Settings;

[assembly: PluginInformation("ExampleProvider", "An example data provider plugin.")]
namespace ExampleProvider
{

    [Serializable]
    class MySettings
    {
        public int ExampleValue = 42;
    }

    public class MyProvider : Plugin
    {
        public override float TickRate => 1.0f;
        private MySettings? _settings;
        private SettingsHandler? _settingsHandler;
        private string _settingsFilename = "example_settings.json";

        public override void OnEnable()
        {
            base.OnEnable();

            _settingsHandler = new SettingsHandler();
            _settings = _settingsHandler.Load<MySettings>(_settingsFilename);
            _settingsHandler.RegisterListener<MySettings>(_settingsFilename, OnSettingsChanged);
            Console.WriteLine($"ExampleProvider loaded setting ExampleValue = {_settings.ExampleValue}");
        }

        private void OnSettingsChanged(MySettings data)
        {
            Console.WriteLine($"ExampleProvider detected settings change: ExampleValue = {data.ExampleValue}");
            _settings = data;
        }

        public override void Tick()
        {
            if (_bus == null)
                return;

            _bus.Publish<float>("ExampleProvider.Time", System.DateTime.Now.Microsecond);
        }
    }
}