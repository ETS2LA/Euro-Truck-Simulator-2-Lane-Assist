using Velopack;
using Velopack.Locators;

using ETS2LA.AR;

namespace ETS2LA;

internal static class Program
{
    /// <summary>
    ///  Main entrypoint for ETS2LA.
    /// </summary>
    static void Main(string[] args)
    {
        // Velopack is the installer / update manager
        VelopackApp.Build()
            .SetAutoApplyOnStartup(false)
            #if DEBUG
            .SetLocator(new TestVelopackLocator(
                appId: "ETS2LA",
                version: "1.0.0",
                packagesDir: "./Releases/Portable"
            ))
            #endif
            .Run();

        var BackendThread = Task.Run(() =>
        {
            // These initialize global instances of both the AR overlay and the backend.
            // Overlay is started "first" since some plugins might need to reference it.
            var ar = ARHandler.Current;
            var backend = Backend.PluginBackend.Current;
        });

        // Gotta wait for the UI thread to close (i.e. user closed the window)
        // and then tell the backend to shutdown too.
        UI.Program.Main(args);
        Backend.PluginBackend.Current.Shutdown();
    }
}
