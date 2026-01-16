using System.Reflection;
using Avalonia.Controls;
using ETS2LA.Backend;
using ETS2LA.Shared;
using Huskui.Avalonia.Controls;

namespace ETS2LA.UI.Services;

public sealed class PluginManagerService
{
    public PluginBackend backend = null!;

    public PluginManagerService(INotificationHandler window)
    {
        backend = PluginBackend.Instance;
        Task.Run(() => backend.Start(window));
    }

    public List<IPlugin> GetPlugins()
    {
        while (backend.pluginHandler == null)
        {
            Thread.Sleep(100);
        }

        while (backend.pluginHandler.loading)
        {
            Thread.Sleep(100);
        }

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
        backend.Shutdown();
    }
}