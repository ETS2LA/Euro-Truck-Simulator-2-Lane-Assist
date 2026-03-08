namespace ETS2LA.Controls.Linux;

public class LinuxControlsBackend : IControlsBackend
{
    private static readonly Lazy<LinuxControlsBackend> _instance = new(() => new LinuxControlsBackend());
    public static LinuxControlsBackend Current => _instance.Value;

    private List<ControlInstance> RegisteredControls { get; } = new();

    public event EventHandler<ControlAddedEventArgs>? ControlAdded;
    public event EventHandler<ControlRemovedEventArgs>? ControlRemoved;

    public LinuxControlsBackend()
    {

    }

    public void RegisterControl(ControlDefinition definition)
    {

    }

    public void On(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {

    }

    public void UnregisterListener(string controlId, EventHandler<ControlChangeEventArgs> callback)
    {

    }

    public void UnregisterControl(string controlId)
    {

    }

    public void UpdateControlBindings(string controlId, string deviceId, string controlKey)
    {

    }

    public void UpdateAxisBehavior(string controlId, AxisType behavior)
    {

    }

    public List<ControlInstance> GetRegisteredControls()
    {
        return RegisteredControls;
    }

    public InputDeviceInfo? GetInputDeviceInfoById(string deviceId)
    {
        return null;
    }

    public void Shutdown()
    {

    }

    public (string, string) WaitForInput(float timeoutSeconds)
    {
        return ("", "");
    }
}