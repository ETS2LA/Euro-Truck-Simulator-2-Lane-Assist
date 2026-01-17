using Avalonia.Media;
using Avalonia.Input;
using Avalonia.Controls;
using Avalonia.Interactivity;

using ETS2LA.Shared;
using ETS2LA.UI.Views;
using ETS2LA.UI.Services;
using ETS2LA.UI.Notifications;

using Huskui.Avalonia.Models;
using Huskui.Avalonia.Controls;

namespace ETS2LA.UI;

public partial class MainWindow : AppWindow
{
    private enum PageKind
    {
        Dashboard,
        Visualization,
        Game,
        Manager,
        Catalogue,
        Performance,
        Wiki,
        Roadmap,
        Feedback,
        Settings
    }

    private bool IsWindows =>
        System.Runtime.InteropServices.RuntimeInformation
            .IsOSPlatform(System.Runtime.InteropServices.OSPlatform.Windows);

    private readonly List<Button> _navButtons = new();
    private readonly PluginManagerService _pluginService;
    private readonly DashboardView _dashboardView = new();
    private readonly VisualizationView _visualizationView = new();
    private readonly GameView _gameView;
    private readonly ManagerView _managerView;
    private readonly SettingsView _settingsView;

    public MainWindow()
    {
        CanResize = true;
        ExtendClientAreaToDecorationsHint = true;
        InitializeComponent();

        NotificationHandler.Instance.SetWindow(this);

        _pluginService = new PluginManagerService();
        _managerView = new ManagerView(_pluginService);
        _settingsView = new SettingsView();
        _visualizationView = new VisualizationView(_pluginService);
        _gameView = new GameView();
        _navButtons.AddRange(new[]
        {
            DashboardButton, VisualizationButton, GameButton, ManagerButton, CatalogueButton,
            PerformanceButton, WikiButton, RoadmapButton, FeedbackButton, SettingsButton
        });

        UpdateTitlebarButtonVisibility();
        SetSelected(DashboardButton);
        ShowPage(PageKind.Dashboard);
    }

    private void OnTitlebarPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
            BeginMoveDrag(e);
    }

    private void OnStayOnTopClick(object? sender, RoutedEventArgs e)
    {
        Topmost = !Topmost;
        StayOnTopIcon.Value = Topmost ? "mdi-picture-in-picture-bottom-right" : "mdi-picture-in-picture-bottom-right-outline";
        if (Topmost) StayOnTopIcon.Classes.Add("Highlight");
        else StayOnTopIcon.Classes.Remove("Highlight");
        
        NotificationHandler.Instance.SendNotification(new Notification
        {
            Id = "MainWindow.StayOnTopChanged",
            Title = "Stay On Top",
            Content = Topmost ? "Enabled" : "Disabled",
            CloseAfter = 2.0f,
            Level = Topmost ? GrowlLevel.Success : GrowlLevel.Danger
        });
    }

    private void OnTransparencyClick(object? sender, RoutedEventArgs e)
    {
        this.Opacity = this.Opacity == 1.0 ? 0.8 : 1.0;
        TransparencyIcon.Value = this.Opacity == 1.0 ? "fa-circle" : "fa-circle-half-stroke";
        if(this.Opacity == 1.0) TransparencyIcon.Classes.Remove("Highlight");
        else TransparencyIcon.Classes.Add("Highlight");
        
        NotificationHandler.Instance.SendNotification(new Notification
        {
            Id = "MainWindow.TransparencyChanged",
            Title = "Transparency",
            Content = this.Opacity < 1.0 ? "Enabled" : "Disabled",
            CloseAfter = 2.0f,
            Level = this.Opacity < 1.0 ? GrowlLevel.Success : GrowlLevel.Danger
        });
    }

    private void OnMinimizeClick(object? sender, RoutedEventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void OnMaxRestoreClick(object? sender, RoutedEventArgs e)
    {
        WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
        MaximizeRestoreIcon.Value = WindowState == WindowState.Maximized ? "fa-window-restore" : "fa-window-maximize";
    }

    private void OnCloseClick(object? sender, RoutedEventArgs e)
    {
        NotificationHandler.Instance.SendNotification(new Notification
        {
            Id = "MainWindow.Shutdown",
            Title = "ETS2LA",
            Content = "Shutting down application & backend...",
            CloseAfter = 20.0f
        });
        _pluginService.Shutdown();
        NotificationHandler.Instance.Shutdown();
        Close();
    }

    private void UpdateTitlebarButtonVisibility()
    {
        if (MainSplitView.IsPaneOpen)
        {
            ToggleSidebarIcon.Value = "fa-right-to-bracket";
            ToggleSidebarIcon.RenderTransform = new RotateTransform(180);
            TitlebarDividerLeft.IsVisible = false;
            TitlebarDividerRight.IsVisible = false;
            ManagerButtonTitlebar.IsVisible = false;
            VisualizationButtonTitlebar.IsVisible = false;
            SettingsButtonTitlebar.IsVisible = false;
        }
        else
        {
            ToggleSidebarIcon.Value = "fa-right-from-bracket";
            ToggleSidebarIcon.RenderTransform = new RotateTransform(0);
            TitlebarDividerLeft.IsVisible = true;
            TitlebarDividerRight.IsVisible = true;
            ManagerButtonTitlebar.IsVisible = true;
            VisualizationButtonTitlebar.IsVisible = true;
            SettingsButtonTitlebar.IsVisible = true;
        }
    }

    private void TogglePane(object? sender, RoutedEventArgs e)
    {
        MainSplitView.IsPaneOpen = !MainSplitView.IsPaneOpen;
        ContentBorder.CornerRadius = MainSplitView.IsPaneOpen ? new Avalonia.CornerRadius(12, 0, 0, 0) : new Avalonia.CornerRadius(0);
        UpdateTitlebarButtonVisibility();
    }

    private UserControl ClosePaneAndOpen(UserControl page)
    {
        MainSplitView.IsPaneOpen = false;
        ContentBorder.CornerRadius = new Avalonia.CornerRadius(0);
        UpdateTitlebarButtonVisibility();
        return page;
    }

    private void ShowPage(PageKind page)
    {
        ContentHost.Content = page switch
        {
            PageKind.Dashboard => _dashboardView,
            PageKind.Manager => _managerView,
            PageKind.Visualization => IsWindows ? ClosePaneAndOpen(_visualizationView) : CreatePlaceholder("Sorry", "This page is only available on Windows."),
            PageKind.Game => _gameView,
            PageKind.Catalogue => CreatePlaceholder("Catalogue", "List plugins, tools, or assets here when available."),
            PageKind.Performance => CreatePlaceholder("Performance", "Performance metrics and graphs will be shown here."),
            PageKind.Wiki => CreatePlaceholder("Wiki", "Link or embed documentation content."),
            PageKind.Roadmap => CreatePlaceholder("Roadmap", "Timeline and milestones will appear here."),
            PageKind.Feedback => CreatePlaceholder("Feedback", "Collect feedback or link to forms."),
            PageKind.Settings => _settingsView,
            _ => _dashboardView
        };
    }

    private Control CreatePlaceholder(string title, string body)
    {
        return new Border {
            Padding = new Avalonia.Thickness(20),
            Child = new ScrollViewer
            {
                Content = new StackPanel
                {
                    Spacing = 8,
                    Children =
                    {
                        new TextBlock { Text = title, FontSize = 18, FontWeight = Avalonia.Media.FontWeight.SemiBold },
                        new TextBlock { Text = body, TextWrapping = Avalonia.Media.TextWrapping.Wrap }
                    }
                }
            }
        };
    }

    private void SetSelected(Button active)
    {
        foreach (var button in _navButtons)
        {
            button.Classes.Remove("Selected");
        }
        active.Classes.Add("Selected");
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

    private void OnGameClick(object? sender, RoutedEventArgs e)
    {
        SetSelected(GameButton);
        ShowPage(PageKind.Game);
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
