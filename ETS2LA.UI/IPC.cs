using Photino.NET;
using System.Drawing;
using ETS2LA.Backend.Events;

namespace ETS2LA.UI;

static class IPC
{
    public static void HandleMessage(string message, PhotinoWindow window)
    {
        if (message.StartsWith("event:"))
        {
            var eventData = message.Replace("event:", "");
            var eventName = eventData.Split(':')[0];
            var eventPayload = eventData.Substring(eventName.Length + 1);
            Events.Current.Publish(eventName, eventPayload);
        }
        if (message.StartsWith("window:moveBy:"))
        {
            var parts = message.Replace("window:moveBy:", "").Split(',');
            if (parts.Length == 2 && int.TryParse(parts[0], out int dx) && int.TryParse(parts[1], out int dy))
            {
                var loc = window.Location;
                window.SetLocation(new Point(loc.X + dx, loc.Y + dy));
            }
            return;
        }

        if (message.StartsWith("window:setSize:"))
        {
            var parts = message.Replace("window:setSize:", "").Split(',');
            if (parts.Length == 2 && int.TryParse(parts[0], out int w) && int.TryParse(parts[1], out int h))
            {
                window.SetSize(w, h);
            }
            return;
        }

        switch (message)
        {
            case "window:minimize":
                window.SetMinimized(true);
                break;
            case "window:maximize":
                window.SetMaximized(!window.Maximized);
                break;
            case "window:close":
                if (window.ShowMessage("Are you sure?", "This will disconnect ETS2LA from the game and close the window. You can minimize the window to keep ETS2LA running.", PhotinoDialogButtons.YesNo, PhotinoDialogIcon.Question) == PhotinoDialogResult.Yes)
                    window.Close();
                break;
            case "window:focus":
                window.SetTopMost(true);
                window.SetTopMost(false);
                break;
        }
    }
}