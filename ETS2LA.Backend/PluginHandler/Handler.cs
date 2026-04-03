using ETS2LA.Shared;
using ETS2LA.Logging;
using Huskui.Avalonia.Controls;
using System.Runtime.Loader;

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

        public readonly List<IPlugin> LoadedPlugins = new();

        // Check PluginLoadContext.cs for why we need to keep track of them here.
        // TLDR: To be able to reload assemblies without restarting ETS2LA.
        private readonly Dictionary<IPlugin, AssemblyLoadContext> _pluginLoadContexts = new();
        // This also applies to shadow directories. Using shadow copies also means that it's
        // possible to detect .dll changes automatically in the future, meaning hot reloading
        // of plugins without requiring a direct reload action from the user.
        private readonly Dictionary<AssemblyLoadContext, string> _contextShadowDirectories = new();
        
        public Action<IPlugin>? PluginEnabled;
        public Action<IPlugin>? PluginDisabled;
        public bool loading = false;

        public string[] DiscoverPlugins()
        {
            try
            {
                var pluginFiles = Directory.GetFiles("Plugins", "*.dll");

                // Exclude anything in _exclusions.
                pluginFiles = pluginFiles.Where(file =>
                {
                    var fileName = Path.GetFileName(file);
                    return !_exclusions.Any(pattern => 
                        System.Text.RegularExpressions.Regex.IsMatch(fileName, 
                            "^" + System.Text.RegularExpressions.Regex.Escape(pattern).Replace("\\*", ".*") + "$"
                        ));
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
                    // This is so ugly...
                    // Please if anyone does have a better idea then help me :sob:
                    var absolutePath = Path.GetFullPath(filename);
                    var shadowPath = CreateShadowCopy(absolutePath);
                    var pluginDirectory = Path.GetDirectoryName(absolutePath) ?? Directory.GetCurrentDirectory();
                    
                    var loadContext = new PluginLoadContext(shadowPath, pluginDirectory);
                    _contextShadowDirectories[loadContext] = Path.GetDirectoryName(shadowPath)!;

                    var assembly = loadContext.LoadFromAssemblyPath(shadowPath);
                    var pluginTypes = assembly.GetTypes()
                        .Where(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsInterface && !t.IsAbstract);

                    var pluginLoaded = false;

                    // There can be multiple plugins in one assembly.
                    foreach (var type in pluginTypes)
                    {
                        var plugin = (IPlugin)Activator.CreateInstance(type)!;
                        plugin.Init();

                        LoadedPlugins.Add(plugin);
                        _pluginLoadContexts[plugin] = loadContext;
                        pluginLoaded = true;
                        
                        Logger.Info($"Loaded plugin: [gray]{type.FullName}[/] from [gray]{filename}[/].");
                    }

                    if (!pluginLoaded)
                    {
                        loadContext.Unload();
                        CleanupShadowDirectory(loadContext);
                    }
                }
                catch (Exception ex)
                {
                    // stacktrace + inner exceptions
                    // (basically we get the full exception info, inside the assembly context)
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
            // Keeps track of the load contexts of plugins
            // we've unloaded, these will be unloaded later.
            var loadContexts = new HashSet<AssemblyLoadContext>();

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

                if (_pluginLoadContexts.TryGetValue(plugin, out var loadContext))
                {
                    loadContexts.Add(loadContext);
                }
            }

            LoadedPlugins.Clear();
            _pluginLoadContexts.Clear();

            foreach (var loadContext in loadContexts)
            {
                try
                {
                    loadContext.Unload();
                }
                catch (Exception ex)
                {
                    Logger.Error($"Failed to unload plugin load context: {ex.Message}");
                }
            }

            // We wait just a bit to force GC to cleanup the old 
            // assemblies, otherwise they might still be around for 
            // the next cycle, meaning a call of UnloadPlugins -> LoadPlugins 
            // without delay might not update the .dlls as expected.
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();

            foreach (var loadContext in loadContexts)
            {
                CleanupShadowDirectory(loadContext);
            }

            loading = false;
        }

        private static string CreateShadowCopy(string sourceAssemblyPath)
        {
            var pluginName = Path.GetFileNameWithoutExtension(sourceAssemblyPath);
            var shadowDirectory = Path.Combine(Path.GetTempPath(), "ETS2LA", "PluginShadow", pluginName + "_" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(shadowDirectory);

            var destinationAssemblyPath = Path.Combine(shadowDirectory, Path.GetFileName(sourceAssemblyPath));
            File.Copy(sourceAssemblyPath, destinationAssemblyPath, overwrite: true);

            return destinationAssemblyPath;
        }

        private void CleanupShadowDirectory(AssemblyLoadContext context)
        {
            if (!_contextShadowDirectories.TryGetValue(context, out var shadowDirectory))
            {
                return;
            }

            _contextShadowDirectories.Remove(context);

            try
            {
                if (Directory.Exists(shadowDirectory))
                {
                    Directory.Delete(shadowDirectory, recursive: true);
                }
            }
            catch (Exception ex)
            {
                Logger.Warn($"Failed to clean plugin shadow directory [gray]{shadowDirectory}[/]: {ex.Message}");
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