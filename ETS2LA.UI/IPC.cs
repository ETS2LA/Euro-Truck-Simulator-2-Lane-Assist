using Photino.Blazor;
using Photino.NET;
using System.Drawing;
using ETS2LA.Backend.Events;
using ETS2LA.Logging;
using static ETS2LA.Translations.T;

namespace ETS2LA.UI;

static class IPC
{
    public static void HandleMessage(string message, object sender, PhotinoBlazorApp app)
    {
        if (message.StartsWith("window:moveBy:"))
        {
            var parts = message.Replace("window:moveBy:", "").Split(',');
            if (parts.Length == 2 && int.TryParse(parts[0], out int dx) && int.TryParse(parts[1], out int dy))
            {
                var loc = app.MainWindow.Location;
                app.MainWindow.SetLocation(new Point(loc.X + dx, loc.Y + dy));
            }
            return;
        }

        if (message.StartsWith("window:setSize:"))
        {
            var parts = message.Replace("window:setSize:", "").Split(',');
            if (parts.Length == 2 && int.TryParse(parts[0], out int w) && int.TryParse(parts[1], out int h))
            {
                app.MainWindow.SetSize(w, h);
            }
            return;
        }

        if (message.StartsWith("window:zoom"))
        {
            var parts = message.Replace("window:zoom:", "").Split(',');
            if (parts.Length == 1 && int.TryParse(parts[0], out int zoom))
            {
                WindowSettings.Current.Zoom = zoom;
                WindowSettings.Current.Save();
                app.MainWindow.SetZoom(zoom);
            }
            return;
        }

        switch (message)
        {
            case "window:minimize":
                app.MainWindow.SetMinimized(true);
                break;
            case "window:maximize":
                app.MainWindow.SetMaximized(!app.MainWindow.Maximized);
                break;
            case "window:close":
                if (app.MainWindow.ShowMessage(_("Are you sure?"), _("This will disconnect ETS2LA from the game and close the window. You can minimize the window to keep ETS2LA running."), PhotinoDialogButtons.YesNo, PhotinoDialogIcon.Question) == PhotinoDialogResult.Yes)
                    app.MainWindow.Close();
                break;
            case "window:topmost":
                // TODO
                break;
            case "window:notopmost":
                // TODO
                break;
        }
    }
}