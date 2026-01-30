using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using ETS2LA.Settings.Global;
using System.Runtime.CompilerServices;
using System.Collections.ObjectModel;

namespace ETS2LA.UI.Views.Settings;

public partial class AssistanceSettingsPage : UserControl, INotifyPropertyChanged
{
    public ObservableCollection<TabStripItemHandler> AccelerationOptions { get; } = new();
    public ObservableCollection<TabStripItemHandler> SteeringSensitivityOptions { get; } = new();
    public ObservableCollection<TabStripItemHandler> FollowingDistanceOptions { get; } = new();
    public ObservableCollection<TabStripItemHandler> SetSpeedBehaviourOptions { get; } = new();

    public bool SeparateCruiseAndSteering
    {
        get => AssistanceSettings.Current.SeparateCruiseAndSteering;
        set
        {
            if (AssistanceSettings.Current.SeparateCruiseAndSteering != value)
            {
                AssistanceSettings.Current.SeparateCruiseAndSteering = value;
                AssistanceSettings.Current.Save();
            }
        }
    }

    public int SelectedAccelerationOption { get; set; }
    public int SelectedSteeringSensitivityOption { get; set; }
    public int SelectedFollowingDistanceOption { get; set; }
    public int SelectedSetSpeedBehaviourOption { get; set; }

    public AssistanceSettingsPage()
    {
        LoadAccelerationOptions();
        LoadSteeringSensitivityOptions();
        LoadFollowingDistanceOptions();
        LoadSetSpeedBehaviourOptions();
        AvaloniaXamlLoader.Load(this);
        DataContext = this;
    }

    private void LoadAccelerationOptions()
    {
        SelectedAccelerationOption = (int)AssistanceSettings.Current.AccelerationResponse;
        foreach (AccelerationResponseOption option in Enum.GetValues(typeof(AccelerationResponseOption)))
        {
            AccelerationOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void LoadSteeringSensitivityOptions()
    {
        SelectedSteeringSensitivityOption = (int)AssistanceSettings.Current.SteeringSensitivity;
        foreach (SteeringSensitivityOption option in Enum.GetValues(typeof(SteeringSensitivityOption)))
        {
            SteeringSensitivityOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void LoadFollowingDistanceOptions()
    {
        SelectedFollowingDistanceOption = (int)AssistanceSettings.Current.FollowingDistance;
        foreach (FollowingDistanceOption option in Enum.GetValues(typeof(FollowingDistanceOption)))
        {
            FollowingDistanceOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void LoadSetSpeedBehaviourOptions()
    {
        SelectedSetSpeedBehaviourOption = (int)AssistanceSettings.Current.SetSpeedBehaviourOption;
        foreach (SetSpeedBehaviour option in Enum.GetValues(typeof(SetSpeedBehaviour)))
        {
            SetSpeedBehaviourOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void OnAccelerationOptionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedAccelerationOption >= 0)
        {
            AssistanceSettings.Current.AccelerationResponse = (AccelerationResponseOption)SelectedAccelerationOption;
            AssistanceSettings.Current.Save();
        }
    }

    private void OnSteeringSensitivityChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedSteeringSensitivityOption >= 0)
        {
            AssistanceSettings.Current.SteeringSensitivity = (SteeringSensitivityOption)SelectedSteeringSensitivityOption;
            AssistanceSettings.Current.Save();
        }
    }

    private void OnFollowingDistanceChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedFollowingDistanceOption >= 0)
        {
            AssistanceSettings.Current.FollowingDistance = (FollowingDistanceOption)SelectedFollowingDistanceOption;
            AssistanceSettings.Current.Save();
        }
    }

    private void OnSetSpeedBehaviourChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedSetSpeedBehaviourOption >= 0)
        {
            AssistanceSettings.Current.SetSpeedBehaviourOption = (SetSpeedBehaviour)SelectedSetSpeedBehaviourOption;
            AssistanceSettings.Current.Save();
        }
    }

    private void OnSeparateCruiseAndSteeringClicked(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        SeparateCruiseAndSteering = !SeparateCruiseAndSteering;
        OnPropertyChanged(nameof(SeparateCruiseAndSteering));
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

public class TabStripItemHandler: INotifyPropertyChanged
{
    public string Item { get; }
    public string Header => GetFormattedName();

    public TabStripItemHandler(string option)
    {
        Item = option;
    }

    private string GetFormattedName()
    {
        // Add a space before each capital letter (except the first)
        // e.g., "AccelerationResponse" -> "Acceleration Response"
        var formatted = System.Text.RegularExpressions.Regex.Replace(Item, "(\\B[A-Z])", " $1");
        return formatted;
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}