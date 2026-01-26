using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using Avalonia.Controls;
using Avalonia.Interactivity;

using ETS2LA.Controls;
using ETS2LA.Logging;

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

    private void OnTriggerChange(object? sender, RoutedEventArgs e)
    {
        if (sender is Control { Tag: ControlItem item })
        {
            item.TriggerChange();
        }
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
        Logger.Info($"Control list updated, total controls: {Controls.Count}");
    }
}


public class ControlItem : INotifyPropertyChanged
{
    private readonly ControlHandler _cHandler;
    private readonly ControlInstance _instance;

    public string DeviceName => _instance.DeviceId != "" ? _instance.DeviceId : "Unbound";
    public string DeviceButton => _instance.ControlId.ToString() ?? "Unbound";
    public string Name => _instance.Definition.Name;
    public string Description => _instance.Definition.Description;

    public ControlItem(ControlInstance instance, ControlHandler cHandler)
    {
        _instance = instance;
        _cHandler = cHandler;
        Update();
    }

    public void Update()
    {
        
    }

    public void TriggerChange()
    {
        
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
