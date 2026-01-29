using System.Runtime.Serialization;
using ETS2LA.Settings;

namespace ETS2LA.Controls;

public enum ControlType
{
    /// <summary>
    ///  A floating point value, e.g. for axes.
    /// </summary>
    Float,
    /// <summary>
    ///  A boolean value, e.g. for buttons.
    /// </summary>
    Boolean
}

public enum AxisType
{
    Normal,   // 0.0 to 1.0 (e.g., Throttle)
    Centered, // -1.0 to 1.0 (e.g., Steering)
    Inverted, // 1.0 to 0.0 (e.g., some Pedals)
    SplitNeg, // 1.0 to 0.0 for the first half of a combined axis (usually Z for xbox-like controllers)
    SplitPos  // 0.0 to 1.0 for the second half of a combined axis (usually Z for xbox-like controllers)
}

/// <summary>
///  This event is fired when a control is added to the ControlHandler.
/// </summary>
public class ControlAddedEventArgs : EventArgs
{
    public ControlInstance Control;
    public ControlAddedEventArgs(ControlInstance control)
    {
        Control = control;
    }
}

/// <summary>
///  This event is fired when a control is removed from the ControlHandler.
/// </summary>
public class ControlRemovedEventArgs : EventArgs
{
    public ControlInstance Control;
    public ControlRemovedEventArgs(ControlInstance control)
    {
        Control = control;
    }
}

/// <summary>
///  This event is fired when a control's value changes. i.e. button pressed or axis moved.
/// </summary>
public class ControlChangeEventArgs : EventArgs
{
    public object NewValue;
    public ControlChangeEventArgs(object newValue)
    {
        NewValue = newValue;
    }
}

/// <summary>
///  Represents a control definition for plugins.
///  Register these in ControlHandler.Current and use .On to listen for changes.
/// </summary>
public class ControlDefinition
{
    /// <summary>
    ///  This Control's unique identifier. Do not change after releasing
    ///  your plugin!
    /// </summary>
    public required string Id;
    /// <summary>
    ///  The display name of this control, will be shown to the user.
    /// </summary>
    public required string Name;
    /// <summary>
    ///  The description of this control, will be shown to the user.
    /// </summary>
    public required string Description;
    /// <summary>
    ///  A default keybind for this control. <br/>
    ///  **NOTE**: You can only default bind to the keyboard!
    /// </summary>
    public string DefaultKeybind = "";
    /// <summary>
    ///  Whether this control outputs a float value (e.g. for axes) 
    ///  or a boolean value (e.g. for buttons). <br/>
    ///  **NOTE**: Updates are only triggered on value change for booleans!
    /// </summary>
    public ControlType Type { get; set; } = ControlType.Boolean;
}

/// <summary>
///  Represents an internal instance of a control binding. Usually shouldn't be 
///  used directly, and instead through ControlHandler's functions.
/// </summary>
[Serializable]
public class ControlInstance : ISerializable
{
    /// <summary>
    ///  The ID of the device this control is bound to.
    /// </summary>
    public string DeviceId = "";
    /// <summary>
    ///  The ID of the control on the device this is bound to. Button/key/axis where:
    ///  - Buttons start with "B" (e.g. "B0", "B1", ...)
    ///  - Keys are the key name (e.g. "Space", "A", "F1", ...) 
    ///    since they are only used when DeviceId is "keyboard"
    ///  - Axes don't start with anything (e.g. "X", "Y", "Z", "RotationX", "RotationY", ...)
    /// </summary>
    public object ControlId = "";
    /// <summary>
    ///  The definition this control instance is based on.
    /// </summary>
    public required ControlDefinition Definition;
    /// <summary>
    ///  The behavior of this axis, only relevant if bound to an axis.
    /// </summary>
    public AxisType AxisBehavior = AxisType.Normal;
    /// <summary>
    ///  Event fired when this control's value changes.
    /// </summary>
    private event EventHandler<ControlChangeEventArgs>? OnChange;
    private object? _lastValue;

    public void GetObjectData(SerializationInfo info, StreamingContext context)
    {
        info.AddValue(nameof(DeviceId), DeviceId);
        info.AddValue(nameof(ControlId), ControlId);
    }

    public bool IsBound()
    {
        return !string.IsNullOrEmpty(DeviceId) && !string.IsNullOrEmpty(ControlId.ToString());
    }

    public void SaveToFile(SettingsHandler settingsHandler, string rootPath)
    {
        var fileName = Path.Combine(rootPath, $"{Definition.Id}.json");
        settingsHandler.Save(fileName, this);
    }

    public void LoadFromFile(SettingsHandler settingsHandler, string rootPath)
    {
        var fileName = Path.Combine(rootPath, $"{Definition.Id}.json");
        var loaded = settingsHandler.Load<ControlInstance>(fileName);
        DeviceId = loaded.DeviceId;
        ControlId = loaded.ControlId;
        AxisBehavior = loaded.AxisBehavior;
    }

    public void RegisterCallback(EventHandler<ControlChangeEventArgs> callback)
    {
        if (OnChange != null && OnChange.GetInvocationList().Contains(callback))
            return;
            
        OnChange += callback;
    }

    public void UnregisterCallback(EventHandler<ControlChangeEventArgs> callback)
    {
        if (OnChange != null && OnChange.GetInvocationList().Contains(callback))
            OnChange -= callback;
    }

    public void UpdateState(object newValue)
    {
        if (_lastValue != null && _lastValue.Equals(newValue))
            return;

        if (Definition.Type == ControlType.Boolean)
        {
            bool boolValue;
            if (newValue.GetType() == typeof(float))
                boolValue = (float)newValue != 0.0f;
            else
                boolValue = (bool)newValue;

            OnChange?.Invoke(this, new ControlChangeEventArgs(boolValue));
        }
        else
        {
            float floatValue;
            if (newValue.GetType() == typeof(bool))
                floatValue = (bool)newValue ? 1.0f : 0.0f;
            else
                floatValue = (float)newValue;

            OnChange?.Invoke(this, new ControlChangeEventArgs(floatValue));
        }

        _lastValue = newValue;
    }
}