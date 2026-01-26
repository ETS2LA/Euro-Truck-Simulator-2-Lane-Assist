using Avalonia.Controls;
using ETS2LA.Logging;
using ETS2LA.Settings;
using JetBrains.Annotations;
using SharpDX.DirectInput;

namespace ETS2LA.Controls;

public class ControlHandler
{
    private static readonly Lazy<ControlHandler> _instance = new(() => new ControlHandler());
    public static ControlHandler Current => _instance.Value;

    private List<ControlInstance> RegisteredControls { get; } = new();
    private SettingsHandler _settingsHandler = new SettingsHandler();
    private string _settingsPath = "Controls/";

    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    // Connected devices is public so other plugins that need it
    // don't have to re-initialize DirectInput and query devices again.
    public List<Joystick> _connectedJoysticks = new();
    private DirectInput _directInput = new DirectInput();
    private Keyboard _keyboard;

    public ControlHandler()
    {
        _keyboard = new Keyboard(_directInput);
        _keyboard.Properties.BufferSize = 16;
        _keyboard.Acquire();

        // TODO: Gotta make this update as we go, rather than once at start.
        var devices = _directInput.GetDevices(DeviceClass.GameControl, DeviceEnumerationFlags.AttachedOnly);
        foreach (var device in devices)
        {
            var joystick = new Joystick(_directInput, device.InstanceGuid);
            joystick.Properties.BufferSize = 16;
            joystick.Acquire();
            _connectedJoysticks.Add(joystick);
            Logger.Info($"Connected joystick: [bold]{device.InstanceName}[/] [gray italic]({device.InstanceGuid})[/]");
        }

        Task.Run(() => ControlListener());
    }

    public void RegisterControl(ControlDefinition definition)
    {
        var instance = new ControlInstance
        {
            Definition = definition,
            DeviceId = "",
            ControlId = ""
        };
        instance.LoadFromFile(_settingsHandler, _settingsPath);
        if (!instance.IsBound() && definition.DefaultKeybind != "")
        {
            instance.DeviceId = "Keyboard";
            instance.ControlId = definition.DefaultKeybind;
            instance.SaveToFile(_settingsHandler, _settingsPath);
        }

        RegisteredControls.Add(instance);
        ControlAdded?.Invoke(this, new ControlAddedEventArgs(instance));
        Logger.Info($"Registered control: {definition.Name} [gray italic]({definition.Id})[/]");
    }

    public void On(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for event subscription.");
            return;
        }
        control.RegisterCallback(callback);
    }

    public void UnregisterListener(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for event unsubscription.");
            return;
        }
        ControlRemoved?.Invoke(this, new ControlRemovedEventArgs(control));
        control.UnregisterCallback(callback);
    }

    public void UnregisterControl(string controlId)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control != null)
        {
            control.SaveToFile(_settingsHandler, _settingsPath);
            RegisteredControls.Remove(control);
            Logger.Info($"Unregistered control: {control.Definition.Name} ({control.Definition.Id})");
        }
        else
        {
            Logger.Warn($"Control with ID '{controlId}' not found for unregistration.");
        }
    }

    public List<ControlInstance> GetRegisteredControls()
    {
        return RegisteredControls;
    }

    public void Shutdown()
    {
        foreach (var control in RegisteredControls)
        {
            control.SaveToFile(_settingsHandler, _settingsPath);
        }
        RegisteredControls.Clear();
        Logger.Info("ControlHandler shutdown complete, all controls saved.");
    }

    private string GetIdFromOffset(JoystickOffset offset)
    {
        // Handle Buttons
        if (offset >= JoystickOffset.Buttons0 && offset <= JoystickOffset.Buttons127)
        {
            return "B" + (offset - JoystickOffset.Buttons0);
        }

        // Handle Axes
        return offset switch
        {
            JoystickOffset.X => "X",
            JoystickOffset.Y => "Y",
            JoystickOffset.Z => "Z",
            JoystickOffset.RotationX => "RotationX",
            JoystickOffset.RotationY => "RotationY",
            JoystickOffset.RotationZ => "RotationZ",
            JoystickOffset.Sliders0 => "Slider1",
            JoystickOffset.Sliders1 => "Slider2",
            _ => string.Empty
        };
    }

    private float NormalizeAxisValue(float rawValue, AxisType axisType)
    {
        return axisType switch
        {
            AxisType.Normal => rawValue,
            AxisType.Centered => (rawValue - 0.5f) * 2.0f,
            AxisType.Inverted => 1.0f - rawValue,
            AxisType.SplitNeg => Math.Clamp((0.5f - rawValue) * 2.0f, 0.0f, 1.0f),
            AxisType.SplitPos => Math.Clamp((rawValue - 0.5f) * 2.0f, 0.0f, 1.0f),
            _ => rawValue,
        };
    }

    private void ControlListener()
    {
        while (true)
        {
            var kbBuffer = _keyboard.GetBufferedData();
            foreach (var keyEvent in kbBuffer)
            {
                string hardwareId = ((Key)keyEvent.Key).ToString();
                var matchingControls = RegisteredControls.Where(c => 
                    c.DeviceId == "Keyboard" && 
                    c.ControlId.ToString() == hardwareId);

                foreach (var control in matchingControls)
                {
                    bool isPressed = keyEvent.Value != 0;
                    control.UpdateState(isPressed);
                }
            }

            foreach (var joystick in _connectedJoysticks)
            {
                joystick.Poll();
                var data = joystick.GetBufferedData();

                foreach (var update in data)
                {
                    string hardwareId = GetIdFromOffset(update.Offset);
                    if (string.IsNullOrEmpty(hardwareId)) continue;

                    var matchingControls = RegisteredControls.Where(c => 
                        c.DeviceId == joystick.Information.InstanceGuid.ToString() && 
                        c.ControlId.ToString() == hardwareId);

                    foreach (var control in matchingControls)
                    {
                        if (update.Offset >= JoystickOffset.Buttons0 && update.Offset <= JoystickOffset.Buttons127)
                        {
                            // Value is 128 for pressed, 0 for released (for whatever reason...)
                            control.UpdateState(update.Value == 128);
                        }
                        else
                        {
                            // SharpDX axis values go from 0 to 65535
                            // (luckily that stays constant across devices)
                            float normalizedValue = NormalizeAxisValue(update.Value / 65535.0f, control.AxisBehavior);
                            control.UpdateState(normalizedValue);
                        }
                    }
                }
            }

            // Sleep for 20ms -> ~50 updates per second
            Thread.Sleep(20);
        }
    }
}