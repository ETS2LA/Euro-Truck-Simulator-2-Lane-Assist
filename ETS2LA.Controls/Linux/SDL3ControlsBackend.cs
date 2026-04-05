using ETS2LA.Controls.Defaults;
using ETS2LA.Logging;
using ETS2LA.Settings;
using Hexa.NET.SDL3;

namespace ETS2LA.Controls.Linux;

public class SDL3ControlsBackend : IControlsBackend
{
    private static readonly Lazy<SDL3ControlsBackend> _instance = new(() => new SDL3ControlsBackend());
    public static SDL3ControlsBackend Current => _instance.Value;

    private readonly List<ControlInstance> _registeredControls = new();
    private readonly SettingsHandler _settingsHandler = new();
    private const string SettingsPath = "Controls/";

    private readonly Dictionary<int, SDLJoystickPtr> _openJoysticks = new();
    private readonly Dictionary<int, InputDeviceInfo> _deviceInfos = new();

    private readonly object _sync = new();
    private readonly CancellationTokenSource _cts = new();

    private bool _sdlInitialized;
    private bool _changingBindings;
    private Task? _listenerTask;

    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    public SDL3ControlsBackend()
    {
        try
        {
            var flags = SDLInitFlags.Events | SDLInitFlags.Joystick | SDLInitFlags.Gamepad;
            _sdlInitialized = SDL.Init((uint)flags);
            if (!_sdlInitialized)
            {
                Logger.Warn("Failed to initialize SDL3 input backend.");
            }
            else
            {
                BootstrapConnectedJoysticks();
                _listenerTask = Task.Run(ControlListener, _cts.Token);
            }
        }
        catch (Exception ex)
        {
            Logger.Warn($"Failed to initialize SDL3 controls backend: {ex.Message}");
        }

        RegisterControl(DefaultControls.Assist);
        RegisterControl(DefaultControls.SET);
        RegisterControl(DefaultControls.Next);
        RegisterControl(DefaultControls.Increase);
        RegisterControl(DefaultControls.Decrease);
    }

    public void RegisterControl(ControlDefinition definition)
    {
        var instance = new ControlInstance
        {
            Definition = definition,
            DeviceId = "",
            ControlId = ""
        };

        instance.LoadFromFile(_settingsHandler, SettingsPath);
        if (!instance.IsBound() && !string.IsNullOrEmpty(definition.DefaultKeybind))
        {
            instance.DeviceId = "Keyboard";
            instance.ControlId = definition.DefaultKeybind;
            instance.SaveToFile(_settingsHandler, SettingsPath);
        }

        lock (_sync)
        {
            _registeredControls.Add(instance);
        }

        ControlAdded?.Invoke(this, new ControlAddedEventArgs(instance));
        Logger.Info($"Registered control: {definition.Name} [gray italic]({definition.Id})[/]");
    }

    public void On(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = FindControl(controlId);
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for event subscription.");
            return;
        }

        control.RegisterCallback(callback);
    }

    public void UnregisterListener(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        var control = FindControl(controlId);
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for event unsubscription.");
            return;
        }

        control.UnregisterCallback(callback);
    }

    public void UnregisterControl(string controlId)
    {
        lock (_sync)
        {
            var control = _registeredControls.FirstOrDefault(c =>
                c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));

            if (control == null)
            {
                Logger.Warn($"Control with ID '{controlId}' not found for unregistration.");
                return;
            }

            control.SaveToFile(_settingsHandler, SettingsPath);
            _registeredControls.Remove(control);
            ControlRemoved?.Invoke(this, new ControlRemovedEventArgs(control));
            Logger.Info($"Unregistered control: {control.Definition.Name} ({control.Definition.Id})");
        }
    }

    public void UpdateControlBindings(string controlId, string deviceId, string controlKey)
    {
        var control = FindControl(controlId);
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for updating bindings.");
            return;
        }

        control.DeviceId = deviceId;
        control.ControlId = controlKey;
        control.SaveToFile(_settingsHandler, SettingsPath);
        Logger.Info($"Updated bindings for control: {control.Definition.Name} ({control.Definition.Id}) to Device: {deviceId}, Control: {controlKey}");
    }

    public void UpdateAxisBehavior(string controlId, AxisType behavior)
    {
        var control = FindControl(controlId);
        if (control == null)
        {
            Logger.Warn($"Control with ID '{controlId}' not found for updating axis behavior.");
            return;
        }

        control.AxisBehavior = behavior;
        control.SaveToFile(_settingsHandler, SettingsPath);
        Logger.Info($"Updated axis behavior for control: {control.Definition.Name} ({control.Definition.Id}) to {behavior}");
    }

    public List<ControlInstance> GetRegisteredControls()
    {
        lock (_sync)
        {
            return _registeredControls;
        }
    }

    public InputDeviceInfo? GetInputDeviceInfoById(string deviceId)
    {
        if (deviceId == "Keyboard")
        {
            return new InputDeviceInfo
            {
                Id = "Keyboard",
                Name = "Keyboard",
                Type = DeviceType.Keyboard
            };
        }

        lock (_sync)
        {
            InputDeviceInfo? info;
            foreach (var device in _deviceInfos.Values)
            {
                if (device.Id == deviceId)
                {
                    info = device;
                    return info;
                }
            }
            return null;
        }
    }

    public void Shutdown()
    {
        _cts.Cancel();

        try
        {
            _listenerTask?.Wait(250);
        }
        catch {}

        lock (_sync)
        {
            foreach (var control in _registeredControls)
            {
                control.SaveToFile(_settingsHandler, SettingsPath);
            }

            _registeredControls.Clear();

            foreach (var joystick in _openJoysticks.Values)
            {
                if (!joystick.IsNull)
                {
                    SDL.CloseJoystick(joystick);
                }
            }

            _openJoysticks.Clear();
            _deviceInfos.Clear();
        }

        if (_sdlInitialized)
        {
            var flags = SDLInitFlags.Events | SDLInitFlags.Joystick | SDLInitFlags.Gamepad;
            SDL.QuitSubSystem((uint)flags);
        }

        Logger.Info("Linux controls backend shutdown complete, all controls saved.");
    }

    public (string, string) WaitForInput(float timeoutSeconds)
    {
        if (!_sdlInitialized)
        {
            return ("", "");
        }

        _changingBindings = true;
        var end = DateTime.UtcNow.AddSeconds(timeoutSeconds);

        while (DateTime.UtcNow < end)
        {
            SDL.PumpEvents();

            SDLEvent ev = default;
            while (SDL.PollEvent(ref ev))
            {
                var type = ev.Type;

                if (type == (uint)SDLEventType.KeyDown)
                {
                    _changingBindings = false;
                    return ("Keyboard", ev.Key.Scancode.ToString());
                }

                if (type == (uint)SDLEventType.JoystickButtonDown)
                {
                    InputDeviceInfo info = _deviceInfos.ContainsKey(ev.Jbutton.Which) ? _deviceInfos[ev.Jbutton.Which] : default;
                    if (info.Id == null)
                    {
                        Logger.Warn($"Received input from unknown joystick with instance ID {ev.Jbutton.Which}.");
                        continue;
                    }

                    _changingBindings = false;
                    return (info.Id, $"Button {ev.Jbutton.Button}");
                }

                if (type == (uint)SDLEventType.JoystickHatMotion)
                {
                    InputDeviceInfo info = _deviceInfos.ContainsKey(ev.Jhat.Which) ? _deviceInfos[ev.Jhat.Which] : default;
                    if (info.Id == null)
                    {
                        Logger.Warn($"Received input from unknown joystick with instance ID {ev.Jhat.Which}.");
                        continue;
                    }

                    _changingBindings = false;
                    return (info.Id, $"Hat {ev.Jhat.Hat} {ev.Jhat.Value}");
                }

                if (type == (uint)SDLEventType.JoystickAxisMotion)
                {
                    InputDeviceInfo info = _deviceInfos.ContainsKey(ev.Jaxis.Which) ? _deviceInfos[ev.Jaxis.Which] : default;
                    if (info.Id == null)
                    {
                        Logger.Warn($"Received input from unknown joystick with instance ID {ev.Jaxis.Which}.");
                        continue;
                    }
                    
                    var normalized = NormalizeSdlAxis(ev.Jaxis.Value);
                    if (Math.Abs(normalized) > 0.1f)
                    {
                        _changingBindings = false;
                        return (info.Id, $"Axis {AxisIdFromIndex(ev.Jaxis.Axis)}");
                    }
                }

                if (type == (uint)SDLEventType.JoystickBallMotion)
                {
                    InputDeviceInfo info = _deviceInfos.ContainsKey(ev.Jball.Which) ? _deviceInfos[ev.Jball.Which] : default;
                    if (info.Id == null)
                    {
                        Logger.Warn($"Received input from unknown joystick with instance ID {ev.Jball.Which}.");
                        continue;
                    }

                    var movement = Math.Sqrt(ev.Jball.Xrel * ev.Jball.Xrel + ev.Jball.Yrel * ev.Jball.Yrel);
                    if (movement > 0.1f)
                    {
                        _changingBindings = false;
                        return (info.Id, $"Ball {ev.Jball.Ball}");
                    }
                }

                if (type == (uint)SDLEventType.JoystickAdded)
                {
                    RegisterJoystick(ev.Jdevice.Which);
                }
                else if (type == (uint)SDLEventType.JoystickRemoved)
                {
                    UnregisterJoystick(ev.Jdevice.Which);
                }
            }

            Thread.Sleep(20);
        }

        _changingBindings = false;
        return ("", "");
    }

    private ControlInstance? FindControl(string controlId)
    {
        lock (_sync)
        {
            return _registeredControls.FirstOrDefault(c =>
                c.Definition.Id.Equals(controlId, StringComparison.OrdinalIgnoreCase));
        }
    }

    private void ControlListener()
    {
        while (!_cts.IsCancellationRequested)
        {
            if (!_sdlInitialized || _changingBindings)
            {
                Thread.Sleep(100);
                continue;
            }

            SDL.PumpEvents();

            SDLEvent ev = default;
            while (SDL.PollEvent(ref ev))
            {
                HandleEvent(ev);
            }

            Thread.Sleep(20);
        }
    }

    private void HandleEvent(SDLEvent ev)
    {
        switch (ev.Type)
        {
            case (uint)SDLEventType.KeyDown:
            case (uint)SDLEventType.KeyUp:
            {
                var controlId = ev.Key.Scancode.ToString();
                var isPressed = ev.Type == (uint)SDLEventType.KeyDown && ev.Key.Down != 0;
                UpdateMatchingControls("Keyboard", controlId, isPressed);
                break;
            }

            case (uint)SDLEventType.JoystickButtonDown:
            case (uint)SDLEventType.JoystickButtonUp:
            {
                var instanceId = ev.Jbutton.Which;
                InputDeviceInfo? deviceInfo = _deviceInfos.ContainsKey(instanceId) ? _deviceInfos[instanceId] : null;
                if (deviceInfo == null)
                    break;

                var deviceId = deviceInfo.Id;
                var controlId = $"Button {ev.Jbutton.Button}";
                var pressed = ev.Jbutton.Down != 0;
                UpdateMatchingControls(deviceId, controlId, pressed);
                break;
            }

            case (uint)SDLEventType.JoystickHatMotion:
            {
                var instanceId = ev.Jhat.Which;
                InputDeviceInfo? deviceInfo = _deviceInfos.ContainsKey(instanceId) ? _deviceInfos[instanceId] : null;
                if (deviceInfo == null)
                    break;

                var deviceId = deviceInfo.Id;
                string[] controlIds = [
                    $"Hat {ev.Jhat.Hat} 0",
                    $"Hat {ev.Jhat.Hat} 1",
                    $"Hat {ev.Jhat.Hat} 2",
                    $"Hat {ev.Jhat.Hat} 4",
                    $"Hat {ev.Jhat.Hat} 8"
                ];
                // With hats we have to update all 4 directions separately, as they default to 0 when not active.
                // 0000 = center,
                // 0001 = up,
                // 0010 = right,
                // 0100 = down,
                // 1000 = left
                foreach (var controlId in controlIds)
                {
                    bool isActive = controlId.EndsWith(ev.Jhat.Value.ToString());
                    UpdateMatchingControls(deviceId, controlId, isActive);
                }
                break;
            }

            case (uint)SDLEventType.JoystickAxisMotion:
            {
                var instanceId = ev.Jaxis.Which;
                InputDeviceInfo? deviceInfo = _deviceInfos.ContainsKey(instanceId) ? _deviceInfos[instanceId] : null;
                if (deviceInfo == null)
                    break;
                
                var deviceId = deviceInfo.Id;
                var controlId = $"Axis {AxisIdFromIndex(ev.Jaxis.Axis)}";
                var raw = NormalizeSdlAxis(ev.Jaxis.Value);
                UpdateMatchingControls(deviceId, controlId, raw, true);
                break;
            }

            case (uint)SDLEventType.JoystickBallMotion:
            {
                var instanceId = ev.Jball.Which;
                InputDeviceInfo? deviceInfo = _deviceInfos.ContainsKey(instanceId) ? _deviceInfos[instanceId] : null;
                if (deviceInfo == null)
                    break;

                var deviceId = deviceInfo.Id;
                var controlId = $"Ball {ev.Jball.Ball}";
                var movement = ev.Jball.Xrel + ev.Jball.Yrel;
                UpdateMatchingControls(deviceId, controlId, movement);
                break;
            }

            case (uint)SDLEventType.JoystickAdded:
                RegisterJoystick(ev.Jdevice.Which);
                break;

            case (uint)SDLEventType.JoystickRemoved:
                UnregisterJoystick(ev.Jdevice.Which);
                break;
        }
    }

    private void UpdateMatchingControls(string deviceId, string controlId, object value, bool isAxis = false)
    {
        List<ControlInstance> matches;
        lock (_sync)
        {
            matches = _registeredControls
                .Where(c => c.DeviceId == deviceId && c.ControlId.ToString() == controlId)
                .ToList();
        }

        foreach (var control in matches)
        {
            if (isAxis)
            {
                var v = NormalizeAxisValue((float)value, control.AxisBehavior);
                control.UpdateState(v);
            }
            else
            {
                control.UpdateState(value);
            }
        }
    }

    private void BootstrapConnectedJoysticks()
    {
        if (!_sdlInitialized)
        {
            return;
        }

        // SDL emits JoystickAdded at init, but bootstrap to have device metadata immediately.
        unsafe
        {
            var count = 0;
            var ids = SDL.GetJoysticks(&count);
            if (ids == null)
            {
                return;
            }

            for (var i = 0; i < count; i++)
            {
                RegisterJoystick(ids[i]);
            }

            SDL.Free(ids);
        }
    }

    private void RegisterJoystick(int instanceId)
    {
        lock (_sync)
        {
            if (_openJoysticks.ContainsKey(instanceId))
            {
                return;
            }

            var joystick = SDL.OpenJoystick(instanceId);
            if (joystick.IsNull)
            {
                Logger.Warn($"Failed to open joystick {instanceId}.");
                return;
            }

            _openJoysticks[instanceId] = joystick;

            var type = SDL.GetJoystickTypeForID(instanceId);
            var uid = SDL.GetJoystickGUIDForID(instanceId);
            var deviceType = type == SDLJoystickType.Wheel ? DeviceType.Wheel : DeviceType.Gamepad;

            var name = $"Joystick {uid}";
            try
            {
                if (!joystick.IsNull)
                {
                    name = SDL.GetJoystickNameS(joystick);
                }
            }
            catch
            {
                // keep fallback name
            }

            _deviceInfos[instanceId] = new InputDeviceInfo
            {
                Id = GuidToString(uid),
                Name = string.IsNullOrWhiteSpace(name) ? $"Joystick {uid}" : name,
                Type = deviceType
            };

            Logger.Info($"Connected joystick: [bold]{_deviceInfos[instanceId].Name}[/] [gray italic]({instanceId}, {uid})[/]");
        }
    }

    private void UnregisterJoystick(int instanceId)
    {
        lock (_sync)
        {
            if (_openJoysticks.TryGetValue(instanceId, out var joystick))
            {
                if (!joystick.IsNull)
                {
                    SDL.CloseJoystick(joystick);
                }

                _openJoysticks.Remove(instanceId);
            }

            _deviceInfos.Remove(instanceId);
            Logger.Info($"Disconnected joystick: [gray italic]({instanceId})[/]");
        }
    }

    private static string AxisIdFromIndex(byte axisIndex)
    {
        return axisIndex switch
        {
            0 => "X",
            1 => "Y",
            2 => "Z",
            3 => "RotationX",
            4 => "RotationY",
            5 => "RotationZ",
            6 => "Slider1",
            7 => "Slider2",
            _ => $"{axisIndex}"
        };
    }

    private static float NormalizeSdlAxis(short value)
    {
        // SDL axis range is -32768 - 32767
        var centered = (value + 32768f) / 65535f;
        return Math.Clamp(centered, 0f, 1f);
    }

    private static float NormalizeAxisValue(float rawValue, AxisType axisType)
    {
        return axisType switch
        {
            AxisType.Normal => rawValue,
            AxisType.Centered => (rawValue - 0.5f) * 2.0f,
            AxisType.Inverted => 1.0f - rawValue,
            AxisType.SplitNeg => Math.Clamp((0.5f - rawValue) * 2.0f, 0.0f, 1.0f),
            AxisType.SplitPos => Math.Clamp((rawValue - 0.5f) * 2.0f, 0.0f, 1.0f),
            _ => rawValue
        };
    }

    private static string GuidToString(SdlGuid guid)
    {
        return $"{guid.Data_0:X2}{guid.Data_1:X2}{guid.Data_2:X2}{guid.Data_3:X2}-" +
               $"{guid.Data_4:X2}{guid.Data_5:X2}-" +
               $"{guid.Data_6:X2}{guid.Data_7:X2}-" +
               $"{guid.Data_8:X2}{guid.Data_9:X2}-" +
               $"{guid.Data_10:X2}{guid.Data_11:X2}{guid.Data_12:X2}{guid.Data_13:X2}{guid.Data_14:X2}{guid.Data_15:X2}";
    }
}