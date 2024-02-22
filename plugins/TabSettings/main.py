"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="TabSettings", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="ExamplePanel.",
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

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def saveAndReload(self):
            # settings.UpdateSettings("User Interface", "CustomKey", self.customKey.get())
            variables.RELOAD = True
        
        def clearAndReload(self):
            settings.UpdateSettings("User Interface", "OpenTabs", [])
            variables.RELOAD = True
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeLabel(self.root, "Tab Settings", 0,0, sticky="w")
            helpers.MakeCheckButton(self.root, "Reopen tabs on restart", "User Interface", "ReopenTabs", 1,0, width=40, default=True)
            helpers.MakeCheckButton(self.root, "Close tab on middle mouse button", "User Interface", "CloseTabMMB", 2,0, width=40, default=True)
            helpers.MakeCheckButton(self.root, "Close tab on right mouse button", "User Interface", "CloseTabRMB", 2,1, width=40, default=False)
            #if settings.GetSettings("User Interface", "CustomKey") == None:
            #    settings.CreateSettings("User Interface", "CustomKey", "")
            #self.customKey = helpers.MakeComboEntry(self.root, "Custom key to close hovered tab", "User Interface", "CustomKey", 3,0, width=10, labelwidth=30, isString=True)
            helpers.MakeLabel(self.root, "General Settings", 3,0, sticky="w")
            helpers.MakeCheckButton(self.root, "Show FPS", "User Interface", "ShowFPS", 4,0, width=40, default=True)
            helpers.MakeCheckButton(self.root, "Show Copyright & Version", "User Interface", "ShowCopyright", 4,1, width=40, default=True)
            helpers.MakeCheckButton(self.root, "Resize based on Windows scaling", "User Interface", "ScaleWindowBasedOnWindowsSetting", 5,0, width=40, default=True)
            helpers.MakeCheckButton(self.root, "Allow manual resizing", "User Interface", "AllowManualResizing", 5,1, width=40, default=False)
            helpers.MakeLabel(self.root, "NOTICE: You MUST keep either copyright notice on for any videos, public instances, forks etc...", 6,0, sticky="w", columnspan=2)
            helpers.MakeCheckButton(self.root, "Show Copyright in titlebar?", "User Interface", "TitleCopyright", 7,0, width=40, default=False)
            
            helpers.MakeButton(self.root, "Save & Reload", lambda: self.saveAndReload(), 8,0, columnspan=3, sticky="w", width=80)
            helpers.MakeButton(self.root, "Clear open tabs & Reload", lambda: self.clearAndReload(), 9,0, columnspan=3, sticky="w", width=80)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)