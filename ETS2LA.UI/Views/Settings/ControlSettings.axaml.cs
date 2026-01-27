using System.Collections.ObjectModel;
using System.Runtime.CompilerServices;
using System.ComponentModel;

using Avalonia.Interactivity;
using Avalonia.Controls;
using Avalonia.Input;

using ETS2LA.Controls;
using ETS2LA.Logging;
using ETS2LA.Shared;
using ETS2LA.UI.Notifications;
using Huskui.Avalonia.Models;

namespace ETS2LA.UI.Views.Settings;

public partial class ControlSettings : UserControl
{
    public ObservableCollection<ControlItem> Controls { get; } = new();
    private readonly ControlHandler _cHandler = ControlHandler.Current;

    public ControlSettings()
    {
        InitializeComponent();
        DataContext = this;
        UpdateControlsList();
        _cHandler.ControlAdded += OnControlAdded;
        _cHandler.ControlRemoved += OnControlRemoved;
    }

    private void OnControlAdded(object? sender, ControlAddedEventArgs e)
    {
        UpdateControlsList();
    }

    private void OnControlRemoved(object? sender, ControlRemovedEventArgs e)
    {
        UpdateControlsList();
    }

    private void UpdateControlsList()
    {
        Controls.Clear();
        List<ControlInstance> controlInstances = _cHandler.GetRegisteredControls();
        foreach (var instance in controlInstances)
        {
            Controls.Add(new ControlItem(instance, _cHandler));
        }
    }

    // Called when a user clicks the control card to rebind it.
    private void OnTriggerChange(object? sender, RoutedEventArgs e)
    {
        if (e is not PointerPressedEventArgs)
            return;

        var pointerEvent = (PointerPressedEventArgs)e;
        if (!pointerEvent.Properties.IsLeftButtonPressed)
            return;

        if (sender is Control { Tag: ControlItem item })
        {
            Task.Run(() => item.TriggerChange());
        }
    }

    // These are called when the user selects an axis type from the context menu.
    // TODO: Someone who knows more about Avalonia can probably make this cleaner.
    private void OnAxisTypeNormalClick(object? sender, RoutedEventArgs e)
    {
        if (sender is MenuItem { Tag: ControlItem item })
        {
            item.OnAxisTypeChanged(AxisType.Normal);
        }
    }

    private void OnAxisTypeCenteredClick(object? sender, RoutedEventArgs e)
    {
        if (sender is MenuItem { Tag: ControlItem item })
        {
            item.OnAxisTypeChanged(AxisType.Centered);
        }
    }

    private void OnAxisTypeInvertedClick(object? sender, RoutedEventArgs e)
    {
        if (sender is MenuItem { Tag: ControlItem item })
        {
            item.OnAxisTypeChanged(AxisType.Inverted);
        }
    }

    private void OnAxisTypeSplitNegativeClick(object? sender, RoutedEventArgs e)
    {
        if (sender is MenuItem { Tag: ControlItem item })
        {
            item.OnAxisTypeChanged(AxisType.SplitNeg);
        }
    }

    private void OnAxisTypeSplitPositiveClick(object? sender, RoutedEventArgs e)
    {
        if (sender is MenuItem { Tag: ControlItem item })
        {
            item.OnAxisTypeChanged(AxisType.SplitPos);
        }
    }
}


public class ControlItem : INotifyPropertyChanged
{
    private readonly ControlHandler _cHandler;
    private readonly ControlInstance _instance;

    public string DeviceName => GetDeviceName();
    public string DeviceButton => _instance.ControlId.ToString() ?? "Unbound";
    public string DeviceButtonType => GetControlType();
    
    private bool _isActive = false;
    public bool IsActive => _isActive;
    private float _currentValue = 0.0f;
    public float CurrentValue => _currentValue;

    public string Name => _instance.Definition.Name;
    public string Description => _instance.Definition.Description;

    public ControlItem(ControlInstance instance, ControlHandler cHandler)
    {
        _instance = instance;
        _cHandler = cHandler;
        // Start listening for value updates from the controls handler.
        // These will trigger a UI refresh so users can see the current values.
        // (especially useful for setting up the axis type)
        _cHandler.On(_instance.Definition.Id, ValueUpdate);
    }

    public void ValueUpdate(object? sender, ControlChangeEventArgs e)
    {
        if (DeviceButtonType == "Button" || DeviceButtonType == "Key")
        {
            _isActive = (bool)e.NewValue;
            _currentValue = _isActive ? 100.0f : 0.0f;
            OnPropertyChanged(nameof(CurrentValue));
            OnPropertyChanged(nameof(IsActive));
        }
        else
        {
            _currentValue = (float)e.NewValue * 100.0f;
            _isActive = _currentValue > 0.5f || _currentValue < -0.5f;
            OnPropertyChanged(nameof(IsActive));
            OnPropertyChanged(nameof(CurrentValue));
        }
    }

    public void TriggerChange()
    {
        NotificationHandler.Current.SendNotification(new Notification
        {
            Id = "ControlSettings.Binding",
            Title = "Control Binding",
            Content = $"Press a key, button or move an axis to bind '{Name}'",
            IsProgressIndeterminate = true,
            CloseAfter = 0.0f
        });
        var result = _cHandler.WaitForInput(10.0f);
        NotificationHandler.Current.CloseNotification("ControlSettings.Binding");
        if (result.Item1 != "" && result.Item2 != "")
        {
            _cHandler.UpdateControlBindings(
                _instance.Definition.Id,
                result.Item1,
                result.Item2
            );
            OnPropertyChanged(nameof(DeviceName));
            OnPropertyChanged(nameof(DeviceButton));
            OnPropertyChanged(nameof(DeviceButtonType));
            NotificationHandler.Current.SendNotification(new Notification
            {
                Id = "ControlSettings.SuccessfullyBound",
                Title = "Control Bound",
                Content = $"Successfully bound '{Name}' to {DeviceName} - {DeviceButton}",
                Level = GrowlLevel.Success,
                CloseAfter = 5.0f
            });
        }
        else
        {
            NotificationHandler.Current.SendNotification(new Notification
            {
                Id = "ControlSettings.BindingFailed",
                Title = "Binding Cancelled",
                Content = $"Binding for '{Name}' was cancelled or timed out.",
                Level = GrowlLevel.Warning,
                CloseAfter = 5.0f
            });
        }
    }

    public void OnAxisTypeChanged(AxisType newType)
    {
        _cHandler.UpdateAxisBehaviour(
            _instance.Definition.Id,
            newType
        );
        OnPropertyChanged(nameof(DeviceButtonType));
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    // This function parses the joystick name from the device ID.
    // I tried to handle some special cases (like "Controller (XBOX One for Windows)"),
    // but there might still be some edge cases that look weird.
    // TODO: Update as necessary.
    private string GetDeviceName()
    {
        if (string.IsNullOrEmpty(_instance.DeviceId))
        {
            return "Unbound";
        }

        if (_instance.DeviceId.ToLower().StartsWith("keyboard"))
        {
            return "Keyboard";
        }

        var joystick = _cHandler.GetJoystickById(_instance.DeviceId);
        string name = joystick != null 
                      ? joystick.Information.ProductName 
                      : "Not Connected";

        if (name.StartsWith("Controller ("))
        {
            name = name.Replace("Controller (", "");
            name = name.EndsWith(")") ? name[..^1] : name;
        }

        // TODO: Dynamic truncation? (i.e. when the window is resized)
        if (name.Length > 43)
        {
            name = name.Substring(0, 40) + "...";
        }

        return name;
    }

    private string GetControlType()
    {
        if (!_instance.IsBound())
            return "Unbound";
        
        bool isKeyboard = _instance.DeviceId.ToString().ToLower().StartsWith("keyboard");
        bool isButton = _instance.ControlId.ToString()?.StartsWith("B") ?? false;

        if (isKeyboard)
            return "Key";
        if (isButton)
            return "Button";

        return _instance.AxisBehavior.ToString() + " Axis";
    }
}
