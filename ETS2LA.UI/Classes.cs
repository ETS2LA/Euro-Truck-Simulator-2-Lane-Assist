using System;
using System.Runtime.InteropServices;
using Photino.NET;

namespace ETS2LA.UI;

public class WebviewWindow
{

    # if LINUX
        [DllImport("libc", EntryPoint = "setenv", CallingConvention = CallingConvention.Cdecl)]
        private static extern int SetNativeEnv(string name, string value, int overwrite);
    # endif

    public static void Main(string[] args)
    {
        # if LINUX
            SetNativeEnv("GDK_BACKEND", "x11", 1);
            SetNativeEnv("WEBKIT_DISABLE_DMABUF_RENDERER", "1", 1);
            SetNativeEnv("WEBKIT_FORCE_COMPOSITING_MODE", "1", 1);
        #endif

        var window = new PhotinoWindow()
            .SetTitle("ETS2LA")
            .SetUseOsDefaultSize(false)
            .SetUseOsDefaultLocation(false)
            .SetMinSize(800, 600)
            .SetSize(1280, 720)
            # if DEBUG
            .SetDevToolsEnabled(true)
            # endif
            .Center()
            .SetChromeless(true);

        window.RegisterWebMessageReceivedHandler((sender, message) => IPC.HandleMessage(message, window));

        #if DEBUG
            // bun run dev in ETS2LA.Frontend
            window.Load("http://localhost:5173");
        #else
            string indexPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ETS2LA.Frontend", "dist", "index.html");
            window.Load(indexPath);
        #endif

        // This is essentially the main loop. Code past this won't run until the window is closed
        // (aka. ETS2LA is closed)
        window.WaitForClose();
    }
}
