using Avalonia.Controls;
using Huskui.Avalonia.Models;

using ETS2LA.Shared;
using ETS2LA.Backend.Updates;
using ETS2LA.UI.Notifications;

using Velopack;
using System.ComponentModel;

namespace ETS2LA.UI.Views.Settings;

public partial class Updates : UserControl, INotifyPropertyChanged
{
    private Updater _updater;

    public string CurrentVersion { get; set; } = "Unknown";
    public bool IsUpdateAvailable => LatestUpdateInfo != null;
    public string LatestVersion => LatestUpdateInfo != null ? $"v{LatestUpdateInfo.TargetFullRelease.Version}" : "N/A";
    public string ReleaseNotes => GetReleaseNotes();

    public UpdateInfo? LatestUpdateInfo { get; set; }
    public event PropertyChangedEventHandler? PropertyChanged;

    public Updates()
    {
        _updater = Updater.Current;
        CurrentVersion = $"v{_updater.UpdateManager.CurrentVersion}";
        InitializeComponent();
        DataContext = this;
        MainWindow.WindowOpened += (s, e) => OnCheckForUpdatesClick(this, new Avalonia.Interactivity.RoutedEventArgs());
    }

    private string GetReleaseNotes()
    {
        if(LatestUpdateInfo == null)
        {
            return "No release notes available.";
        }

        if (string.IsNullOrEmpty(LatestUpdateInfo.TargetFullRelease.NotesMarkdown))
        {
            return "No release notes available.";
        }

        return LatestUpdateInfo.TargetFullRelease.NotesMarkdown;
    }

    public void OnCheckForUpdatesClick(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        NotificationHandler.Current.SendNotification(new Notification
        {
            Id = "UpdateNotification",
            Title = "Checking for Updates",
            Content = "Please wait while we check for updates...",
            Level = GrowlLevel.Information,
            CloseAfter = 0,
            IsProgressIndeterminate = true
        });
        Task.Run(() => {
            LatestUpdateInfo = _updater.CheckForUpdates();
            if (LatestUpdateInfo != null)
            {
                NotificationHandler.Current.SendNotification(new Notification
                {
                    Id = "UpdateNotification",
                    Title = "Update Available",
                    Content = $"A new version is available: {LatestUpdateInfo.TargetFullRelease.Version}",
                    Level = GrowlLevel.Success,
                    CloseAfter = 5,
                    IsProgressIndeterminate = false
                });
                OnPropertyChanged(nameof(IsUpdateAvailable));
                OnPropertyChanged(nameof(LatestVersion));
                OnPropertyChanged(nameof(LatestUpdateInfo));
                OnPropertyChanged(nameof(ReleaseNotes));
            }
            else
            {
                NotificationHandler.Current.SendNotification(new Notification
                {
                    Id = "UpdateNotification",
                    Title = "No Update Available",
                    Content = "You are using the latest version.",
                    Level = GrowlLevel.Information,
                    CloseAfter = 5,
                    IsProgressIndeterminate = false
                });
            }
        });
    }

    private void DownloadCallback(int progress)
    {
        NotificationHandler.Current.SendNotification(new Notification
        {
            Id = "UpdateDownloadProgress",
            Title = "Downloading Update",
            Content = $"Download progress: {progress}%",
            Level = GrowlLevel.Information,
            Progress = progress,
            CloseAfter = 0
        });
    }

    public void OnInstallAndRestartClick(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        if (LatestUpdateInfo != null)
        {
            Task.Run(() => 
            {
                NotificationHandler.Current.SendNotification(new Notification
                {
                    Id = "UpdateDownloadProgress",
                    Title = "Downloading Update",
                    Content = $"Starting download...",
                    Level = GrowlLevel.Information,
                    Progress = 0,
                    CloseAfter = 0
                });
                _updater.DownloadUpdates(LatestUpdateInfo, DownloadCallback);
                _updater.ApplyUpdatesAndRestart(LatestUpdateInfo);
                NotificationHandler.Current.CloseNotification("UpdateDownloadProgress");
            });
        }
    }

    protected virtual void OnPropertyChanged(string propertyName)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
