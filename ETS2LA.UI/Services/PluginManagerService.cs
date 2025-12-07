using System.Reflection;
using System.IO;
using ETS2LA.Backend;
using ETS2LA.Shared;
using ETS2LA.Logging;
using System;

namespace ETS2LA.UI.Services;

public sealed class PluginManagerService
{
    private readonly EventBus _bus = new();
    private readonly PluginHandler _handler;
    private readonly List<PluginUiInfo> _pluginUis = new();

    public PluginManagerService()
    {
        _handler = new PluginHandler(_bus);
        LoadPluginsSafe();
        NotifyChanged();
    }

    public event Action? PluginsChanged;

    public IEnumerable<PluginMetadata> GetPlugins()
    {
        foreach (var plugin in _handler.LoadedPlugins)
        {
            var assembly = plugin.GetType().Assembly;
            var info = assembly.GetCustomAttribute<PluginInformation>();

            yield return new PluginMetadata(
                info?.Name ?? plugin.GetType().Name,
                info?.Description ?? "No description provided.",
                info?.AuthorName ?? "Unknown",
                info?.Tags ?? Array.Empty<string>(),
                plugin);
        }
    }

    public bool SetEnabled(PluginMetadata plugin, bool enable)
    {
        var ok = enable
            ? _handler.EnablePlugin(plugin.Instance)
            : _handler.DisablePlugin(plugin.Instance);

        if (ok)
            NotifyChanged();

        return ok;
    }

    public void Reload()
    {
        _handler.LoadedPlugins.Clear();
        _pluginUis.Clear();
        LoadPluginsSafe();
        NotifyChanged();
    }

    public IReadOnlyList<PluginUiInfo> GetPluginUis() => _pluginUis;

    private void LoadPluginsSafe()
    {
        var originalCwd = Environment.CurrentDirectory;
        var workingDir = ResolveWorkingDirectory();
        Environment.CurrentDirectory = workingDir;
        try
        {
            var dlls = DiscoverPluginPaths(workingDir).ToList();
            Logger.Info($"Plugin loader scanning {dlls.Count} assemblies under '{Path.Combine(workingDir, "Plugins")}'.");

            foreach (var dll in dlls)
            {
                try
                {
                    var assembly = System.Reflection.Assembly.LoadFrom(dll);
                    var pluginTypes = assembly.GetTypes()
                        .Where(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsInterface && !t.IsAbstract);

                    foreach (var type in pluginTypes)
                    {
                        var plugin = (IPlugin)Activator.CreateInstance(type)!;
                        plugin.Init(_bus);
                        _handler.LoadedPlugins.Add(plugin);
                        Logger.Info($"Loaded plugin: {type.FullName} from {dll}");

                        if (plugin is IPluginUi uiProvider)
                        {
                            var pages = uiProvider.RenderPages().ToList();
                            var info = assembly.GetCustomAttribute<PluginInformation>();
                            var meta = new PluginMetadata(
                                info?.Name ?? plugin.GetType().Name,
                                info?.Description ?? "No description provided.",
                                info?.AuthorName ?? "Unknown",
                                info?.Tags ?? Array.Empty<string>(),
                                plugin);
                            _pluginUis.Add(new PluginUiInfo(meta, uiProvider, pages));
                        }
                    }
                }
                catch (Exception ex)
                {
                    Logger.Error($"Failed to load plugins from {dll}: {ex.Message}");
                }
            }
        }
        finally
        {
            Environment.CurrentDirectory = originalCwd;
        }
    }

    private static IEnumerable<string> DiscoverPluginPaths(string workingDir)
    {
        var pluginsRoot = Path.Combine(workingDir, "Plugins");
        if (!Directory.Exists(pluginsRoot))
            return Enumerable.Empty<string>();

        var candidates = Directory.EnumerateFiles(pluginsRoot, "*.dll", SearchOption.AllDirectories)
            .Where(p => !p.Contains($"{Path.DirectorySeparatorChar}ref{Path.DirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase))
            .Where(p => !Path.GetFileName(p).EndsWith(".resources.dll", StringComparison.OrdinalIgnoreCase))
            .Where(p => !Path.GetFileName(p).StartsWith("Microsoft.", StringComparison.OrdinalIgnoreCase))
            .Where(p => !Path.GetFileName(p).StartsWith("System.", StringComparison.OrdinalIgnoreCase));

        return candidates
            .GroupBy(Path.GetFileNameWithoutExtension, StringComparer.OrdinalIgnoreCase)
            .Select(g => g.OrderByDescending(File.GetLastWriteTimeUtc).First());
    }

    private static string ResolveWorkingDirectory()
    {
        // Prefer executable directory first.
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            if (Directory.Exists(Path.Combine(dir.FullName, "Plugins")))
                return dir.FullName;
            dir = dir.Parent;
        }

        // Fallback: current directory walk-up.
        dir = new DirectoryInfo(Environment.CurrentDirectory);
        while (dir is not null)
        {
            if (Directory.Exists(Path.Combine(dir.FullName, "Plugins")))
                return dir.FullName;
            dir = dir.Parent;
        }

        return Environment.CurrentDirectory;
    }

    private void NotifyChanged() => PluginsChanged?.Invoke();
}

public record PluginMetadata(
    string Name,
    string Description,
    string Author,
    string[] Tags,
    IPlugin Instance);

public record PluginUiInfo(
    PluginMetadata Metadata,
    IPluginUi Ui,
    IReadOnlyList<PluginPage> Pages);
