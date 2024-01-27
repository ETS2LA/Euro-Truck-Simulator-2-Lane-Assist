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
import os
import win32gui, win32con

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
            messagebox.showinfo("Reinstall", "All plugins will be reinstalled on next startup. The application will now close.")
            mainUI.quit()
            
        def exampleFunction(self):
            global crashreportvar
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass

            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.updateRate = helpers.MakeComboEntry(self.root, "UI Update Every x Frames", "User Interface", "updateRate", 1,0, value=4, labelwidth=25, width=25)
            self.awareness = helpers.MakeComboEntry(self.root, "DPI mode (0/1/2)", "User Interface", "DPIAwareness", 2,0, value=0, labelwidth=25, width=25)
            # self.ignore = helpers.MakeComboEntry(self.root, "Ignore Modules (seperate by ,)", "Plugins", "Ignore", 2,0, value="EvdevController," if os.name != "nt" else "DXCamScreenCapture,", labelwidth=25, isString=True, width=55)
            
            self.printDebug = helpers.MakeCheckButton(self.root, "Print Debug", "logger", "debug", 3,0, width=20)

            helpers.MakeCheckButton(self.root, "Hide Console", "User Interface", "hide_console", 3,1, width=20)
        
            crashreportvar = tk.BooleanVar()
            crashreportvar.set(settings.GetSettings("CrashReporter", "AllowCrashReports", False))
            crashreport = ttk.Checkbutton(self.root, text="Send crash data", variable=crashreportvar, width=20)
            crashreport.grid(row=4, column=0, padx=0, pady=7, sticky="w")

            
            helpers.MakeButton(self.root, "Translation Settings", lambda: mainUI.switchSelectedPlugin("plugins.DeepTranslator.main"), 5,0, padx=30, pady=10, width=20)
            
            helpers.MakeButton(self.root, "Themes", lambda: mainUI.switchSelectedPlugin("plugins.ThemeManager.main"), 5,1, padx=30, pady=10, width=20)
            
            helpers.MakeButton(self.root, "Reinstall all plugins", lambda: self.reinstall(), 6,0, padx=30, pady=10, width=20)
            
            # Use the mainUI.quit() function to quit the app
            helpers.MakeButton(self.root, "UI Settings", lambda: mainUI.switchSelectedPlugin("plugins.TabSettings.main"), 6,1, padx=30, pady=10, width=20)
            
            helpers.MakeButton(self.root, "Reload Plugins", lambda: variables.ReloadAllPlugins(), 7,0, padx=30, pady=10, width=20)

            helpers.MakeButton(self.root, "Save & Reload", lambda: self.save(), 7,1, padx=30, pady=10, width=20)
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def save(self): # This function is called when the user presses the "Save & Quit" button
            global crashreportvar
            settings.CreateSettings("User Interface", "updateRate", self.updateRate.get())
            if settings.GetSettings("User Interface", "DPIAwareness") != self.awareness.get():
                settings.CreateSettings("User Interface", "DPIAwareness", self.awareness.get())
                tk.messagebox.showinfo("Restart required", "You need to restart the app for the DPI mode to take effect.")
            # settings.CreateSettings("Plugins", "Ignore", self.ignore.get())
            if settings.GetSettings("User Interface", "hide_console") == False:
                win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_RESTORE)
            if settings.GetSettings("User Interface", "hide_console") == True:
                if variables.CONSOLENAME == None:
                    window_found = False
                    target_text = "/venv/Scripts/python"
                    top_windows = []
                    win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
                    for hwnd, window_text in top_windows:
                        if target_text in window_text:
                            window_found = True
                            variables.CONSOLENAME = hwnd
                            break
                    if window_found == False:
                        print("Console window not found, unable to hide!")
                    else:
                        print(f"Console Name: {window_text}, Console ID: {hwnd}")
                        win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_HIDE)
                else:
                    win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_HIDE)
            print(crashreportvar.get())
            if crashreportvar.get():
                CrashReportWindow = tk.messagebox.askokcancel("CrashReporter", "This will send anonymous crash report data to the developers.\nThis can help improve the app and fix any bugs that are found.\n This will send only the error that caused the app to crash.\n Your name and person info will be censored.\n\nDo you want to continue?", icon="warning") 
                if CrashReportWindow == True:
                    settings.CreateSettings("CrashReporter", "AllowCrashReports", True)
                else: 
                    settings.CreateSettings("CrashReporter", "AllowCrashReports", False)
            else:
                settings.CreateSettings("CrashReporter", "AllowCrashReports", False)
            
            variables.RELOAD = True
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
