using System;
using System.Runtime.InteropServices;
using Microsoft.Extensions.DependencyInjection;
using Photino.Blazor;

namespace ETS2LA.UI;

public class UserInterface
{
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
            .SetUseOsDefaultSize(false)
            .SetUseOsDefaultLocation(false)
            .SetMinSize(800, 600)
            .SetSize(1280, 720)
            .SetLogVerbosity(0)
            .RegisterWebMessageReceivedHandler((sender, e) => IPC.HandleMessage(e, sender, app))
            #if DEBUG
            .SetDevToolsEnabled(true)
            #endif
            .Center()
            .SetChromeless(true);

        // blocking until window is closed.
        app.Run();
    }
}