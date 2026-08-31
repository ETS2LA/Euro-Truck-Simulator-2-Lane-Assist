using ETS2LA.Logging;
using ETS2LA.Settings;
using ETS2LA.Controls.Defaults;
using static ETS2LA.Translations.T;

using SharpDX.DirectInput;

namespace ETS2LA.Controls.Windows;

enum HatPosition
{
    None,
    Up,
    Right,
    Down,
    Left
}

public class SharpDXControlsBackend : IControlsBackend
{
    private static readonly Lazy<SharpDXControlsBackend> _instance = new(() => new SharpDXControlsBackend());
    public static SharpDXControlsBackend Current => _instance.Value;

    private List<ControlInstance> RegisteredControls { get; } = new();
    private SettingsHandler _settingsHandler = new SettingsHandler();
    private string _settingsPath = "Controls/";

    public event EventHandler<ControlChangeEventArgs>? ControlValueChanged;
    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    private bool pauseListener = false;
    private const int AxisMoveThreshold = 16384;
    private const int PovHatDiff = 9000; // 0 - up, 9000 - right, etc...

    /// <summary>
    ///  You can access connected joysticks through this list. It is preferred <br/>
    ///  that you use this list instead of discovering new DI devices again.
    /// </summary>
    public List<Joystick> _connectedJoysticks = new();
    public Dictionary<Joystick, List<JoystickUpdate>> _previousStates = new();
    private DirectInput _directInput = new DirectInput();
    private Keyboard _keyboard;

    public SharpDXControlsBackend()
    {
        _keyboard = new Keyboard(_directInput);
        _keyboard.Properties.BufferSize = 16;
        _keyboard.Acquire();

        RefreshConnectedJoysticks();

        Task.Factory.StartNew(ControlListener, TaskCreationOptions.LongRunning);
        RegisterControl(DefaultControls.Increase); // RES
        RegisterControl(DefaultControls.Decrease); // SET
        RegisterControl(DefaultControls.Cancel); // MODE
        RegisterControl(DefaultControls.Next);
    }

    private void RefreshConnectedJoysticks()
    {
        var attachedGuids = _directInput
            .GetDevices(DeviceClass.GameControl, DeviceEnumerationFlags.AttachedOnly)
            .Select(device => device.InstanceGuid)
            .ToHashSet();

        var currentByGuid = new Dictionary<Guid, Joystick>();
        foreach (var joystick in _connectedJoysticks)
        {
            try { currentByGuid[joystick.Information.InstanceGuid] = joystick; }
            catch { }
        }

        var currentGuids = currentByGuid.Keys.ToHashSet();
        if (attachedGuids.SetEquals(currentGuids))
            return;

        var updated = new List<Joystick>();

        foreach (var (guid, joystick) in currentByGuid)
        {
            if (attachedGuids.Contains(guid))
            {
                updated.Add(joystick);
            }
            else
            {
                Logger.Info(_("Disconnected joystick: [gray italic]({0})[/]", guid));
                try { joystick.Unacquire(); } catch { }
            }
        }

        foreach (var guid in attachedGuids)
        {
            if (currentGuids.Contains(guid))
                continue;

            try
            {
                var joystick = new Joystick(_directInput, guid);
                joystick.Properties.BufferSize = 16;
                joystick.Acquire();
                updated.Add(joystick);
                Logger.Info(_("Connected joystick: [bold]{0}[/] [gray italic]({1})[/]", joystick.Information.InstanceName, guid));
            }
            catch (Exception ex)
            {
                Logger.Warn(_("Failed to acquire joystick [gray italic]({0})[/]: {1}", guid, ex.Message));
            }
        }

        _connectedJoysticks = updated;
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
        Logger.Info(_("Registered control: {0} [gray italic]({1})[/]", definition.Name, definition.Id));
    }

    public void On(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control == null)
        {
            Logger.Warn(_("Control with ID '{0}' not found for event subscription.", controlId));
            return;
        }
        control.RegisterCallback(callback);
    }

    public void UnregisterListener(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control == null)
        {
            Logger.Warn(_("Control with ID '{0}' not found for event unsubscription.", controlId));
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
            Logger.Info(_("Unregistered control: {0} ({1})", control.Definition.Name, control.Definition.Id));
        }
        else
        {
            Logger.Warn(_("Control with ID '{0}' not found for unregistration.", controlId));
        }
    }

    public void UpdateControlBindings(string controlId, string deviceId, string controlKey)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control != null)
        {
            control.DeviceId = deviceId;
            control.ControlId = controlKey;
            control.SaveToFile(_settingsHandler, _settingsPath);
            Logger.Info(_("Updated bindings for control: {0} ({1}) to Device: {2}, Control: {3}", control.Definition.Name, control.Definition.Id, deviceId, controlKey));
        }
        else
        {
            Logger.Warn(_("Control with ID '{0}' not found for updating bindings.", controlId));
        }
    }

    public void UpdateAxisBehavior(string controlId, AxisType behavior)
    {
        var control = RegisteredControls.FirstOrDefault(c => c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        if (control != null)
        {
            control.AxisBehavior = behavior;
            control.SaveToFile(_settingsHandler, _settingsPath);
            Logger.Info(_("Updated axis behavior for control: {0} ({1}) to {2}", control.Definition.Name, control.Definition.Id, behavior));
        }
        else
        {
            Logger.Warn(_("Control with ID '{0}' not found for updating axis behavior.", controlId));
        }
    }

    public List<ControlInstance> GetRegisteredControls()
    {
        return RegisteredControls;
    }

    public InputDeviceInfo? GetInputDeviceInfoById(string deviceId)
    {
        var joystick = _connectedJoysticks.FirstOrDefault(j => j.Information.InstanceGuid.ToString() == deviceId);
        if (joystick != null)
        {
            return new InputDeviceInfo
            {
                Id = deviceId,
                Name = joystick.Information.InstanceName,
                Type = DeviceType.Gamepad
            };
        }
        else if (deviceId == "Keyboard")
        {
            return new InputDeviceInfo
            {
                Id = deviceId,
                Name = "Keyboard",
                Type = DeviceType.Keyboard
            };
        }

        return null;
    }

    public void Shutdown()
    {
        foreach (var control in RegisteredControls)
        {
            control.SaveToFile(_settingsHandler, _settingsPath);
        }
        RegisteredControls.Clear();
        Logger.Info(_("Controls Backend shutdown complete, all controls saved."));
    }

    private string GetIdFromOffset(JoystickOffset offset)
    {
        // Handle Buttons
        if (offset >= JoystickOffset.Buttons0 && offset <= JoystickOffset.Buttons127)
        {
            return "Button " + (offset - JoystickOffset.Buttons0);
        }

        // Handle Axes
        return offset switch
        {
            JoystickOffset.X => "Axis X",
            JoystickOffset.Y => "Axis Y",
            JoystickOffset.Z => "Axis Z",
            JoystickOffset.RotationX => "Axis RotationX",
            JoystickOffset.RotationY => "Axis RotationY",
            JoystickOffset.RotationZ => "Axis RotationZ",
            JoystickOffset.Sliders0 => "Axis Slider1",
            JoystickOffset.Sliders1 => "Axis Slider2",
            JoystickOffset.PointOfViewControllers0 => "Hat 1",
            JoystickOffset.PointOfViewControllers1 => "Hat 2",
            JoystickOffset.PointOfViewControllers2 => "Hat 3",
            JoystickOffset.PointOfViewControllers3 => "Hat 4",
            _ => "Axis " + offset.ToString()
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

    private HatPosition DecodePovHatSwitch(int value)
    {
        if (value == -1) return HatPosition.None;
        if (value < PovHatDiff) return HatPosition.Up;
        if (value < PovHatDiff * 2) return HatPosition.Right;
        if (value < PovHatDiff * 3) return HatPosition.Down;
        return HatPosition.Left;
    }

    private HatPosition DecodeHatIdToValue(string hatId)
    {
        if (hatId.Contains("Up")) return HatPosition.Up;
        if (hatId.Contains("Right")) return HatPosition.Right;
        if (hatId.Contains("Down")) return HatPosition.Down;
        if (hatId.Contains("Left")) return HatPosition.Left;
        return HatPosition.None;
    }

    private void ControlListener()
    {
        var lastDeviceRefresh = DateTime.MinValue;
        while (true)
        {
            if (pauseListener)
            {
                Thread.Sleep(100);
                continue;
            }

            if ((DateTime.Now - lastDeviceRefresh).TotalSeconds >= 2)
            {
                try { RefreshConnectedJoysticks(); }
                catch (Exception ex) { Logger.Warn(_("Failed to refresh joysticks: {0}", ex.Message)); }
                lastDeviceRefresh = DateTime.Now;
            }

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
                    ControlValueChanged?.Invoke(this, new ControlChangeEventArgs(isPressed, control.Definition));
                }
            }

            foreach (var joystick in _connectedJoysticks)
            {
                JoystickUpdate[] data;
                try
                {
                    joystick.Poll();
                    data = joystick.GetBufferedData();
                }
                catch
                {
                    continue;
                }

                foreach (var update in data)
                {
                    string controlId = GetIdFromOffset(update.Offset);
                    if (string.IsNullOrEmpty(controlId)) continue;

                    if (!_previousStates.ContainsKey(joystick))
                    {
                        _previousStates[joystick] = new List<JoystickUpdate>();
                    }

                    bool needsReplace = _previousStates[joystick].Any(u => u.Offset == update.Offset);
                    if (needsReplace) _previousStates[joystick].RemoveAll(u => u.Offset == update.Offset);
                    _previousStates[joystick].Add(update);

                    var matchingControls = RegisteredControls.Where(c => 
                        c.DeviceId == joystick.Information.InstanceGuid.ToString() && 
                        (c.ControlId.ToString()?.StartsWith(controlId) ?? false)
                    );

                    try
                    {
                        foreach (var control in matchingControls)
                        {
                            if (update.Offset >= JoystickOffset.Buttons0 && update.Offset <= JoystickOffset.Buttons127)
                            {
                                // Value is 128 for pressed, 0 for released (for whatever reason...)
                                control.UpdateState(update.Value == 128);
                                ControlValueChanged?.Invoke(this, new ControlChangeEventArgs(update.Value == 128, control.Definition));
                            }
                            else if (update.Offset >= JoystickOffset.PointOfViewControllers0 && update.Offset <= JoystickOffset.PointOfViewControllers3)
                            {
                                var dir = DecodePovHatSwitch(update.Value);
                                control.UpdateState(dir == DecodeHatIdToValue(control.ControlId.ToString()));
                                ControlValueChanged?.Invoke(this, new ControlChangeEventArgs(dir == DecodeHatIdToValue(control.ControlId.ToString()), control.Definition));
                            }
                            else
                            {
                                // SharpDX axis values go from 0 to 65535
                                // (luckily that stays constant across devices)
                                float normalizedValue = NormalizeAxisValue(update.Value / 65535.0f, control.AxisBehavior);
                                control.UpdateState(normalizedValue);
                                ControlValueChanged?.Invoke(this, new ControlChangeEventArgs(normalizedValue, control.Definition));
                            }
                        }
                    } catch {}
                }
            }

            // Sleep for 10ms -> ~100 updates per second
            Thread.Sleep(10);
        }
    }

    public (string, string) WaitForInput(float timeoutSeconds)
    {
        var startTime = DateTime.Now;
        pauseListener = true;
        while ((DateTime.Now - startTime).TotalSeconds < timeoutSeconds)
        {
            var kbBuffer = _keyboard.GetBufferedData();
            if (kbBuffer.Length > 0)
            {
                var keyEvent = kbBuffer[0];
                string controlId = ((Key)keyEvent.Key).ToString();
                pauseListener = false;
                return ("Keyboard", controlId);
            }

            foreach (var joystick in _connectedJoysticks)
            {
                JoystickUpdate[] data;
                try
                {
                    joystick.Poll();
                    data = joystick.GetBufferedData();
                }
                catch
                {
                    continue;
                }

                foreach(var update in data)
                {
                    string controlId = GetIdFromOffset(update.Offset);

                    if (update.Offset >= JoystickOffset.Buttons0 && update.Offset <= JoystickOffset.Buttons127)
                    {
                        pauseListener = false;
                        return (joystick.Information.InstanceGuid.ToString(), controlId);
                    }

                    if (update.Offset >= JoystickOffset.PointOfViewControllers0 && update.Offset <= JoystickOffset.PointOfViewControllers3)
                    {
                        pauseListener = false;
                        return (joystick.Information.InstanceGuid.ToString(), controlId + " " + DecodePovHatSwitch(update.Value).ToString());
                    }

                    if (!_previousStates.ContainsKey(joystick))
                        _previousStates[joystick] = new List<JoystickUpdate>();

                    int restIndex = _previousStates[joystick].FindIndex(u => u.Offset == update.Offset);
                    if (restIndex < 0)
                    {
                        _previousStates[joystick].Add(update);
                        continue;
                    }

                    if (Math.Abs(_previousStates[joystick][restIndex].Value - update.Value) < AxisMoveThreshold)
                    {
                        continue;
                    }

                    pauseListener = false;
                    return (joystick.Information.InstanceGuid.ToString(), controlId);
                }
            }
            Thread.Sleep(20);
        }

        pauseListener = false;
        return ("", "");
    }
}