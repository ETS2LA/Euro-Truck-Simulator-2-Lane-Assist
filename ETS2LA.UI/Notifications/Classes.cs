using Huskui.Avalonia.Controls;
using Huskui.Avalonia.Models;

namespace ETS2LA.UI.Notifications;

/// <summary>
    ///  Represents a notification sent in the bottom right corner of the ETS2LA UI.
    ///  Uses Huskui's GrowlItem system.
    /// </summary>
    public class UINotification
    {
        /// <summary>
        ///  A unique identifier for this notification. For example: ExampleConsumer.SteeringOutput.
        /// </summary>
        public required string Id;
        /// <summary>
        ///  Indicates this notification was made by the notification system. Do not use.
        /// </summary>
        public bool IsInternal = false;
        /// <summary>
        ///  The time this notification was created, can be edited, but set to the current time by default.
        /// </summary>
        public DateTime CreatedAt = DateTime.UtcNow;
        /// <summary>
        ///  The GrowlItem this notification represents. Set by the notification system, don't use.
        /// </summary>
        public GrowlItem? Item = null;

        /// <summary>
        ///  The level of the notification, affects the color shown. <br/>
        ///  using Huskui.Avalonia.Models;     <br/>
        ///  GrowlLevel.Information; // Blue   <br/>
        ///  GrowlLevel.Success;     // Green  <br/>
        ///  GrowlLevel.Warning;     // Yellow <br/>
        ///  GrowlLevel.Danger;      // Red    <br/>
        /// </summary>
        public GrowlLevel Level = GrowlLevel.Information;
        /// <summary>
        ///  The title of the notification.
        /// </summary>
        public string Title = "";
        /// <summary>
        ///  The content of the notification.
        /// </summary>
        public string Content = "";

        /// <summary>
        ///  The progress of the notification progress bar. From 0.0f to 100.0f. <br/>
        ///  **NOTE**: Remember to set the `CloseAfter` parameter if you want to manually edit the progress bar! 
        /// </summary>
        public float Progress = 0.0f;
        /// <summary>
        ///  Whether the progress is indeterminate (i.e. a loading bar with no specified state).
        /// </summary>
        public bool IsProgressIndeterminate = false;

        /// <summary>
        ///  The time in seconds after which the notification will automatically close. <br/>
        ///  **NOTE**: Set to 0.0f if you want to manually edit the progress bar!
        /// </summary>
        public float CloseAfter = 8.0f; // seconds
        /// <summary>
        ///  The time in seconds after which the close button will be shown if CloseAfter is not set.
        /// </summary>
        public float ShowCloseButtonAfter = 0.0f; // seconds
    }