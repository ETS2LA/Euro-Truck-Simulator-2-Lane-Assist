using ETS2LA.Logging;
using ETS2LA.Settings;
using SharpDX.DirectInput;
using ETS2LA.Controls.Defaults;

namespace ETS2LA.Controls;

public class ControlHandler
{
    // When accessing ControlHandler, always use ControlHandler.Current
    private static readonly Lazy<ControlHandler> _instance = new(() => new ControlHandler());
    public static ControlHandler Current => _instance.Value;
    public static DefaultControls Defaults { get; } = new DefaultControls();

    private List<ControlInstance> RegisteredControls { get; } = new();
    private SettingsHandler _settingsHandler = new SettingsHandler();
    private string _settingsPath = "Controls/";

    /// <summary>
    ///  This event is fired when a control is added to the ControlHandler.
    /// </summary>
    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    /// <summary>
    ///  This event is fired when a control is removed from the ControlHandler.
    /// </summary>
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    /// <summary>
    ///  You can access connected joysticks through this list. It is preferred <br/>
    ///  that you use this list instead of discovering new DI devices again.
    /// </summary>
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
        RegisterControl(Defaults.Assist);
        RegisterControl(Defaults.SET);
        RegisterControl(Defaults.Next);
        RegisterControl(Defaults.Increase);
        RegisterControl(Defaults.Decrease);
    }

    /// <summary>
    ///  Register a new control definition to the ControlHandler. <br/>
    ///  After registering you can use ControlHandler.On to listen for changes to this control.
    /// </summary>
    /// <param name="definition">The control definition to register.</param>
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

    /// <summary>
    ///  Listen for changes to a registered control. Please note that the control must be <br/>
    ///  registered first using ControlHandler.RegisterControl, each time the app is launched (use init()).
    /// </summary>
    /// <param name="controlId">The ID of the control to listen to (ControlDefinition.Id).</param>
    /// <param name="callback">The callback to invoke when the control's value changes.</param>
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

    /// <summary>
    ///  Stop listening for changes to a registered control.
    /// </summary>
    /// <param name="controlId">The ID of the control to stop listening to (ControlDefinition.Id).</param>
    /// <param name="callback">The callback to remove.</param>
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

    /// <summary>
    ///  Unregister a control from the ControlHandler. This will also save its current state. <br/>
    ///  **NOTE**: This will remove the control from the settings!
    /// </summary>
    /// <param name="controlId">The ID of the control to unregister (ControlDefinition.Id).</param>
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

    /// <summary>
    ///  Update the bindings for a registered control. This should only ever be called from <br/>
    ///  the settings menu, however plugins can technically use this as well.
    /// </summary>
    /// <param name="controlId">The ID of the control to update (ControlDefinition.Id).</param>
    /// <param name="deviceId">The ID of the device to bind the control to.</param>
    /// <param name="controlKey">The key or axis to bind the control to.</param>
    public void UpdateControlBindings(string controlId, string deviceId, string controlKey)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control != null)
        {
            control.DeviceId = deviceId;
            control.ControlId = controlKey;
            control.SaveToFile(_settingsHandler, _settingsPath);
            Logger.Info($"Updated bindings for control: {control.Definition.Name} ({control.Definition.Id}) to Device: {deviceId}, Control: {controlKey}");
        }
        else
        {
            Logger.Warn($"Control with ID '{controlId}' not found for updating bindings.");
        }
    }

    /// <summary>
    ///  Update the axis behavior for a registered control.
    /// </summary>
    /// <param name="controlId">The ID of the control to update (ControlDefinition.Id).</param>
    /// <param name="axisType">The new axis behavior to set.</param>
    public void UpdateAxisBehaviour(string controlId, AxisType axisType)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control != null)
        {
            control.AxisBehavior = axisType;
            control.SaveToFile(_settingsHandler, _settingsPath);
            Logger.Info($"Updated axis behavior for control: {control.Definition.Name} ({control.Definition.Id}) to {axisType}");
        }
        else
        {
            Logger.Warn($"Control with ID '{controlId}' not found for updating axis behavior.");
        }
    }

    /// <summary>
    ///  Get a list of all registered controls.
    /// </summary>
    /// <returns>A list of all registered control instances.</returns>
    public List<ControlInstance> GetRegisteredControls()
    {
        return RegisteredControls;
    }

    /// <summary>
    ///  Return a joystick instance by its device ID.
    /// </summary>
    /// <param name="deviceId">The device ID of the joystick.</param>
    /// <returns>The joystick instance, or null if not found.</returns>
    public Joystick? GetJoystickById(string deviceId)
    {
        return _connectedJoysticks.FirstOrDefault(j => j.Information.InstanceGuid.ToString() == deviceId);
    }

    /// <summary>
    ///  Shutdown the ControlHandler, saving all control states to their files. <br/>
    ///  **NEVER** call this inside of plugins!
    /// </summary>
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
                string controlId = ((Key)keyEvent.Key).ToString();
                var matchingControls = RegisteredControls.Where(c => 
                    c.DeviceId == "Keyboard" && 
                    c.ControlId.ToString() == controlId);

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
                    string controlId = GetIdFromOffset(update.Offset);
                    if (string.IsNullOrEmpty(controlId)) continue;

                    var matchingControls = RegisteredControls.Where(c => 
                        c.DeviceId == joystick.Information.InstanceGuid.ToString() && 
                        c.ControlId.ToString() == controlId);

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

    /// <summary>
    ///  Waits for an input from any connected device within the specified timeout.
    /// </summary>
    /// <param name="timeoutSeconds">How long to wait for input, in seconds.</param>
    /// <returns>
    ///  A tuple containing the device ID and control ID of the detected input.
    ///  If no input is detected within the timeout, returns ("", "").
    /// </returns>
    public (string, string) WaitForInput(float timeoutSeconds)
    {
        var startTime = DateTime.Now;
        while ((DateTime.Now - startTime).TotalSeconds < timeoutSeconds)
        {
            var kbBuffer = _keyboard.GetBufferedData();
            if (kbBuffer.Length > 0)
            {
                var keyEvent = kbBuffer[0];
                string controlId = ((Key)keyEvent.Key).ToString();
                return ("Keyboard", controlId);
            }

            foreach (var joystick in _connectedJoysticks)
            {
                joystick.Poll();
                var data = joystick.GetBufferedData();
                if (data.Length > 0)
                {
                    var update = data[0];
                    string controlId = GetIdFromOffset(update.Offset);
                    
                    if (update.Offset >= JoystickOffset.Buttons0 && update.Offset <= JoystickOffset.Buttons127)
                    {
                        return (joystick.Information.InstanceGuid.ToString(), controlId);
                    }
                    else
                    {
                        float normalizedValue = NormalizeAxisValue(update.Value / 65535.0f, AxisType.Normal);
                        if(Math.Abs(normalizedValue) > 0.1f)
                        {
                            return (joystick.Information.InstanceGuid.ToString(), controlId);
                        }
                    }
                }
            }
            Thread.Sleep(20);
        }

        return ("", "");
    }
}