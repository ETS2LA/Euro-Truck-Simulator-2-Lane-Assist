using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using ETS2LA.UI.Views;
using ETS2LA.UI.Services;
using Huskui.Avalonia.Controls;

namespace ETS2LA.UI;

public partial class MainWindow : AppWindow
{
    private enum PageKind
    {
        Dashboard,
        Visualization,
        Manager,
        Catalogue,
        Performance,
        Wiki,
        Roadmap,
        Feedback,
        Settings
    }

    private readonly List<Button> _navButtons = new();
    private readonly PluginManagerService _pluginService = new();
    private readonly DashboardView _dashboardView = new();
    private readonly ManagerView _managerView;
    private readonly SettingsView _settingsView;

    public MainWindow()
    {
        CanResize = true;
        ExtendClientAreaToDecorationsHint = true;
        InitializeComponent();
        _managerView = new ManagerView(_pluginService);
        _settingsView = new SettingsView(_pluginService);
        _navButtons.AddRange(new[]
        {
            DashboardButton, VisualizationButton, ManagerButton, CatalogueButton,
            PerformanceButton, WikiButton, RoadmapButton, FeedbackButton, SettingsButton
        });

        SetSelected(DashboardButton);
        ShowPage(PageKind.Dashboard);
    }

    private void TitleBar_PointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
            BeginMoveDrag(e);
    }

    private void OnMinimizeClick(object? sender, RoutedEventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void OnMaxRestoreClick(object? sender, RoutedEventArgs e)
    {
        WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
    }

    private void OnCloseClick(object? sender, RoutedEventArgs e)
    {
        Close();
    }

    private void ShowPage(PageKind page)
    {
        ContentHost.Content = page switch
        {
            PageKind.Dashboard => _dashboardView,
            PageKind.Manager => _managerView,
            PageKind.Visualization => CreatePlaceholder("Visualization", "Charts, map overlays, and telemetry visuals will live here."),
            PageKind.Catalogue => CreatePlaceholder("Catalogue", "List plugins, tools, or assets here when available."),
            PageKind.Performance => CreatePlaceholder("Performance", "Performance metrics and graphs will be shown here."),
            PageKind.Wiki => CreatePlaceholder("Wiki", "Link or embed documentation content."),
            PageKind.Roadmap => CreatePlaceholder("Roadmap", "Timeline and milestones will appear here."),
            PageKind.Feedback => CreatePlaceholder("Feedback", "Collect feedback or link to forms."),
            PageKind.Settings => ShowAndRefreshSettings(),
            _ => _dashboardView
        };
    }

    private Control ShowAndRefreshSettings()
    {
        _settingsView.RefreshPages();
        return _settingsView;
    }

    private Control CreatePlaceholder(string title, string body)
    {
        return new ScrollViewer
        {
            Content = new StackPanel
            {
                Spacing = 8,
                Children =
                {
                    new TextBlock { Text = title, FontSize = 18, FontWeight = Avalonia.Media.FontWeight.SemiBold, Foreground = this.FindResource("TextPrimaryBrush") as Avalonia.Media.IBrush },
                    new TextBlock { Text = body, Foreground = this.FindResource("TextSecondaryBrush") as Avalonia.Media.IBrush, TextWrapping = Avalonia.Media.TextWrapping.Wrap }
                }
            }
        };
    }

    private void SetSelected(Button active)
    {
        foreach (var button in _navButtons)
        {
            button.Classes.Remove("selected");
        }
        active.Classes.Add("selected");
    }

    private void OnDashboardClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(DashboardButton);
        ShowPage(PageKind.Dashboard);
    }

    private void OnVisualizationClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(VisualizationButton);
        ShowPage(PageKind.Visualization);
    }

    private void OnManagerClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(ManagerButton);
        ShowPage(PageKind.Manager);
    }

    private void OnCatalogueClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(CatalogueButton);
        ShowPage(PageKind.Catalogue);
    }

    private void OnPerformanceClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(PerformanceButton);
        ShowPage(PageKind.Performance);
    }

    private void OnWikiClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(WikiButton);
        ShowPage(PageKind.Wiki);
    }

    private void OnRoadmapClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(RoadmapButton);
        ShowPage(PageKind.Roadmap);
    }

    private void OnFeedbackClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(FeedbackButton);
        ShowPage(PageKind.Feedback);
    }

    private void OnSettingsClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(SettingsButton);
        ShowPage(PageKind.Settings);
    }
}
