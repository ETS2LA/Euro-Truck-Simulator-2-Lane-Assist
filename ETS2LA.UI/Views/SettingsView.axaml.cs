using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Controls.Metadata;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using ETS2LA.UI.Views.Settings;

namespace ETS2LA.UI.Views;

public partial class SettingsView : UserControl
{

    private readonly WindowSettings _windowSettings = new();
    private readonly AudioSettings _audioSettings = new();
    private readonly ThemeSettings _themeSettings = new();
    private readonly ControlSettings _controlSettings = new();
    private readonly SDKSettings _sdkSettings = new();
    private readonly Updates _updates = new();
    private readonly AssistanceSettingsPage _assistanceSettings = new();

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
            this.FindControl<Button>("WindowButton"),
            this.FindControl<Button>("AudioButton"),
            this.FindControl<Button>("ThemeButton"),
            this.FindControl<Button>("ControlsButton"),
            this.FindControl<Button>("SDKButton"),
            this.FindControl<Button>("UpdateButton"),
            this.FindControl<Button>("AssistanceButton"),
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
    }

    private void OnWindowSettingsClick(object? sender, RoutedEventArgs e)
    {
        _contentHost.Content = _windowSettings;
        SetSelected("WindowButton");
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

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}