using Velopack;

namespace ETS2LA;

internal static class Program
{
    /// <summary>
    ///  Main entrypoint for ETS2LA.
    /// </summary>
    static void Main(string[] args)
    {
        // Velopack is the installer / update manager
        VelopackApp.Build().Run();

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
