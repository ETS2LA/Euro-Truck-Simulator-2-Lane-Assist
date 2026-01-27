using ETS2LA.Shared;
using ETS2LA.Logging;
using Huskui.Avalonia.Controls;

namespace ETS2LA.Backend
{
    public class PluginHandler
    {
        // These are files in the plugins folder that the backend will
        // exclude when trying to load.
        private readonly List<string> _exclusions = new()
        {
            "Microsoft.*",
            "System.*",
            "SharpDX.*",
            "ETS2LA.*",
        };

        private readonly IEventBus _bus;
        public readonly List<IPlugin> LoadedPlugins = new();
        public Action<IPlugin>? PluginEnabled;
        public Action<IPlugin>? PluginDisabled;
        public bool loading = false;

        public PluginHandler(IEventBus eventBus)
        {
            _bus = eventBus;
        }

        public string[] DiscoverPlugins()
        {
            try
            {
                var pluginFiles = Directory.GetFiles("Plugins", "*.dll");

                // Exclude anything in _exclusions.
                pluginFiles = pluginFiles.Where(file =>
                {
                    var fileName = Path.GetFileName(file);
                    return !_exclusions.Any(pattern => System.Text.RegularExpressions.Regex.IsMatch(fileName, "^" + System.Text.RegularExpressions.Regex.Escape(pattern).Replace("\\*", ".*") + "$"));
                }).ToArray();

                return pluginFiles;
            } catch (Exception ex)
            {
                Logger.Error($"Failed to discover plugins: {ex.Message}");
                return Array.Empty<string>();
            }
        }

        public void LoadPlugins()
        {
            loading = true;
            string[] pluginFiles = DiscoverPlugins();
            Logger.Info($"Discovered {pluginFiles.Length} .dll files in Plugin folder.");
            foreach (string filename in pluginFiles)
            {
                Thread.Sleep(100); // Slight delay to avoid overwhelming the system
                                   // and to allow other processes / logging to run smoothly.
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
                        plugin.Init();
                        plugin.Register(_bus);
                        LoadedPlugins.Add(plugin);
                        Logger.Info($"Loaded plugin: [gray]{type.FullName}[/] from [gray]{filename}[/].");
                    }
                }
                catch (Exception ex)
                {
                    // stacktrace + inner exceptions
                    if (ex is System.Reflection.ReflectionTypeLoadException rtle)
                    {
                        Logger.Error($"Failed to load plugin from [gray]{filename}[/]: {rtle}");
                        foreach (var le in rtle.LoaderExceptions)
                        {
                            Logger.Error(le?.ToString() ?? "LoaderException: null");
                        }
                    }
                    else if (ex is System.Reflection.TargetInvocationException tie && tie.InnerException != null)
                    {
                        Logger.Error($"Failed to load plugin from [gray]{filename}[/]: {tie.InnerException}");
                        Logger.Error(tie.InnerException.ToString());
                    }
                    else
                    {
                        Logger.Error($"Failed to load plugin from [gray]{filename}[/]: {ex}");
                    }
                }
            }
            loading = false;
        }

        public void UnloadPlugins()
        {
            loading = true;
            foreach (var plugin in LoadedPlugins)
            {
                try
                {
                    if(plugin._IsRunning)
                        plugin.OnDisable();
                        
                    plugin.Shutdown();
                }
                catch (Exception ex)
                {
                    Logger.Error($"Failed to shutdown plugin {plugin.GetType().FullName}: {ex.Message}");
                }
            }
            LoadedPlugins.Clear();
            loading = false;
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
                Logger.Info($"Enabled plugin: [bold]{plugin.Info.Name}[/]");
                PluginEnabled?.Invoke(plugin);
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
                Logger.Info($"Disabled plugin: [bold]{plugin.Info.Name}[/]");
                PluginDisabled?.Invoke(plugin);
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