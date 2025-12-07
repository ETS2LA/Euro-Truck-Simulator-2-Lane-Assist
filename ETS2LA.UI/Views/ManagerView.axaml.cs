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
    public ObservableCollection<PluginItem> Plugins { get; } = new();
    private readonly PluginManagerService _pluginService;
    public bool HasPlugins
    {
        get => _hasPlugins;
        private set
        {
            if (_hasPlugins == value) return;
            _hasPlugins = value;
            OnPropertyChanged();
        }
    }
    private bool _hasPlugins;

    public ManagerView(PluginManagerService? service = null)
    {
        _pluginService = service ?? new PluginManagerService();
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

    private void OnRefreshClick(object? sender, RoutedEventArgs e)
    {
        UpdatePluginList();
    }

    private void OnCardPointerReleased(object? sender, PointerReleasedEventArgs e)
    {
        if (e.Source is Button) return; // avoid toggling when pressing buttons
        if (sender is Border { Tag: PluginItem item })
        {
            item.Toggle();
        }
    }

    private async void OnOpenSettingsClick(object? sender, RoutedEventArgs e)
    {
        if (sender is not Control { Tag: PluginItem item }) return;
        var page = item.SettingsPage;
        if (page == null || item.Ui == null) return;

        var window = new PluginUiWindow();
        window.LoadPage(page, item.Ui);
        await window.ShowDialog((Window?)VisualRoot);
    }

    private void LoadPlugins()
    {
        Plugins.Clear();
        UpdatePluginList();
    }

    private void UpdatePluginList()
    {
        var uiEntries = _pluginService.GetPluginUis().ToDictionary(x => x.Metadata.Instance);
        foreach (var plugin in _pluginService.GetPlugins())
        {
            uiEntries.TryGetValue(plugin.Instance, out var uiInfo);
            Plugins.Add(new PluginItem(plugin, _pluginService, uiInfo?.Ui, uiInfo?.Pages));
        }

        HasPlugins = Plugins.Count > 0;
        if (this.FindControl<ItemsControl>("PluginList") is { } list)
            list.IsVisible = HasPlugins;
        if (this.FindControl<Border>("PlaceholderPanel") is { } placeholder)
            placeholder.IsVisible = !HasPlugins;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public new event PropertyChangedEventHandler? PropertyChanged;

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

public class PluginItem : INotifyPropertyChanged
{
    private static readonly IBrush EnabledCard = new SolidColorBrush(Color.Parse("#1E2732"));
    private static readonly IBrush DisabledCard = new SolidColorBrush(Color.Parse("#16181D"));
    private static readonly IBrush EnabledStatus = new SolidColorBrush(Color.Parse("#2D7DFF"));
    private static readonly IBrush DisabledStatus = new SolidColorBrush(Color.Parse("#262B33"));
    private static readonly IBrush PrimaryText = new SolidColorBrush(Color.Parse("#ECEDEE"));

    private readonly PluginMetadata _metadata;
    private readonly PluginManagerService _service;
    private bool _isEnabled;

    public string Name { get; }
    public string Description { get; }
    public string Source { get; }
    public string Initials { get; }
    public bool HasSettingsPage { get; }
    public PluginPage? SettingsPage { get; }
    public IPluginUi? Ui { get; }

    public bool IsEnabled
    {
        get => _isEnabled;
        set
        {
            if (_isEnabled == value) return;
            _isEnabled = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(StatusText));
            OnPropertyChanged(nameof(CardBackground));
            OnPropertyChanged(nameof(StatusBackground));
            OnPropertyChanged(nameof(StatusForeground));
        }
    }

    public string StatusText => IsEnabled ? "Enabled" : "Disabled";
    public IBrush CardBackground => IsEnabled ? EnabledCard : DisabledCard;
    public IBrush StatusBackground => IsEnabled ? EnabledStatus : DisabledStatus;
    public IBrush StatusForeground => IsEnabled ? Brushes.White : PrimaryText;

    public PluginItem(PluginMetadata metadata, PluginManagerService service, IPluginUi? ui = null, IReadOnlyList<PluginPage>? pages = null)
    {
        _metadata = metadata;
        _service = service;
        Ui = ui;

        Name = metadata.Name;
        Description = metadata.Description;
        Source = string.IsNullOrWhiteSpace(metadata.Author) ? "Unknown" : metadata.Author;
        Initials = BuildInitials(Name);
        _isEnabled = metadata.Instance._IsRunning;

        SettingsPage = pages?.FirstOrDefault(p => p.Location == PluginPageLocation.Settings);
        HasSettingsPage = SettingsPage != null;
    }

    public void Toggle()
    {
        var target = !IsEnabled;
        var success = _service.SetEnabled(_metadata, target);
        if (success)
            IsEnabled = target;
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
