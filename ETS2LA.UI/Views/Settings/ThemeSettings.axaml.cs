using Avalonia;
using Avalonia.Controls;
using ETS2LA.Logging;
using Avalonia.Styling;
using Huskui.Avalonia;

namespace ETS2LA.UI.Views.Settings;

public partial class ThemeSettings : UserControl
{
    private ThemeVariant CurrentTheme = Application.Current?.RequestedThemeVariant ?? ThemeVariant.Default;
    private AccentColor CurrentAccent = AccentColor.Orange;

    public ThemeSettings()
    {
        InitializeComponent();
        UpdateIndex();
    }

    private void UpdateIndex()
    {
        string key = CurrentTheme.Key.ToString() ?? "System";
        int index = key switch
        {
            "Light" => 1,
            "Dark" => 2,
            _ => 0,
        };
        this.Find<ComboBox>("ThemeCombobox")?.SelectedIndex = index;
        this.Find<ComboBox>("AccentColorCombobox")?.SelectedIndex = (int)CurrentAccent;
    }

    private void OnThemeChanged(object sender, SelectionChangedEventArgs e)
    {
        if (e.AddedItems.Count > 0)
        {
            var themeString = ((ComboBoxItem)e.AddedItems[0]).Content;
            CurrentTheme = themeString switch
            {
                "Light" => ThemeVariant.Light,
                "Dark" => ThemeVariant.Dark,
                _ => ThemeVariant.Default,
            };
        }
        UpdateIndex();
        Application.Current?.RequestedThemeVariant = CurrentTheme;
    }

    private void UpdateHuskuiTheme()
    {
        if (Application.Current?.Styles is { } styles)
        {
            // Find and update the HuskuiTheme
            foreach (var t in styles)
            {
                if (t is HuskuiTheme huskuiTheme)
                {
                    huskuiTheme.Accent = CurrentAccent;
                    break;
                }
            }
        }
    }

    private void OnAccentColorChanged(object sender, SelectionChangedEventArgs e)
    {
        if (e.AddedItems.Count > 0)
        {
            var accentString = ((ComboBoxItem)e.AddedItems[0]).Content;
            CurrentAccent = accentString switch
            {
                "System" => AccentColor.System,
                "Neutral" => AccentColor.Neutral,
                "Tomato" => AccentColor.Tomato,
                "Red" => AccentColor.Red,
                "Ruby" => AccentColor.Ruby,
                "Crimson" => AccentColor.Crimson,
                "Pink" => AccentColor.Pink,
                "Plum" => AccentColor.Plum,
                "Purple" => AccentColor.Purple,
                "Violet" => AccentColor.Violet,
                "Iris" => AccentColor.Iris,
                "Indigo" => AccentColor.Indigo,
                "Blue" => AccentColor.Blue,
                "Cyan" => AccentColor.Cyan,
                "Teal" => AccentColor.Teal,
                "Jade" => AccentColor.Jade,
                "Green" => AccentColor.Green,
                "Grass" => AccentColor.Grass,
                "Bronze" => AccentColor.Bronze,
                "Gold" => AccentColor.Gold,
                "Orange" => AccentColor.Orange,
                "Amber" => AccentColor.Amber,
                "Yellow" => AccentColor.Yellow,
                "Lime" => AccentColor.Lime,
                "Mint" => AccentColor.Mint,
                "Sky" => AccentColor.Sky,
                _ => AccentColor.Orange,
            };
            UpdateHuskuiTheme();
            UpdateIndex();
        }
    }
}
