"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ThemeSelector", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will let you switch between themes.\nTHEMES CREATED BY rdbende!",
    version="0.1",
    author="rdbende,Tumppi066",
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


reloads = 0
def ChangeTheme(theme, root, changedColor=False):
    global reloads
    ChangeThemeCustom(fr"themes\{theme}\theme.tcl", root, "forest", name=theme, titlebar="0x313131")
    
def ChangeThemeCustom(themePath, root, base, name="Custom", titlebar="0x313131"):
    global reloads
    
    source = themePath
    
    try:
        root.tk.call("source", source)
    except:
        import traceback
        traceback.print_exc()
        pass
    
    try:
        if base.lower() == "forest":
            ttk.Style().theme_use(f"{name}")
        else:
            root.tk.call(f"{name}")
    except:
        import traceback
        traceback.print_exc()
        pass
    
    settings.CreateSettings("User Interface", "ColorTheme", name)
    ColorTitleBar(root, override=titlebar)
    
    if reloads != 0:
        variables.RELOAD = True
    reloads += 1
            

def ColorTitleBar(root, override=False):
    
    theme = settings.GetSettings("User Interface", "ColorTheme")
    
    # Needs to be int values so windows can understand them
    # It should be #2d2d2d
    # These have to then be converted to windows compatible int values
    if override == False:
        # Change the titlebar color
        from ctypes import windll, c_int, byref, sizeof
        HWND = windll.user32.GetParent(mainUI.root.winfo_id())

        returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(0x313131)), sizeof(c_int))
        if settings.GetSettings("Dev", "print_ui_events", False) == True:
            print(f"Titlebar color change return code: {returnCode}")
    else:
        # Convert from str to int
        override = int(override, 16)
        
        from ctypes import windll, c_int, byref, sizeof
        HWND = windll.user32.GetParent(mainUI.root.winfo_id())
        returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(override)), sizeof(c_int))

def SwitchThemeType():
    ChangeTheme(settings.GetSettings("User Interface", "ColorTheme"), mainUI.root, changedColor=True)
    settings.CreateSettings("User Interface", "Theme", "dark")
    print("Switched theme type to dark")
