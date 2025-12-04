using ETS2LA.Shared;
using ETS2LA.Logging;

namespace ETS2LA.Backend
{
    public class PluginHandler
    {
        private readonly IEventBus _bus;
        public readonly List<IPlugin> LoadedPlugins = new();

        public PluginHandler(IEventBus eventBus)
        {
            _bus = eventBus;
        }

        public string[] DiscoverPlugins()
        {
            var pluginFiles = Directory.GetFiles("Plugins", "*.dll");
            return pluginFiles;
        }

        public void LoadPlugins()
        {
            string[] pluginFiles = DiscoverPlugins();
            foreach (string filename in pluginFiles)
            {
                try
                {
                    // Load plugin assembly
                    var assembly = System.Reflection.Assembly.LoadFrom(filename);
                    var pluginTypes = assembly.GetTypes()
                        .Where(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsInterface && !t.IsAbstract);

                    // Init and save to list, there can be multiple plugins in one assembly.
                    foreach (var type in pluginTypes)
                    {
                        var plugin = (IPlugin)Activator.CreateInstance(type)!;
                        plugin.Init(_bus);
                        LoadedPlugins.Add(plugin);
                        Logger.Info($"Loaded plugin: {type.FullName} from {filename}");
                    }
                }
                catch (Exception ex)
                {
                    Logger.Error($"Failed to load plugin from {filename}: {ex.Message}");
                }
            }
        }

        private IPlugin? GetPluginByName(string pluginName)
        {
            return LoadedPlugins.FirstOrDefault(p => p.GetType().FullName == pluginName);
        }

        public bool EnablePlugin(IPlugin? plugin = null, string? pluginName = null)
        {
            plugin ??= GetPluginByName(pluginName!);
            if (plugin == null)
            {
                Logger.Warn($"Tried to enable {pluginName}, but it was not found among loaded plugins.");
                return false;
            }

            try
            {
                plugin.OnEnable();
                return true;
            }
            catch (Exception ex)
            {
                Logger.Error($"Failed to enable {plugin.GetType().FullName}: {ex.Message}");
                return false;
            }
        }

        public bool DisablePlugin(IPlugin? plugin = null, string? pluginName = null)
        {
            plugin ??= GetPluginByName(pluginName!);
            if (plugin == null)
            {
                Logger.Warn($"Tried to disable {pluginName}, but it was not found among loaded plugins.");
                return false;
            }

            try
            {
                plugin.OnDisable();
                return true;
            }
            catch (Exception ex)
            {
                Logger.Error($"Failed to disable {plugin.GetType().FullName}: {ex.Message}");
                return false;
            }
        }
    }
}