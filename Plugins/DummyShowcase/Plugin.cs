using ETS2LA.Logging;
using ETS2LA.Shared;
using System.Collections.Generic;

namespace DummyShowcase;
public class DemoPlugin : Plugin, IPluginUi
{
    public override PluginInformation Info => new PluginInformation
    {
        Name = "Dummy Showcase",
        Description = "Minimal plugin used to validate the manager UI and plugin loader.",
        AuthorName = "Flavio Giacchetti",
    };

    public override float TickRate => 0.5f;

    public override void OnEnable()
    {
        base.OnEnable();
        Logger.Info("Dummy Showcase plugin enabled.");
    }

    public override void Tick()
    {
        // Publish a simple heartbeat; consumers can subscribe if desired.
        Events.Current.Publish("DummyShowcase.Heartbeat", DateTime.UtcNow);
    }

    public override void OnDisable()
    {
        base.OnDisable();
        Logger.Info("Dummy Showcase plugin disabled.");
    }

    public IEnumerable<PluginPage> RenderPages()
    {
        var body = new UiElement[]
        {
            new UiSection("Demo Controls", "Toggle and adjust sample values.", new UiElement[]
            {
                new UiCheckbox("Enable feature", "Simple checkbox bound to an action.", _isEnabledFlag, "toggle_feature"),
                new UiSlider("Sensitivity", "Adjust a numeric setting.", 0, 10, 1, _sensitivity, "set_sensitivity"),
                new UiButton("Run action", "Triggers a sample action.", "run_action", Emphasized: true),
            }),
            new UiSection("Info", null, new UiElement[]
            {
                new UiText("This page is rendered from the plugin via IPluginUi.", Muted: true),
                new UiCombobox("Mode", "Pick a mode to demonstrate combobox.", _modes, _modeIndex, "set_mode"),
                new UiTable("Recent actions", new []{ "Action", "Value" }, BuildRows())
            })
        };

        yield return new PluginPage("dummy-settings", PluginPageLocation.Settings, "Dummy Showcase", "Sample settings page for the demo plugin.", body);
    }

    public void OnAction(string actionId, object? value)
    {
        switch (actionId)
        {
            case "toggle_feature":
                _isEnabledFlag = value is bool b && b;
                Logger.Info($"Dummy feature toggled: {_isEnabledFlag}");
                break;
            case "set_sensitivity":
                _sensitivity = value is double d ? d : _sensitivity;
                Logger.Info($"Dummy sensitivity set: {_sensitivity}");
                break;
            case "set_mode":
                _modeIndex = value is string s ? _modes.IndexOf(s) : _modeIndex;
                Logger.Info($"Dummy mode set: {_modes[_modeIndex]}");
                break;
            case "run_action":
                Logger.Info("Dummy action executed.");
                _recent.Add(("run_action", DateTime.UtcNow.ToString("T")));
                break;
        }
    }

    private bool _isEnabledFlag = false;
    private double _sensitivity = 5;
    private readonly List<(string action, string value)> _recent = new();
    private readonly List<string> _modes = new() { "Standard", "Power", "Eco" };
    private int _modeIndex = 0;

    private IReadOnlyList<IReadOnlyList<string>> BuildRows()
    {
        return _recent
            .TakeLast(5)
            .Select(r => (IReadOnlyList<string>)new List<string> { r.action, r.value })
            .ToList();
    }
}
