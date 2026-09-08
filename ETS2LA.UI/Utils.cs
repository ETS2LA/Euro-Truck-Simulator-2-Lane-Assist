using ETS2LA.Logging;
using System.Diagnostics;
using Photino.NET;
using static ETS2LA.Translations.T;
using System.Runtime.InteropServices;

namespace ETS2LA.UI;

public static class UserInterfaceUtils
{
    public static string ClassnameWithSpaces(string option)
    {
        return System.Text.RegularExpressions.Regex.Replace(
            option, 
            @"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])|(?<=[A-Z])(?=[A-Z][a-z])", 
            " "
        );
    }

    // Source - https://stackoverflow.com/a/43232486
    // Posted by Joel Harkes, modified by community. See post 'Timeline' for change history
    // Retrieved 2026-09-08, License - CC BY-SA 4.0
    public static void OpenUrl(string url)
    {
        try
        {
            Process.Start(url);
        }
        catch
        {
            // hack because of this: https://github.com/dotnet/corefx/issues/10361
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                url = url.Replace("&", "^&");
                Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                Process.Start("xdg-open", url);
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
            {
                Process.Start("open", url);
            }
            else
            {
                throw;
            }
        }
    }

    public static void AskForRestart(string title, string message)
    {
        if(UserInterface.Current.Window.ShowMessage(
            _("Restart Required"), 
            _("Changing this option requires a restart of ETS2LA to take effect. Restart now?"), 
            PhotinoDialogButtons.YesNo
        ) == PhotinoDialogResult.Yes)
        {
            UserInterfaceUtils.Restart();
        }
    }

    public static void Restart()
    {
        Logger.Info(_("Restarting ETS2LA..."));
        UserInterface.Current.Window.Close();
        
        using Process currentProcess = Process.GetCurrentProcess();
        var startInfo = new ProcessStartInfo
        {
            FileName = currentProcess.MainModule?.FileName,
            UseShellExecute = true
        };

        // Let the new instance wait for this process to exit.
        startInfo.ArgumentList.Add($"--restart-parent-process-id={currentProcess.Id}");
        Process.Start(startInfo);
    }
}