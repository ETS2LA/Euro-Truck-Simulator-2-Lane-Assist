using ETS2LA.Networking.Users;
using ETS2LA.Networking.Settings;
using ETS2LA.Backend;
using ETS2LA.Backend.Events;
using ETS2LA.Backend.Plugins;
using ETS2LA.Notifications;
using ETS2LA.Logging;

using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;
using System.Reflection;

namespace ETS2LA.Networking.Plugins;

public class PluginApiClient
{
    public List<NetworkPlugin> AvailablePlugins { get; private set; } = new List<NetworkPlugin>();

    JsonSerializerOptions jsonOptions = new JsonSerializerOptions
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
    };

    private void Log(string message, NotificationLevel level = NotificationLevel.Information)
    {
        switch (level)
        {
            case NotificationLevel.Information:
                Logger.Info(message);
                break;
            case NotificationLevel.Warning:
                Logger.Warn(message);
                break;
            case NotificationLevel.Danger:
                Logger.Error(message);
                break;
            case NotificationLevel.Success:
                Logger.Success(message);
                break;
            default:
                Logger.Info(message);
                break;
        }

        NotificationHandler.Current.SendNotification(new Notification
        {
            Id = Guid.NewGuid().ToString(),
            Title = "Plugin Installer",
            Content = message,
            Level = level
        });
    }

    public async Task FetchAvailablePluginsAsync()
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            var response = await httpClient.GetAsync($"{apiServer.Value.BaseUrl}/plugins");
            response.EnsureSuccessStatusCode();

            var jsonResponse = await response.Content.ReadAsStringAsync();
            AvailablePlugins = JsonSerializer.Deserialize<List<NetworkPlugin>>(jsonResponse, jsonOptions) ?? new List<NetworkPlugin>();

            Log($"Fetched {AvailablePlugins.Count} plugins from {apiServer.Value.BaseUrl}");
        }
        catch
        {
            Log($"Failed to fetch available plugins. Please check your internet connection.", NotificationLevel.Danger);
        }
    }

    public NetworkPluginVersion? GetPluginUpdate(string pluginId)
    {
        var plugin = AvailablePlugins.FirstOrDefault(p => p.Id == pluginId);
        if (plugin == null)
        {
            Log($"Plugin with ID {pluginId} not found in available plugins.", NotificationLevel.Warning);
            return null;
        }

        InstalledPlugin? installedPlugin = InstalledPluginManifest.Current.InstalledPlugins.FirstOrDefault(p => p.Id == pluginId);
        if (!installedPlugin.HasValue || string.IsNullOrEmpty(installedPlugin.Value.Version))
        {
            return null;
        }

        var appVersion = Assembly.GetEntryAssembly()?.GetName().Version?.ToString(3) ?? "0.0.0";
        OperatingSystem currentOS = Environment.OSVersion.Platform != PlatformID.Unix ? OperatingSystem.Windows : OperatingSystem.Linux;
        var latestVersion = plugin.GetLatestCompatibleVersion(appVersion, currentOS);

        if (latestVersion == null || string.IsNullOrEmpty(latestVersion.Version))
        {
            Log($"No valid versions found for plugin with ID {pluginId}.", NotificationLevel.Warning);
            return null;
        }

        return new Version(latestVersion.Version) > new Version(installedPlugin.Value.Version) ? latestVersion : null;
    }

    public bool InstallPlugin(string pluginId, string? version = null)
    {
        var plugin = AvailablePlugins.FirstOrDefault(p => p.Id == pluginId);
        if (plugin == null)
        {
            Log($"Plugin with ID {pluginId} not found.", NotificationLevel.Warning);
            return false;   
        }

        var appVersion = Assembly.GetEntryAssembly()?.GetName().Version?.ToString(3) ?? "0.0.0";
        OperatingSystem currentOS = Environment.OSVersion.Platform != PlatformID.Unix ? OperatingSystem.Windows : OperatingSystem.Linux;

        NetworkPluginVersion targetVersion;
        if (string.IsNullOrEmpty(version))
        {
            var latestVersion = plugin.GetLatestCompatibleVersion(appVersion, currentOS);
            if (latestVersion == null)
            {
                Log($"No valid versions found for plugin with ID {pluginId}.", NotificationLevel.Warning);
                return false;
            }
            targetVersion = latestVersion;
        }
        else
        {
            targetVersion = plugin.Versions.FirstOrDefault(v => v.Version == version);
            if (targetVersion == null)
            {
                Log($"Version {version} not found for plugin with ID {pluginId}.", NotificationLevel.Warning);
                return false;
            }
            if (!plugin.IsCompatible(targetVersion, appVersion, currentOS))
            {
                Log($"Version {version} of plugin with ID {pluginId} is not compatible with the current application version or operating system.", NotificationLevel.Warning);
                return false;
            }
        }

        // Downloading is done from whatever region the user is in
        Region currentRegion = NetworkingSettings.Current.CurrentApiServer?.Name == "China" ? Region.China : Region.Global;
        string downloadUrl = targetVersion.DownloadUrl.FirstOrDefault(d => d.Key == Region.Global).Value;
        if (currentRegion == Region.China)
            downloadUrl = downloadUrl.Replace("ets2la.com", "ets2la.cn");

        if (string.IsNullOrEmpty(downloadUrl))
        {
            Log($"No download URL found for plugin with ID {pluginId} in region {currentRegion}.", NotificationLevel.Warning);
            return false;
        }

        if (targetVersion.Dependencies.Count > 0)
        {
            bool allDependenciesInstalled = true;
            foreach (var dependencyId in targetVersion.Dependencies)
            {
                if (!InstalledPluginManifest.Current.InstalledPlugins.Any(p => p.Id == dependencyId))
                {
                    if (!InstallPlugin(dependencyId))
                    {
                        Log($"Failed to install dependency {dependencyId} for plugin {pluginId}.", NotificationLevel.Warning);
                        allDependenciesInstalled = false;
                    }
                }
            }
            if (!allDependenciesInstalled)
            {
                Log($"Not all dependencies for plugin {pluginId} are installed.", NotificationLevel.Warning);
                return false;
            }
        }

        string tempFilePath = Path.GetTempFileName();
        using (var httpClient = new HttpClient())
        {
            var downloadTask = httpClient.GetAsync(downloadUrl);
            downloadTask.Wait();
            var downloadResponse = downloadTask.Result;
            if (!downloadResponse.IsSuccessStatusCode)
            {
                Log($"Failed to download plugin with ID {pluginId} from {downloadUrl}. Status code: {downloadResponse.StatusCode}", NotificationLevel.Warning);
                return false;
            }
            using (var fs = new FileStream(tempFilePath, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                var copyTask = downloadResponse.Content.CopyToAsync(fs);
                copyTask.Wait();
            }
        }

        // And the output path is determined by the PluginBackend's PluginRootPath.
        // On windows that's set to none so it's in /Plugins or /Libraries.
        string location = PluginBackend.Current.PluginHandler?.PluginRootPath ?? string.Empty;

        string type = plugin.Tags.Contains(NetworkPluginTags.Plugin) ? "Plugin" : "Library";
        string folder = type == "Plugin" ? "Plugins" : "Libraries";
        string outputPath = Path.Combine(location, folder, plugin.Id);
        Directory.CreateDirectory(outputPath);

        System.IO.Compression.ZipFile.ExtractToDirectory(tempFilePath, outputPath, true);
        File.Delete(tempFilePath);

        // Finally we just have to register this plugin in the InstalledPluginManifest.
        InstalledPluginManifest.Current.InstalledPlugins.Add(new InstalledPlugin
        {
            Id = plugin.Id,
            Version = targetVersion.Version,
            Dependencies = targetVersion.Dependencies,
            DllPath = Path.Combine(outputPath, targetVersion.DllPath),
            Type = type == "Plugin" ? PluginType.Plugin : PluginType.Library
        });
        InstalledPluginManifest.Current.Save();

        Events.Current.Publish<string>("ETS2LA.Plugins.Installed", pluginId);
        Events.Current.Publish<EventArgs>($"ETS2LA.Plugins.Installed.{pluginId}", EventArgs.Empty);
        Log($"Successfully installed plugin {plugin.Name} ({plugin.Id}, {targetVersion.Version})", NotificationLevel.Success);
        return true;
    }

    public bool UpdatePlugin(string pluginId)
    {
        if (GetPluginUpdate(pluginId) == null)
        {
            Log($"No update available for plugin with ID {pluginId}.", NotificationLevel.Information);
            return false;
        }

        // Uninstall the current version first.
        if (!UninstallPlugin(pluginId, overrideDependencyCheck: true))
        {
            Log($"Failed to uninstall current version of plugin with ID {pluginId}.", NotificationLevel.Warning);
            return false;
        }

        // Then install the latest version.
        if (!InstallPlugin(pluginId))
        {
            Log($"Failed to install latest version of plugin with ID {pluginId}.", NotificationLevel.Warning);
            return false;
        }

        Events.Current.Publish<string>("ETS2LA.Plugins.Updated", pluginId);
        Events.Current.Publish<EventArgs>($"ETS2LA.Plugins.Updated.{pluginId}", EventArgs.Empty);
        Log($"Successfully updated plugin with ID {pluginId}.", NotificationLevel.Success);
        return true;
    }

    public bool UninstallPlugin(string pluginId, bool overrideDependencyCheck = false)
    {
        InstalledPlugin? installedPlugin = InstalledPluginManifest.Current.InstalledPlugins.FirstOrDefault(p => p.Id == pluginId);
        if (installedPlugin == null)
        {
            Log($"Installed plugin with ID {pluginId} not found.", NotificationLevel.Warning);
            return false;
        }

        if (!overrideDependencyCheck)
        {
            // Scan for other plugins that depend on this one.
            var dependentPlugins = InstalledPluginManifest.Current.InstalledPlugins
                .Where(p => p.Dependencies.Contains(installedPlugin.Value.Id));
            if (dependentPlugins.Any())
            {
                string dependentPluginIds = string.Join(", ", dependentPlugins.Select(p => p.Id));
                Log($"Cannot uninstall plugin with ID {pluginId} because the following installed plugins depend on it: {dependentPluginIds}", NotificationLevel.Warning);
                return false;
            }
        }
        
        // Remove the plugin's files from the filesystem.
        string pluginPath = Path.Combine(
            PluginBackend.Current.PluginHandler?.PluginRootPath ?? string.Empty, 
            installedPlugin.Value.Type == PluginType.Plugin ? "Plugins" 
                                                            : "Libraries", 
            installedPlugin.Value.Id
        );

        if (Directory.Exists(pluginPath)) Directory.Delete(pluginPath, true);
        else
        {
            Log($"Apparent plugin directory {pluginPath} does not exist.", NotificationLevel.Warning);
            return false;
        }

        // And then we remove it from the InstalledPluginManifest.
        InstalledPluginManifest.Current.InstalledPlugins.Remove(installedPlugin.Value);
        InstalledPluginManifest.Current.Save();

        Events.Current.Publish<string>("ETS2LA.Plugins.Uninstalled", pluginId);
        Events.Current.Publish<EventArgs>($"ETS2LA.Plugins.Uninstalled.{pluginId}", EventArgs.Empty);
        Log($"Successfully uninstalled plugin with ID {pluginId}", NotificationLevel.Success);
        return true;
    }
}