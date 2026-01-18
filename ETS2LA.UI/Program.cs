using System;
using Avalonia;
using Avalonia.ReactiveUI;
using Projektanker.Icons.Avalonia;
using Projektanker.Icons.Avalonia.FontAwesome;
using Projektanker.Icons.Avalonia.MaterialDesign;

namespace ETS2LA.UI;

/// <summary>
///  The main entrypoint for ETS2LA's user interface.
///  This class will call App.axaml.cs to start the UI.
/// </summary>
public class Program
{
    // Avalonia configuration
    public static AppBuilder BuildAvaloniaApp()
    {
        IconProvider.Current
            .Register<FontAwesomeIconProvider>()
            .Register<MaterialDesignIconProvider>();

        return AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .UseReactiveUI();
    }

    // Called from ETS2LA entrypoint.
    public static void Main(string[] args)
    {
        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
    }
}
