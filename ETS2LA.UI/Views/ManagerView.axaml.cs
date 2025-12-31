using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Linq;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using Avalonia.Input;
using Avalonia.Media;
using ETS2LA.UI.Services;
using ETS2LA.Shared;

namespace ETS2LA.UI.Views;

public partial class ManagerView : UserControl
{
    // This list is listened by the UI to show available plugins.
    public ObservableCollection<PluginItem> Plugins { get; } = new();
    private readonly PluginManagerService _pluginService;

    public ManagerView(PluginManagerService service)
    {
        _pluginService = service;
        InitializeComponent();
        DataContext = this;
        UpdatePluginList();
    }

    private void TogglePluginClick(object? sender, RoutedEventArgs e)
    {
        if (sender is Control { Tag: PluginItem item })
        {
            item.Toggle();
        }
    }

    private void OnCardPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.Source is Button) return; // avoid toggling when pressing buttons
        if (sender is Huskui.Avalonia.Controls.Card { Tag: PluginItem item })
        {
            item.Toggle();
        }
    }

    private void UpdatePluginList()
    {
        List<IPlugin> plugins = _pluginService.GetPlugins();
        foreach (var plugin in plugins)
        {
            Plugins.Add(new PluginItem(plugin, _pluginService));
            _pluginService.backend.pluginHandler?.PluginEnabled += (enabledPlugin) =>
            {
                if (enabledPlugin == plugin)
                {
                    var item = Plugins.FirstOrDefault(pi => pi.Name == plugin.Info.Name);
                    item?.Update();
                }
            };
            _pluginService.backend.pluginHandler?.PluginDisabled += (disabledPlugin) =>
            {
                if (disabledPlugin == plugin)
                {
                    var item = Plugins.FirstOrDefault(pi => pi.Name == plugin.Info.Name);
                    item?.Update();
                }
            };
        }

        bool hasPlugins = plugins.Count > 0;
        if (this.FindControl<ItemsControl>("PluginList") is { } list)
            list.IsVisible = hasPlugins;
        if (this.FindControl<Border>("PlaceholderPanel") is { } placeholder)
            placeholder.IsVisible = !hasPlugins;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}

public class PluginItem : INotifyPropertyChanged
{
    private readonly PluginManagerService _service;
    private readonly IPlugin _instance;
    private bool _isEnabled;

    public string Name => _instance.Info.Name;
    public string Description => _instance.Info.Description;
    public string Author => _instance.Info.AuthorName;
    public string Initials => BuildInitials(Name);

    public bool IsEnabled
    {
        get => _isEnabled;
        set
        {
            if (_isEnabled == value) return;
            _isEnabled = value;
            OnPropertyChanged();
        }
    }

    public PluginItem(IPlugin instance, PluginManagerService service)
    {
        _instance = instance;
        _service = service;
        _isEnabled = _instance._IsRunning;
        Update();
    }

    public void Update()
    {
        IsEnabled = _instance._IsRunning;
    }

    public void Toggle()
    {
        var target = !IsEnabled;
        _service.SetEnabled(_instance, target);
        Update();
    }

    private static string BuildInitials(string name)
    {
        var parts = name.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length == 1)
            return parts[0].Length >= 2 ? parts[0].Substring(0, 2).ToUpperInvariant() : parts[0].ToUpperInvariant();
        return string.Concat(parts.Take(2).Select(p => p[0])).ToUpperInvariant();
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
