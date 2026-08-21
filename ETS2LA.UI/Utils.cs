using ETS2LA.Logging;
using System.Diagnostics;
using Photino.NET;
using static ETS2LA.Translations.T;

namespace ETS2LA.UI;

public static class UserInterfaceUtils
{
    public static string ClassnameWithSpaces(string option)
    {
        return System.Text.RegularExpressions.Regex.Replace(option, @"(\B[A-Z]|(?<=[a-zA-Z])\d)", " $1");
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