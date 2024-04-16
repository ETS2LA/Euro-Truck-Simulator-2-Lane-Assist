"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Settings", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Global settings.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.console as console
import win32gui, win32con, win32console

global crashreportvar

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def reinstall(self):
            for plugin in settings.GetSettings("Plugins", "Installed"):
                settings.RemoveFromList("Plugins", "Installed", plugin)
            
            from tkinter import messagebox
            helpers.ShowInfo("All plugins will be reinstalled on next startup. The application will now close.", title="Reinstall")
            mainUI.quit()
            
        def exampleFunction(self):
            global crashreportvar
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass

            self.root = tk.Canvas(self.master, width=600, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeLabel(self.root, "Categories", 0,0, padx=30, pady=10, font=("Segoe UI", 16, "bold"), autoplace=True)
            helpers.MakeButton(self.root, "Translation Settings", lambda: mainUI.switchSelectedPlugin("plugins.DeepTranslator.main"), 5,0, padx=30, pady=10, width=20, autoplace=True)
            helpers.MakeButton(self.root, "UI Settings", lambda: mainUI.switchSelectedPlugin("plugins.TabSettings.main"), 6,1, padx=30, pady=10, width=20, autoplace=True)
            helpers.MakeButton(self.root, "Themes", lambda: mainUI.switchSelectedPlugin("plugins.ThemeManager.main"), 5,0, padx=30, pady=10, width=20, autoplace=True)
            
            helpers.MakeLabel(self.root, "Global Settings", 2,0, padx=30, pady=10, font=("Segoe UI", 16, "bold"), autoplace=True)
            self.updateRate = helpers.MakeComboEntry(self.root, "UI Update Every x Frames", "User Interface", "updateRate", 1,0, value=4, labelwidth=25, width=25, autoplace=True)
            self.awareness = helpers.MakeComboEntry(self.root, "DPI mode (0/1/2)", "User Interface", "DPIAwareness", 2,0, value=0, labelwidth=25, width=25, autoplace=True)
            
            helpers.MakeCheckButton(self.root, "Print Debug", "logger", "debug", 3,0, width=20, autoplace=True, callback=self.save)
            helpers.MakeCheckButton(self.root, "Print UI Debug", "Dev", "print_ui_events", 3,1, width=20, autoplace=True, callback=self.save)
            self.crashreport = helpers.MakeCheckButton(self.root, "Send Crash Data", "CrashReporter", "AllowCrashReports",4,0, width=20, autoplace=True, callback=self.show_crashreports_info)
            helpers.MakeCheckButton(self.root, "Hide Console", "User Interface", "hide_console", 4,1, width=20, autoplace=True, callback=self.save)
            
            helpers.MakeButton(self.root, "Reload", lambda: self.reload(), 7,0, padx=30, pady=10, width=20, autoplace=True)
            helpers.MakeButton(self.root, "Open Installer Menu", lambda: self.open_menu(), 7,1, padx=30, pady=10, width=20, autoplace=True)
            helpers.MakeButton(self.root, "Reinstall plugins", lambda: self.reinstall(), 6,0, padx=30, pady=10, width=20, autoplace=True)
            helpers.MakeButton(self.root, "Reload Plugins", lambda: variables.ReloadAllPlugins(), 7,1, padx=30, pady=10, width=20, autoplace=True)

            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def save(self): # This function is called when the user presses the "Save & Quit" button
            settings.CreateSettings("User Interface", "updateRate", self.updateRate.get())
            if settings.GetSettings("User Interface", "DPIAwareness") != self.awareness.get():
                settings.CreateSettings("User Interface", "DPIAwareness", self.awareness.get())
                helpers.ShowInfo("You need to restart the app for the DPI mode to take effect.", title="Restart required")
            # settings.CreateSettings("Plugins", "Ignore", self.ignore.get())
            if settings.GetSettings("User Interface", "hide_console") == False:
                console.RestoreConsole()
            if settings.GetSettings("User Interface", "hide_console") == True:
                console.HideConsole()

        def open_menu(self):
            import os
            if os.path.exists(os.path.dirname(os.path.dirname(variables.PATH)) + "\menu.bat"):
                import subprocess
                subprocess.Popen(os.path.dirname(os.path.dirname(variables.PATH)) + "\menu.bat")
            else:
                helpers.Dialog("Information","The menu.bat file could not be found.\nNote: Only available for app installations before version 1.11.0.", ["Exit"], "Exit")

        def show_crashreports_info(self):
            if self.crashreport.get():
                CrashReportWindow = helpers.AskOkCancel("CrashReporter", "Toggling this setting will send all crash data to the developers.\nNo personal information is sent, and all paths have the username censored.\nWe take all crash reports seriously and will try and fix all crashes ASAP.\n\nTIP: You can also use the Feedback page to send more detailed info.\n\nDo you want to enable the crash reporting?", yesno=True) 
                if CrashReportWindow == True:
                    settings.CreateSettings("CrashReporter", "AllowCrashReports", True)
                else: 
                    settings.CreateSettings("CrashReporter", "AllowCrashReports", False)
                    self.exampleFunction()
            else:
                settings.CreateSettings("CrashReporter", "AllowCrashReports", False)
        
        def reload(self):
            variables.RELOAD = True

        def update(self, data): # When the panel is open this function is called each frame 
            if self.updateRate.get() != settings.GetSettings("User Interface", "updateRate"):
                self.save()
            if self.awareness.get() != settings.GetSettings("User Interface", "DPIAwareness"):
                self.save()
            self.root.update()
    
    except Exception as ex:
        print(ex.args)
