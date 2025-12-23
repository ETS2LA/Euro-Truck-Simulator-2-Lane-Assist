// TODO: This file is WIP and needs to be reviewed and tested.
// The datastructure needs changes before pushing to production
// for clarity and easier use!
using ETS2LA.Shared;
using ETS2LA.Logging;
using Avalonia.Threading;
using Huskui.Avalonia.Controls;
using Avalonia.LogicalTree;

namespace ETS2LA.UI.Notifications;

public class NotificationHandler : INotificationHandler
{
    private readonly AppWindow _window;
    private bool _isRunning = true;
    public List<Tuple<string, GrowlItem, Notification>> ActiveNotifications { get; } = new();

    public NotificationHandler(AppWindow window)
    {
        _window = window;
        Task.Run(WatcherThread);

        _window.Loaded += (s, e) =>
        {
            SendNotification(new Notification
            {
                Id = "app_loaded",
                Title = "ETS2LA",
                Content = "Application & Backend started successfully.",
            });
        };
    }

    public void WatcherThread()
    {
        while (_isRunning)
        {
            var now = DateTime.UtcNow;
            var toClose = new List<string>();
            foreach (var notif in ActiveNotifications)
            {
                if (notif.Item3.IsProgressIndeterminate || notif.Item3.CloseAfter <= 0.0f)
                    continue; // skip progress notifs

                float timeElapsed = (float)(now - notif.Item3.CreatedAt).TotalSeconds;
                float progress = timeElapsed / notif.Item3.CloseAfter * 100; // (0.0 to 100.0)

                if (notif.Item3.CloseAfter > 0.0f)
                {
                    Notification clone = new Notification
                    {
                        Id = notif.Item3.Id,
                        Title = notif.Item3.Title,
                        Content = notif.Item3.Content,
                        Level = notif.Item3.Level,
                        Progress = progress,
                        IsProgressIndeterminate = false,
                        CloseAfter = notif.Item3.CloseAfter,
                        ShowCloseButtonAfter = notif.Item3.ShowCloseButtonAfter,
                        CreatedAt = notif.Item3.CreatedAt,
                        IsInternal = true
                    };
                    SendNotification(clone);
                }

                if (notif.Item3.CloseAfter > 0.0f && timeElapsed >= notif.Item3.CloseAfter)
                {
                    toClose.Add(notif.Item1);
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

        var toUpdate = ActiveNotifications.FirstOrDefault(x => x.Item1 == notification.Id);
        if (toUpdate != null)
        {
            toUpdate.Item2.Title = notification.Title;
            toUpdate.Item2.Content = notification.Content;
            toUpdate.Item2.Level = notification.Level;
            toUpdate.Item2.Progress = notification.Progress;
            toUpdate.Item2.IsProgressIndeterminate = notification.IsProgressIndeterminate;
            toUpdate.Item2.IsCloseButtonVisible = notification.CloseAfter <= 0.0f; // show if not automatic
            toUpdate.Item2.IsProgressBarVisible = notification.Progress >= 0.0f || notification.IsProgressIndeterminate;

            if (!notification.IsInternal)
            {
                toUpdate.Item3.Title = notification.Title;
                toUpdate.Item3.Content = notification.Content;
                toUpdate.Item3.Level = notification.Level;
                toUpdate.Item3.Progress = notification.Progress;
                toUpdate.Item3.IsProgressIndeterminate = notification.IsProgressIndeterminate;
                toUpdate.Item3.CloseAfter = notification.CloseAfter;
                toUpdate.Item3.ShowCloseButtonAfter = notification.ShowCloseButtonAfter;
                toUpdate.Item3.CreatedAt = DateTime.UtcNow;
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
        await Dispatcher.UIThread.InvokeAsync(() =>
        {
            if (ActiveNotifications.Any(x => x.Item1 == notification.Id))
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
            
            growlHost.Pop(item);
            ActiveNotifications.Add(new Tuple<string, GrowlItem, Notification>(notification.Id, item, notification));
        });
    }

    public void CloseNotification(string id)
    {
        if (!Dispatcher.UIThread.CheckAccess())
        {
            Dispatcher.UIThread.Post(() => CloseNotification(id));
            return;
        }

        var toRemove = ActiveNotifications.FirstOrDefault(x => x.Item1 == id);
        if (toRemove != null)
        {
            toRemove.Item2.Dismiss();
            ActiveNotifications.Remove(toRemove);
        }
    }
}