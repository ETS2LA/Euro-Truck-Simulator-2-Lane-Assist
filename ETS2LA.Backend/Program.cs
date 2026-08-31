using ETS2LA.Logging;
using ETS2LA.Controls;
using ETS2LA.Audio;
using static ETS2LA.Translations.T;

using Spectre.Console;

namespace ETS2LA.Backend
{
    /// <summary>
    ///  This class represents the plugin backend in ETS2LA. Every action to do with plugins
    ///  will one way or another go through this class. <br/> 
    ///  You usually shouldn't access it, but if you do, then use `PluginBackend.Current`.
    /// </summary>
    public class PluginBackend
    {
        private static readonly Lazy<PluginBackend> _instance = new(() => new PluginBackend());

        /// <summary>
        ///  This Instance property gives access to the ETS2LA-wide backend instance.
        ///  No matter where this is called from, it will always return the same instance.
        /// </summary>
        public static PluginBackend Current => _instance.Value;

        /// <summary>
        ///  The PluginHandler is what actually manages the plugins.
        /// </summary>
        public PluginHandler? PluginHandler;
        /// <summary>
        ///  This event is fired when the backend has been loaded.
        /// </summary>
        public Action OnBackendLoaded;
        /// <summary>
        ///  Is the backing loaded?
        /// </summary>
        public bool IsLoaded = false;

        public void Start()
        {
            Logger.Console.Status().Start(_("Starting ETS2LA..."), ctx =>
            {
                PluginHandler = new PluginHandler();
                PluginHandler.LoadLibraries();
                PluginHandler.LoadPlugins();
                Thread.Sleep(1000);

                Logger.Success(_("ETS2LA is running."));
                OnBackendLoaded?.Invoke();
                IsLoaded = true;
            });
        }

        public void Shutdown()
        {
            if (PluginHandler != null)
            {
                PluginHandler.UnloadPlugins();
            }
            ControlsBackend.Current.Shutdown();
            AudioHandler.Current.Shutdown();
            Logger.Info(_("Backend shutdown complete."));
        }
    }
}