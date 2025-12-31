using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Controls.Metadata;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using ETS2LA.UI.Views.Settings;

namespace ETS2LA.UI.Views;

[TemplatePart(PART_ContentHost, typeof(Control))]
public partial class SettingsView : UserControl
{

    private const string PART_ContentHost = "ContentHost";
    private readonly WindowSettings _windowSettings = new();
    private readonly List<Button> _navButtons = new();
    ContentControl _contentHost => this.FindControl<ContentControl>(PART_ContentHost) ?? throw new InvalidOperationException("ContentHost not found");

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
        // Placeholder for future Audio settings
    }

    private void OnThemeSettingsClick(object? sender, RoutedEventArgs e)
    {
        // Placeholder for future Theme settings
    }

    private void OnControlsSettingsClick(object? sender, RoutedEventArgs e)
    {
        // Placeholder for future Controls settings
    }

    private void OnSDKSettingsClick(object? sender, RoutedEventArgs e)
    {
        // Placeholder for future SDK settings
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}