"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="MainMenu", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    # In case the plugin is not the main file (for example plugins\Panel\Panel.py) then the name would be "Panel.Panel"
    
    description="The main menu of the app.",
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
import src.server as server
from src.translator import Translate
import os
import time
from tkinter.font import families

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            
            try:
                self.motd = server.GetMotd().replace("\n", " ")
                self.motd = Translate(self.motd)
            except:
                pass
            
            self.motdUpdateTime = 0
            self.motdScrollTime = 0
            self.motdScrollPosition = 0
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=1, height=1, border=0, highlightthickness=0)
            #self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            #self.root.pack_propagate(0)
            
            # Make a label to offset the text and buttons to the center of the frame
            helpers.lastParent = self.root
            helpers.defaultAutoplaceColumn = 1
            helpers.MakeEmptyLine(self.root, 0, 1, columnspan=2, autoplace=True, fontSize=1)
            helpers.MakeLabel(self.root, f"You are running ETS2LA version {str(variables.VERSION)}", 0, 1, columnspan=2, font=("Roboto", 18, "bold"), autoplace=True)
            # date text, month, date, time, year
            try:
                updateTime = str(variables.LASTUPDATE).split(" ")
                updateTime = updateTime[1:]
                months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct":10, "Nov": 11, "Dec": 12}
                updateTime[0] = months[updateTime[0]]
                updateText = f"{updateTime[1]}.{updateTime[0]}.{updateTime[3]} - {updateTime[2]} "
            except:
                import traceback
                traceback.print_exc()
                updateText = "-- Unknown --"
            
            helpers.MakeLabel(self.root, f"Released {updateText}", 0, 1, columnspan=2, pady=0, autoplace=True)
            
            if variables.UPDATEAVAILABLE != False:
                helpers.MakeLabel(self.root, "An update is available!", 0, 1, columnspan=2, fg="green", autoplace=True, tooltip=f"New version: {'.'.join(variables.UPDATEAVAILABLE)}\nRestart to update.")
            else: 
                helpers.MakeEmptyLine(self.root, 0, 1, columnspan=2, autoplace=True, fontSize=3)
            
            from plugins.Wiki.main import LoadURL
            helpers.MakeButton(self.root, "Panel Manager", lambda: mainUI.switchSelectedPlugin("plugins.PanelManager.main"), 0, 1, width=20, autoplace=True)
            helpers.MakeButton(self.root, "Plugin Manager", lambda: mainUI.switchSelectedPlugin("plugins.PluginManager.main"), 0, 2, width=20, autoplace=True)
            helpers.MakeButton(self.root, "First Time Setup", lambda: mainUI.switchSelectedPlugin("plugins.FirstTimeSetup.main"), 0, 1, width=20, style="Accent.TButton", autoplace=True)
            helpers.MakeButton(self.root, "LANGUAGE - 语言设置", lambda: mainUI.switchSelectedPlugin("plugins.DeepTranslator.main"), 0, 2, width=20, style="Accent.TButton", translate=False, autoplace=True)
            helpers.MakeButton(self.root, "Video Tutorial", lambda: LoadURL("https://www.youtube.com/watch?v=0pic0rzjvik"), 0, 1, width=20, autoplace=True, tooltip="https://www.youtube.com/watch?v=0pic0rzjvik")
            helpers.MakeButton(self.root, "ETS2LA Wiki", lambda: LoadURL("https://wiki.ets2la.com"), 0, 2, width=20, autoplace=True, tooltip="https://wiki.ets2la.com/en/LaneAssist")
            helpers.MakeEmptyLine(self.root, 0, 1, columnspan=2, autoplace=True, fontSize=3)
            helpers.MakeLabel(self.root, "You can use F5 to refresh the UI and come back to this page.\n                    (as long as the app is disabled)", 0, 1, columnspan=2, autoplace=True)
            helpers.MakeLabel(self.root, "The top of the app has all your currently open tabs.\n They can be closed with the middle mouse button.\n        (or right mouse button if so configured)", 0, 1, columnspan=2, autoplace=True)
            # Make a label to show if crash reporting is enabled or disabled
            crashReporting = settings.GetSettings("CrashReporter", "AllowCrashReports")
            if crashReporting != None:
                if crashReporting:
                    helpers.MakeLabel(self.root, "Crash reporting is enabled.", 0, 1, columnspan=2, fg="green", autoplace=True, tooltip="You can disable it in the settings if you so desire.")
                    helpers.MakeEmptyLine(self.root, 0, 1, columnspan=2, autoplace=True, fontSize=3)
                else:
                    helpers.MakeLabel(self.root, "Crash reporting is disabled.", 0, 1, columnspan=2, fg="red", autoplace=True, tooltip="You can enable it in the settings.")
                    helpers.MakeEmptyLine(self.root, 0, 1, columnspan=2, autoplace=True, fontSize=3)
                    
            self.motdLabel = helpers.MakeLabel(self.root, "Loading...", 0, 1, columnspan=2, autoplace=True, fg="gray")
            self.userCount = helpers.MakeLabel(self.root, "Loading...", 0, 1, columnspan=2, autoplace=True, fg="gray")
            
            self.root.pack(anchor="center", expand=True)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            if time.time() - self.motdUpdateTime > 60:
                self.motdUpdateTime = time.time()
                try:
                    self.motd = server.GetMotd().replace("\n", " ")
                    self.motd = Translate(self.motd)
                except Exception as ex:
                    print(ex.args)
                    
                try:
                    self.userCount.config(text=f"Users online: {server.GetUserCount()}") # Get the amount of users online
                except:
                    self.exampleFunction()
                    self.motdUpdateTime = 0
                    
            # Scroll the MOTD text horizontally
            charactersToShow = 60
            try:
                if len(self.motd) < charactersToShow:
                    self.motdLabel.config(text=self.motd)
                else:
                    if time.time() - self.motdScrollTime > 0.1:
                        self.motdScrollTime = time.time()
                        self.motdScrollPosition += 1
                        if self.motdScrollPosition > len(self.motd):
                            self.motdScrollPosition = 0
                        # Scroll the text, if we are closing the end, then mirror the start
                        if self.motdScrollPosition + charactersToShow > len(self.motd):
                            self.motdLabel.config(text=self.motd[self.motdScrollPosition:] + " " + self.motd[:charactersToShow - (len(self.motd) - self.motdScrollPosition)])
                        else:
                            self.motdLabel.config(text=self.motd[self.motdScrollPosition:self.motdScrollPosition + charactersToShow])
            except:
                pass
                    
            # Check if there are no children on the root canvas
            try:
                self.root.winfo_children()
            except:
                self.exampleFunction()
                return
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)