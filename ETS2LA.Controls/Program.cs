using System.Collections;

#if WINDOWS
using ETS2LA.Controls.Windows;
#elif LINUX
using ETS2LA.Controls.Linux;
#endif

namespace ETS2LA.Controls;

public class ControlsBackend : IControlsBackend
{
    private static ControlsBackend? _instance;
    public static ControlsBackend Current => _instance ??= new ControlsBackend();

    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    private readonly IControlsBackend _backend;

    public ControlsBackend()
    {
        if (OperatingSystem.IsWindows())
        {
#if WINDOWS
            _backend = SharpDXControlsBackend.Current;
#endif
        }
        else
        {
#if LINUX
            _backend = new SDL3ControlsBackend();
#endif
        }

        _backend.ControlAdded += (s, e) => ControlAdded?.Invoke(this, e);
        _backend.ControlRemoved += (s, e) => ControlRemoved?.Invoke(this, e);
    }

    public void RegisterControl(ControlDefinition definition)
    {
        _backend.RegisterControl(definition);
    }

    public void On(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        _backend.On(controlId, callback);
    }

    public void UnregisterListener(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {
        _backend.UnregisterListener(controlId, callback);
    }

    public void UnregisterControl(string controlId)
    {
        _backend.UnregisterControl(controlId);
    }

    public void UpdateControlBindings(string controlId, string deviceId, string controlKey)
    {
        _backend.UpdateControlBindings(controlId, deviceId, controlKey);
    }

    public void UpdateAxisBehavior(string controlId, AxisType behavior)
    {
        _backend.UpdateAxisBehavior(controlId, behavior);
    }

    public List<ControlInstance> GetRegisteredControls()
    {
        return _backend.GetRegisteredControls();
    }

    public InputDeviceInfo? GetInputDeviceInfoById(string deviceId)
    {
        return _backend.GetInputDeviceInfoById(deviceId);
    }

    public (string, string) WaitForInput(float timeoutSeconds)
    {
        return _backend.WaitForInput(timeoutSeconds);
    }

    public void Shutdown()
    {
        _backend.Shutdown();
    }
}