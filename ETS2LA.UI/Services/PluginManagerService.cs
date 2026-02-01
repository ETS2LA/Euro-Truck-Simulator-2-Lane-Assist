using ETS2LA.Backend;
using ETS2LA.Shared;

namespace ETS2LA.UI.Services;

public sealed class PluginManagerService
{
    public PluginBackend backend = null!;

    public PluginManagerService()
    {
        backend = PluginBackend.Current;
        Task.Run(() => backend.Start());
    }

    public List<IPlugin> GetPlugins()
    {
        if (backend.pluginHandler == null)
            return new List<IPlugin>();
        
        return backend.pluginHandler.LoadedPlugins;
    }

    public bool SetEnabled(IPlugin plugin, bool enable)
    {
        var ok = enable
            ? backend.pluginHandler!.EnablePlugin(plugin)
            : backend.pluginHandler!.DisablePlugin(plugin);

        return ok;
    }

    public void Shutdown()
    {
    }
}