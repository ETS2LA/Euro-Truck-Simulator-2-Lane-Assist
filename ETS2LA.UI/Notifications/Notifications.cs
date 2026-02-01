using ETS2LA.Shared;
using ETS2LA.Logging;
using Avalonia.Threading;
using Huskui.Avalonia.Controls;
using Avalonia.LogicalTree;

namespace ETS2LA.UI.Notifications;

/// <summary>
///  This class handles in-app notifications.
///  Access it with `NotificationHandler.Current`.
/// </summary>
public class NotificationHandler : INotificationHandler
{
    private static readonly Lazy<NotificationHandler> _instance = new(() => new NotificationHandler());
    /// <summary>
    ///  This Instance property gives access to the ETS2LA-wide notification handler instance.
    ///  No matter where this is called from, it will always return the same instance.
    /// </summary>
    public static NotificationHandler Current => _instance.Value;

    private AppWindow? _window;
    private bool _isRunning = true;
    public List<Notification> ActiveNotifications { get; private set; } = new();

    public NotificationHandler()
    {
        Task.Run(WatcherThread);
    }

    public void SetWindow(AppWindow window)
    {
        _window = window;
    }

    public void WatcherThread()
    {
        while (_isRunning)
        {
            var now = DateTime.UtcNow;
            var toClose = new List<string>();
            foreach (var notif in ActiveNotifications)
            {
                if (notif.IsProgressIndeterminate || notif.CloseAfter <= 0.0f)
                    continue; // skip progress notifs

                float timeElapsed = (float)(now - notif.CreatedAt).TotalSeconds;
                float progress = timeElapsed / notif.CloseAfter * 100; // (0.0 to 100.0)

                if (notif.CloseAfter > 0.0f)
                {
                    Notification clone = new Notification
                    {
                        Id = notif.Id,
                        Title = notif.Title,
                        Content = notif.Content,
                        Level = notif.Level,
                        Progress = progress,
                        IsProgressIndeterminate = false,
                        CloseAfter = notif.CloseAfter,
                        ShowCloseButtonAfter = notif.ShowCloseButtonAfter,
                        CreatedAt = notif.CreatedAt,
                        IsInternal = true
                    };
                    SendNotification(clone);
                }

                if (notif.CloseAfter > 0.0f && timeElapsed >= notif.CloseAfter)
                {
                    toClose.Add(notif.Id);
                }
            }

            foreach (var id in toClose)
            {
                CloseNotification(id);
            }

            Thread.Sleep(50);
        }
    }

    public void Shutdown()
    {
        _isRunning = false;
    }

    public void UpdateNotification(Notification notification)
    {
        if (!Dispatcher.UIThread.CheckAccess())
        {
            Dispatcher.UIThread.Post(() => UpdateNotification(notification));
            return;
        }

        var toUpdate = ActiveNotifications.FirstOrDefault(x => x.Id == notification.Id);
        if (toUpdate != null)
        {
            toUpdate.Item?.Title = notification.Title;
            toUpdate.Item?.Content = notification.Content;
            toUpdate.Item?.Level = notification.Level;
            toUpdate.Item?.Progress = notification.Progress;
            toUpdate.Item?.IsProgressIndeterminate = notification.IsProgressIndeterminate;
            toUpdate.Item?.IsCloseButtonVisible = notification.CloseAfter <= 0.0f; // show if not automatic
            toUpdate.Item?.IsProgressBarVisible = notification.Progress >= 0.0f || notification.IsProgressIndeterminate;

            if (!notification.IsInternal)
            {
                toUpdate.Title = notification.Title;
                toUpdate.Content = notification.Content;
                toUpdate.Level = notification.Level;
                toUpdate.Progress = notification.Progress;
                toUpdate.IsProgressIndeterminate = notification.IsProgressIndeterminate;
                toUpdate.CloseAfter = notification.CloseAfter;
                toUpdate.ShowCloseButtonAfter = notification.ShowCloseButtonAfter;
                toUpdate.CreatedAt = DateTime.UtcNow;
            }
        }
    }

    public async void SendNotification(Notification notification)
    {
        if (!_window.IsLoaded) {
            Logger.Warn("Attempted to send notification before MainWindow was loaded.");
            return;
        }

        // Switch to UI thread as this will probably be 
        // called from a plugin thread. Code gets stuck at creating the notif 
        // if we don't do this.
        try
        {
            await Dispatcher.UIThread.InvokeAsync(() =>
            {
                if (ActiveNotifications.Any(x => x.Id == notification.Id))
                {
                    UpdateNotification(notification);
                    return;
                }

                GrowlHost? growlHost = _window.GetLogicalChildren().OfType<GrowlHost>().FirstOrDefault();
                if (growlHost == null) return;

                GrowlItem item = new GrowlItem
                {
                    Title = notification.Title,
                    Content = notification.Content,
                    Level = notification.Level,
                    Progress = notification.Progress,
                    IsProgressIndeterminate = notification.IsProgressIndeterminate,
                    IsCloseButtonVisible = notification.CloseAfter <= 0.0f, // show if not automatic
                    IsProgressBarVisible = notification.Progress >= 0.0f || notification.IsProgressIndeterminate
                };

                notification.Item = item;
                growlHost.Pop(notification.Item);
                ActiveNotifications.Add(notification);
            });
        } catch (Exception ex)
        {
            Logger.Error($"Failed to send notification '{notification.Title}': {ex}");
        }
    }

    public void CloseNotification(string id)
    {
        if (!Dispatcher.UIThread.CheckAccess())
        {
            Dispatcher.UIThread.Post(() => CloseNotification(id));
            return;
        }

        var toRemove = ActiveNotifications.FirstOrDefault(x => x.Id == id);
        if (toRemove != null)
        {
            toRemove.Item?.Dismiss();
            ActiveNotifications.Remove(toRemove);
        }
    }
}