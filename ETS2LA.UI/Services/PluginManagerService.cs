using System.Reflection;
using ETS2LA.Shared;

namespace ETS2LA.UI.Services;

public sealed class PluginManagerService
{
    Backend.Program backend = null!;
    private readonly List<PluginUiInfo> _pluginUis = new();

    public PluginManagerService()
    {
        // Start the backend.
        backend = new Backend.Program();
        backend.Main(Array.Empty<string>());
        NotifyChanged();
    }

    public event Action? PluginsChanged;

    public IEnumerable<PluginMetadata> GetPlugins()
    {
        foreach (var plugin in backend.pluginHandler!.LoadedPlugins)
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
            ? backend.pluginHandler!.EnablePlugin(plugin.Instance)
            : backend.pluginHandler!.DisablePlugin(plugin.Instance);

        if (ok)
            NotifyChanged();

        return ok;
    }

    public void Reload()
    {
        // Clear plugins and reload.
        // backend.pluginHandler!.LoadedPlugins.Clear();
        // backend.pluginHandler!.LoadPlugins();
        // _pluginUis.Clear();
        // NotifyChanged();
    }

    public IReadOnlyList<PluginUiInfo> GetPluginUis() => _pluginUis;

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
