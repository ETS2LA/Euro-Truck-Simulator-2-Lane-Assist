using System.Collections.ObjectModel;
using System.Linq;
using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Threading;
using ETS2LA.Shared;
using ETS2LA.UI.Rendering;
using ETS2LA.UI.Services;

namespace ETS2LA.UI.Views;

public class PluginPageEntry
{
    public string Title { get; }
    public string Description { get; }
    public PluginPage Page { get; }
    public IPluginUi Ui { get; }

    public PluginPageEntry(string title, string description, PluginPage page, IPluginUi ui)
    {
        Title = title;
        Description = description;
        Page = page;
        Ui = ui;
    }
}

public partial class SettingsView : UserControl, INotifyPropertyChanged
{
    private readonly PluginManagerService _pluginService;
    public ObservableCollection<PluginPageEntry> Pages { get; } = new();
    public bool HasPluginPages
    {
        get => _hasPluginPages;
        private set
        {
            if (_hasPluginPages == value) return;
            _hasPluginPages = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(HasPluginPages)));
        }
    }
    private bool _hasPluginPages;

    public SettingsView(PluginManagerService pluginService)
    {
        InitializeComponent();
        return;
        // _pluginService = pluginService;
        // DataContext = this;
        // _pluginService.PluginsChanged += OnPluginsChanged;
        // RefreshPages();
    }

    private void OnPluginsChanged()
    {
        return;
        // Ensure updates happen on the UI thread.
        Dispatcher.UIThread.Post(RefreshPages);
    }

    public void RefreshPages()
    {
        return;
        // Pages.Clear();
        // var entries = _pluginService.GetPluginUis()
        //     .SelectMany(p => p.Pages
        //         .Where(pg => pg.Location == PluginPageLocation.Settings)
        //         .Select(pg => new PluginPageEntry(p.Metadata.Name, p.Metadata.Description, pg, p.Ui)))
        //     .ToList();

        // foreach (var e in entries)
        //     Pages.Add(e);
        // HasPluginPages = Pages.Count > 0;

        // if (this.FindControl<ListBox>("PluginList") is { } list &&
        //     this.FindControl<Border>("PluginPlaceholder") is { } placeholder)
        // {
        //     list.IsVisible = HasPluginPages;
        //     placeholder.IsVisible = !HasPluginPages;

        //     if (HasPluginPages)
        //         list.SelectedIndex = 0;
        //     else if (this.FindControl<ContentControl>("ContentHost") is { } host)
        //         host.Content = new TextBlock
        //         {
        //             Text = "No plugin settings available.",
        //             Foreground = this.FindResource("TextMutedBrush") as Avalonia.Media.IBrush
        //         };
        // }
    }

    private void OnSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        return;
        // if (this.FindControl<ContentControl>("ContentHost") is not { } host) return;
        // if (sender is not ListBox { SelectedItem: PluginPageEntry entry }) return;

        // host.Content = PluginUiRenderer.RenderPage(entry.Page, entry.Ui);
    }

    private void InitializeComponent()
    {
        return;
        // AvaloniaXamlLoader.Load(this);
    }

    public new event PropertyChangedEventHandler? PropertyChanged;
}
