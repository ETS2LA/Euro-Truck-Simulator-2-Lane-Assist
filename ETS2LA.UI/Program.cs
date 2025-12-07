using System;
using Avalonia;
using Avalonia.ReactiveUI;

namespace ETS2LA.UI;

public static class Program
{
    // Avalonia configuration, don't remove; also used by previewer.
    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace()
            .UseReactiveUI();

    [STAThread]
    public static void Main(string[] args) =>
        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
}
