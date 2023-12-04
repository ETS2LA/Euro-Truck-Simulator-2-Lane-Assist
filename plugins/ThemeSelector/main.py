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


# Will switch the application theme
# theme = "SunValley", "Forest", "Azure"
reloads = 0
def ChangeTheme(theme, root, changedColor=False):
    global reloads
    
    if theme != "SunValley" and theme != "Azure":
        ChangeThemeCustom(fr"themes\{theme}\theme.tcl", root, "forest", name=theme, titlebar="0x313131") # Support custom themes from mainUI
        return
    
    else:
        from tkinter import messagebox
        messagebox.showinfo("Theme", "The old default themes have been deprecated, please use / create a new theme for yourself to use.\nFor now we have selected the default ForestRed theme.")
        settings.CreateSettings("User Interface", "ColorTheme", "ForestRed")
        ChangeThemeCustom(fr"themes\ForestRed\theme.tcl", root, "forest", name="ForestRed", titlebar="0x313131") # Support custom themes from mainUI
    
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
    # For dark themes it should be #2d2d2d and for light themes #f0f0f0
    # These have to then be converted to windows compatible int values
    if override == False:
        darkTitlebarColors = {
            "SunValley": 0x1c1c1c,
            "Forest": 0x313131,
            "Azure": 0x333333
        }
        lightTitlebarColors = {
            "SunValley": 0xfafafa,
            "Forest": 0xffffff,
            "Azure": 0xffffff
        }
        
        # Change the titlebar color
        from ctypes import windll, c_int, byref, sizeof
        HWND = windll.user32.GetParent(mainUI.root.winfo_id())
        try:
            returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(lightTitlebarColors[theme]) if themeType == "light" else c_int(darkTitlebarColors[theme])), sizeof(c_int))
        except:
            returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(0x313131)), sizeof(c_int))
            
        print(f"Titlebar color change return code: {returnCode}")
    else:
        # Convert from str to int
        override = int(override, 16)
        
        from ctypes import windll, c_int, byref, sizeof
        HWND = windll.user32.GetParent(mainUI.root.winfo_id())
        returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(override)), sizeof(c_int))
        print(f"Titlebar color change return code: {returnCode}")
    

def SwitchThemeType():
    global themeType
    print(themeType)
    themeType = "dark" if themeType == "light" else "light"
    ChangeTheme(settings.GetSettings("User Interface", "ColorTheme"), mainUI.root, changedColor=True)
    settings.CreateSettings("User Interface", "Theme", themeType)
    print("Switched theme type to " + themeType)
