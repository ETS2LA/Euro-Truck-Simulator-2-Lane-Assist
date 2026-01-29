using Splat;
using Velopack;
using Velopack.Locators;

#if WINDOWS
using System.Windows.Forms;
#endif

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
            #if WINDOWS
            .OnAfterInstallFastCallback((v) =>
            {
                // Doing this in a thread since a FastCallback means it should return instantly,
                // or it will cause Velopack to hang.
                new Thread(() =>
                {
                    MessageBox.Show("Please wait a few seconds for ETS2LA to finish setting up. You can close this notification.", "ETS2LA Installed", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }).Start();
            })
            #endif
            .Run();

        var BackendThread = Task.Run(() =>
        {
            var backend = Backend.PluginBackend.Current;
        });

        // Gotta wait for the UI thread to close (i.e. user closed the window)
        // and then tell the backend to shutdown too.
        UI.Program.Main(args);
        Backend.PluginBackend.Current.Shutdown();
    }
}
