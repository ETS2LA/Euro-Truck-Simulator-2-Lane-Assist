namespace ETS2LA.Notifications;

public class NotificationHandler
{
    private static readonly Lazy<NotificationHandler> _instance = new(() => new NotificationHandler());
    /// <summary>
    ///  This Instance property gives access to the ETS2LA-wide notification handler instance.
    ///  No matter where this is called from, it will always return the same instance.
    /// </summary>
    public static NotificationHandler Current => _instance.Value;

    public List<Notification> ActiveNotifications { get; private set; } = new();

    public event EventHandler<Notification> OnNotificationAdded;
    public event EventHandler<Notification> OnNotificationUpdated;
    public event EventHandler<string> OnNotificationRemoved;

    public NotificationHandler() {}

    public void UpdateNotification(Notification notification)
    {
        var toUpdate = ActiveNotifications.FirstOrDefault(x => x.Id == notification.Id);
        if (toUpdate != null)
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

        OnNotificationUpdated?.Invoke(this, notification);
    }

    public void SendNotification(Notification notification)
    {
        ActiveNotifications.Add(notification);
        OnNotificationAdded?.Invoke(this, notification);
    }

    public void CloseNotification(string id)
    {
        var toRemove = ActiveNotifications.FirstOrDefault(x => x.Id == id);
        if (toRemove != null)
        {
            ActiveNotifications.Remove(toRemove);
            OnNotificationRemoved?.Invoke(this, id);
        }
    }

    public List<Notification> GetActiveNotifications()
    {
        return ActiveNotifications;
    }
}