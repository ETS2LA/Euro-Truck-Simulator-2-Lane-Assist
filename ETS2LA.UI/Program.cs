using System;
using System.Runtime.InteropServices;
using Microsoft.Extensions.DependencyInjection;
using Photino.Blazor;
using Photino.NET;

namespace ETS2LA.UI;

public class UserInterface
{
    private static readonly Lazy<UserInterface> _instance = new(() => new UserInterface());
    public static UserInterface Current => _instance.Value;

    public PhotinoWindow Window { get; private set; }
    
    #if LINUX
        [DllImport("libc", EntryPoint = "setenv", CallingConvention = CallingConvention.Cdecl)]
        private static extern int SetNativeEnv(string name, string value, int overwrite);
    #endif

    [STAThread]
    public static void Start(string[] args)
    {
        #if LINUX
            SetNativeEnv("GDK_BACKEND", "x11", 1);
            SetNativeEnv("WEBKIT_DISABLE_DMABUF_RENDERER", "1", 1);
            SetNativeEnv("WEBKIT_FORCE_COMPOSITING_MODE", "1", 1);
        #endif

        var appBuilder = PhotinoBlazorAppBuilder.CreateDefault(args);

        // mounted into <div id="app"> inside wwwroot/index.html.
        appBuilder.RootComponents.Add<App>("#app");
        var app = appBuilder.Build();

        app.MainWindow
            .SetTitle("ETS2LA")
            .SetUserAgent("ETS2LA/3.X.X")
            .SetIconFile("wwwroot/favicon.ico")
            .SetUseOsDefaultSize(false)
            .SetUseOsDefaultLocation(false)
            .SetMinSize(800, 600)
            .SetSize(WindowSettings.Current.Width, WindowSettings.Current.Height)
            .SetLogVerbosity(0)
            .SetTransparent(true)
            .SetZoom(WindowSettings.Current.Zoom)
            .RegisterWebMessageReceivedHandler((sender, e) => IPC.HandleMessage(e, sender, app))
            #if DEBUG
            .SetDevToolsEnabled(true)
            #endif
            .SetChromeless(true);

        if (WindowSettings.Current.X != 0 || WindowSettings.Current.Y != 0)
            app.MainWindow.Location = new System.Drawing.Point(WindowSettings.Current.X, WindowSettings.Current.Y);
        else 
            app.MainWindow.Center();

        Current.Window = app.MainWindow;
        Current.Window.WindowSizeChanged += (sender, e) => {
            WindowSettings.Current.Width = e.Width;
            WindowSettings.Current.Height = e.Height;
        };
        Current.Window.WindowLocationChanged += (sender, e) => {
            WindowSettings.Current.X = e.X;
            WindowSettings.Current.Y = e.Y;
        };
        
        // blocking until window is closed.
        app.Run();
        WindowSettings.Current.Save();
    }
}