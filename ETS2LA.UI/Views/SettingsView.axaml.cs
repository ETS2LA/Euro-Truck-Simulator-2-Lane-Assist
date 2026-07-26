using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Controls.Metadata;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using ETS2LA.Backend.Events;
using ETS2LA.UI.Views.Settings;

namespace ETS2LA.UI.Views;

public partial class SettingsView : UserControl
{

    private readonly DisplaySettings _displaySettings = new();
    private readonly AudioSettings _audioSettings = new();
    private readonly ThemeSettings _themeSettings = new();
    private readonly ControlSettings _controlSettings = new();
    private readonly SDKSettings _sdkSettings = new();
    private readonly Updates _updates = new();
    private readonly AssistanceSettingsPage _assistanceSettings = new();
    private readonly DataSettingsPage _dataSettings = new();
    private readonly UserSettingsView _userSettings = new();
    private readonly ExperimentsSettings _experimentsSettings = new();

    public string SelectedPageName { get; private set; } = string.Empty;

    private readonly List<Button> _navButtons = new();
    ContentControl _contentHost => this.FindControl<ContentControl>("ContentHost") ?? throw new InvalidOperationException("ContentHost not found");

    public SettingsView()
    {
        InitializeComponent();

#pragma warning disable CS8601 // Possible null reference assignment.
        _navButtons.AddRange(
        [
            // Don't know why I have to find the controls, a direct reference
            // to them via x:Name doesn't work in this file for some reason.
            // TODO: Investigate later.
            this.FindControl<Button>("DisplayButton"),
            this.FindControl<Button>("AudioButton"),
            this.FindControl<Button>("ThemeButton"),
            this.FindControl<Button>("ControlsButton"),
            this.FindControl<Button>("SDKButton"),
            this.FindControl<Button>("UserButton"),
            this.FindControl<Button>("UpdateButton"),
            this.FindControl<Button>("AssistanceButton"),
            this.FindControl<Button>("DataButton"),
            this.FindControl<Button>("ExperimentsButton")
        ]);
#pragma warning restore CS8601 // Possible null reference assignment.

    }

    private void SetSelected(string active)
    {
        foreach (var button in _navButtons)
        {
            button.Classes.Remove("Selected");
        }

        this.FindControl<Button>(active)?.Classes.Add("Selected");
        string pageName = active.Replace("Button", "");
        SelectedPageName = pageName;
        Events.Current.Publish<string>("ETS2LA.UI.SwitchedPage", "Settings." + pageName);
        Events.Current.Publish<EventArgs>($"ETS2LA.UI.SwitchedPage.Settings.{pageName}", EventArgs.Empty);

        // Focus the content host for accessibility
        _contentHost.Focus();
    }

    private void OnUserSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _userSettings;
        SetSelected("UserButton");
    }

    private void OnDisplaySettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _displaySettings;
        SetSelected("DisplayButton");
    }

    private void OnAudioSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _audioSettings;
        SetSelected("AudioButton");
    }

    private void OnThemeSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _themeSettings;
        SetSelected("ThemeButton");
    }

    private void OnControlsSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _controlSettings;
        SetSelected("ControlsButton");
    }

    private void OnSDKSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _sdkSettings;
        SetSelected("SDKButton");
    }

    private void OnUpdatesClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _updates;
        SetSelected("UpdateButton");
    }

    private void OnAssistanceSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _assistanceSettings;
        SetSelected("AssistanceButton");
    }

    private void OnDataSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _dataSettings;
        SetSelected("DataButton");
    }

    private void OnExperimentsSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _experimentsSettings;
        SetSelected("ExperimentsButton");
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}