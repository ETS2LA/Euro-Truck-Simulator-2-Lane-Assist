"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="TruckersMPLock", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will prevent you from using the app with TruckersMP.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI=True # This plugin does not have a UI
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.controls as controls
import os
import win32gui
from tkinter import messagebox

def CheckForTruckersMP():
    def get_window_titles():
        ret = []
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                txt = win32gui.GetWindowText(hwnd)
                if txt:
                    ret.append((hwnd,txt))

        win32gui.EnumWindows(winEnumHandler, None)
        return ret

    all_titles = get_window_titles()
    window_starts = lambda title: [(hwnd,full_title) for (hwnd,full_title) in all_titles if full_title.startswith(title)]

    all_matching_windows = window_starts('Euro Truck Simulator 2 Multiplayer')
    if len(all_matching_windows) > 0:
        return True
    else:
        return False

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    
    if CheckForTruckersMP():
        if helpers.AskOkCancel("TruckersMP detected", "TruckersMP has been detected. Using ETS2LA in TMP is allowed, but you need to keep in mind you might get banned for reckless driving. Keep your eyes on the road, and hands on the steering wheel ready to take over.\nClicking cancel will close the app.\nClicking ok will disable this plugin."):
            settings.RemoveFromList("Plugins", "Enabled", "TruckersMPLock")
            variables.UpdatePlugins()
        else:
            mainUI.quit()

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass