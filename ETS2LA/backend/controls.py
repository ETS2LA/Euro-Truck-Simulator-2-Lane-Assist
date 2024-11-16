"""
Input manager for other plugins. This plugin will handle all the inputs and provide a way for other plugins to use them.

```python
# Will register a keybind to the input manager. This is necessary to use the keybind.
RegisterKeybind(name, callback=None, description="") 

# Will get the value of a keybind.
GetKeybindValue(name)
```
"""

# This file is from V1, it will be refactored at some point...
# for now it works so we will roll with it.
# Sorry for the mess.

from ETS2LA.frontend.immediate import send_sonner
from ETS2LA.utils.translator import Translate
import ETS2LA.backend.settings as settings
import ETS2LA.variables as variables
from tktooltip import ToolTip
from tkinter import ttk
import tkinter as tk
import threading
import keyboard
import colorsys
import logging
import pygame
import math
import time
import os

KEYBOARD_GUID = 1
KEYBINDS = []
SETTINGS_FILENAME = "ETS2LA/backend/settings/controls.json"
def RegisterKeybind(name:str, callback=None, notBoundInfo:str="", description:str="", axis:bool=False, defaultButtonIndex:int=-1, defaultAxisIndex:int=-1):
    """Will register a keybind to the input manager. This is necessary to use the keybind.

    Args:
        name (str): Keybind name. This is used to identify the keybind.
        callback (_type_, optional): Callback when the keybind is pressed. Defaults to None.
        notBoundInfo (str, optional): Will be shown to the user when nothing is bound. Useful for notifying of optional keybinds. Defaults to "".
        description (str, optional): Additional description to the keybind. Defaults to "".
        axis (bool, optional): Should the keybind be an axis.
    """
    
    keybind = GetKeybindFromName(name)
    if keybind == None: # This is the first time we've seen the keybind
        SaveKeybind(name, description=description, 
                    deviceGUID=KEYBOARD_GUID if type(defaultButtonIndex) == type("n") else -1, 
                    buttonIndex=defaultButtonIndex, 
                    axisIndex=defaultAxisIndex, 
                    shouldBeAxis=axis,
                    notBoundInfo=notBoundInfo)
        
        KEYBINDS.append({"name": name, 
                         "callback": callback, 
                         "description": description, 
                         "deviceGUID": KEYBOARD_GUID if type(defaultButtonIndex) == type("n") else -1, 
                         "buttonIndex": defaultButtonIndex, 
                         "axisIndex": defaultAxisIndex,
                         "shouldBeAxis": axis,
                         "notBoundInfo": notBoundInfo})
    else: # We already have data for the keybind
        KEYBINDS.append({"name": name, 
                         "callback": callback, 
                         "description": description if description != keybind["description"] else keybind["description"], 
                         "deviceGUID": keybind["deviceGUID"], 
                         "buttonIndex": keybind["buttonIndex"], 
                         "axisIndex": keybind["axisIndex"],
                         "shouldBeAxis": axis,
                         "notBoundInfo": notBoundInfo if notBoundInfo != keybind["notBoundInfo"] else keybind["notBoundInfo"]})

def UpdateKeybindsFromSettings():
    """Will update the keybinds from the settings file."""
    global KEYBINDS
    keybinds = settings.GetJSON(SETTINGS_FILENAME)
    KEYBINDS = []
    for keybind in keybinds:
        KEYBINDS.append({"name": keybind, 
                         "callback": None, 
                         "description": keybinds[keybind]["description"], 
                         "deviceGUID": keybinds[keybind]["deviceGUID"], 
                         "buttonIndex": keybinds[keybind]["buttonIndex"], 
                         "axisIndex": keybinds[keybind]["axisIndex"],
                         "shouldBeAxis": keybinds[keybind]["shouldBeAxis"],
                         "notBoundInfo": keybinds[keybind]["notBoundInfo"]})

def ReadKeybindsVariable():
    """Returns the KEYBINDS variable."""
    global KEYBINDS
    return KEYBINDS

def WriteKeybindsVariable(value=[]):
    """Overwrites the KEYBINDS variable."""
    global KEYBINDS
    KEYBINDS = value
    
def GetKeybindFromName(name):
    """Get a keybind from the settings file.

    Args:
        name (str): Keybind name.

    Returns:
        dict: Keybind data.
    """
    keybind = settings.Get(SETTINGS_FILENAME, name)
    return keybind

def SaveKeybind(name, description="", deviceGUID=-1, buttonIndex=-1, axisIndex=-1, shouldBeAxis=False, notBoundInfo=""):
    """Save a keybind to the settings file.

    Args:
        name (str): Keybind name to save.
        description (str, optional): Description to save. Defaults to "".
        deviceGUID (str, optional): Device GUID. Defaults to -1.
        buttonIndex (int, optional): Button index. If -1 buttons will not be considered. Defaults to -1.
        axisIndex (int, optional): Axis index. If -1 axis will not be considered. Defaults to -1.
        notBoundInfo (str, optional): Info to show when the keybind is not bound. Defaults to "".
    """
    settings.Set(SETTINGS_FILENAME, name, {"description": description, "deviceGUID": deviceGUID, "buttonIndex": buttonIndex, "axisIndex": axisIndex, "shouldBeAxis": shouldBeAxis, "notBoundInfo": notBoundInfo})    

wasPressing = []
def plugin():
    """Handles calling back the keybinds. Should not be called directly.

    Args:
        data (dict): Data dictionary from main.py

    Returns:
        dict: Data dictionary to main.py
    """
    global wasPressing
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    while True:
        time.sleep(0.01)
        try:
            pygame.event.pump()
            for keybind in KEYBINDS:
                if keybind["callback"] != None:
                    if keybind["deviceGUID"] == KEYBOARD_GUID:
                        try:
                            if keyboard.is_pressed(keybind["buttonIndex"]) and keybind["name"] not in wasPressing:
                                try:
                                    keybind["callback"]()
                                except:
                                    import traceback
                                    traceback.print_exc()
                                wasPressing.append(keybind["name"])
                            elif not keyboard.is_pressed(keybind["buttonIndex"]) and keybind["name"] in wasPressing:
                                wasPressing.remove(keybind["name"])
                        except:
                            pass
                    else:
                        for joystick in joysticks:
                            try:
                                if joystick.get_guid() == keybind["deviceGUID"]:
                                    if keybind["buttonIndex"] != -1:
                                        if joystick.get_button(keybind["buttonIndex"]):
                                            keybind["callback"]()
                                    elif keybind["axisIndex"] != -1:
                                        if abs(joystick.get_axis(keybind["axisIndex"])) > 0.4:
                                            keybind["callback"]()
                            except:
                                pass
                    pass
        except:
            logging.exception("Error in keybinds")
            pass

def ChangeKeybind(name:str, callback=None):
    """Will run the keybind change window code.

    Args:
        name (str): Keybind to change (name).
        updateUI (bool): Whether the UI should be updated (should be False if the function is called from other files).
        callback (function): Callback to run after the keybind has been changed.
    """
    global save
    global ignore
    global currentbinding

    keybindToChange = KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))]
    if keybindToChange == None:
        print("Keybind not found")
        try:
            window.destroy()
        except:
            pass
        return

    try:
        theme = settings.Get("global", "theme", "dark")
        with open(f"{variables.PATH}frontend\\src\\pages\\globals.css", "r") as file:
            content = file.read().split("\n")
            for i, line in enumerate(content):
                if i > 0:
                    if content[i - 1].replace(" ", "").startswith(":root{" if theme == "light" else ".dark{") and line.replace(" ", "").startswith("--background"):
                        line = str(line.split(":")[1]).replace(";", "")
                        for i, char in enumerate(line):
                            if char == " ":
                                line = line[i+1:]
                            else:
                                break
                        line = line.split(" ")
                        line = [round(float(line[0])), round(float(line[1][:-1])), round(float(line[2][:-1]))]
                        rgb_color = colorsys.hls_to_rgb(int(line[0])/360,int(line[2])/100,int(line[1])/100)
                        hex_color = '#%02x%02x%02x'%(round(rgb_color[0]*255),round(rgb_color[1]*255),round(rgb_color[2]*255))
                        BackgroundColor = hex_color
    except:
        try:
            BackgroundColor = "#ffffff" if settings.Get("global", "theme", "dark") == "light" else "#09090b"
        except:
            BackgroundColor = "#09090b"

    TextColor = '#%02x%02x%02x' % (255 - int(BackgroundColor[1:3], 16), 255 - int(BackgroundColor[3:5], 16), 255 - int(BackgroundColor[5:7], 16))
    ActiveBackgroundColor = "#%02x%02x%02x" % (int(BackgroundColor[1:3], 16) + 20, int(BackgroundColor[3:5], 16) + 20, int(BackgroundColor[5:7], 16) + 20)

    print("Changing keybind " + name)
    UpdateKeybindsFromSettings() # Make sure we have the latest keybinds
    # Make a new window to get the keybind on

    if os.name == "nt":
        import win32gui
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        if hwnd != 0:
            rect = win32gui.GetClientRect(hwnd)
            tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
            br = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
            window = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
            window_x = window[0] + window[2] / 2 - 150
            window_y = window[1] + window[3] / 2 - (94 if keybindToChange["shouldBeAxis"] else 75)
        else:
            window_x = None
            window_y = None
    else:
        window_x = None
        window_y = None

    window = tk.Tk()
    # TODO: This will freeze the UI on the second time the window is opened. Fix this.
    #import sv_ttk
    #sv_ttk.set_theme(theme, window)
    window.title("Change keybind")
    window.geometry("300x188" if keybindToChange["shouldBeAxis"] else "300x150")
    if window_x != None and window_y != None:
        window.geometry(f"+{int(window_x)}+{int(window_y)}")
    window.resizable(False, False)
    window.configure(bg=BackgroundColor)
    window.update()
    window.grab_set()
    window.focus_set()

    # Focus to the new window
    window.focus_force()

    if os.name == "nt":
        from ctypes import windll, byref, sizeof, c_int
        windll.dwmapi.DwmSetWindowAttribute(windll.user32.GetParent(window.winfo_id()), 35, byref(c_int(int(int(BackgroundColor[5:7] + BackgroundColor[3:5] + BackgroundColor[1:3], 16)))), sizeof(c_int))
        # TODO - Add favicon back
        #window.iconbitmap(default=f"{variables.PATH}frontend/src/assets/favicon.ico")

    # Try to grab focus
    try:
        window.attributes("-topmost", True)
    except:
        pass

    if keybindToChange["shouldBeAxis"]:
        # Make a label to show the current keybind
        label = ttk.Label(window, text="Listening for input...\n(expecting an axis)", foreground=TextColor, background=BackgroundColor)
        label.pack()
        # Slider for the axis
        axisSlider = tk.Scale(window, from_=-1, to=1, orient="horizontal", length=200, resolution=0.01, foreground=TextColor, background=BackgroundColor, activebackground=ActiveBackgroundColor, highlightthickness=0)
        axisSlider.pack()
    else:
        # Make a label to show the current keybind
        label = ttk.Label(window, text="Listening for input...\n(expecting a button)", foreground=TextColor, background=BackgroundColor)
        label.pack()

    ttk.Label(window, text="", foreground=TextColor, background=BackgroundColor).pack()

    def IgnoreBind():
        global ignore
        ignore = True
        print("Ignoring next input")

    def SaveBind():
        global save
        save = True
        window.destroy()

    # Ignore button
    ignoreButton = ttk.Button(window, text="Ignore", command=lambda: IgnoreBind(), width=30)
    ignoreButton.pack()

    # Save button
    saveButton = ttk.Button(window, text="Save", command=lambda: SaveBind(), width=30)
    saveButton.pack(pady=10)

    # Get all devices from pygame
    pygame.init()
    pygame.joystick.init()
    pygame.event.pump()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    import time
    time.sleep(0.2)
    pygame.event.pump()

    # For all devices, save the default state
    defaultStates = []
    for joystick in joysticks:
        defaultStates.append({"name": joystick.get_name(), "buttons": [joystick.get_button(i) for i in range(joystick.get_numbuttons())], "axes": [joystick.get_axis(i) for i in range(joystick.get_numaxes())]})

    save = False
    ignore = False
    currentbinding = None

    def KeyboardEvent(event):
        global currentbinding
        if not keybindToChange["shouldBeAxis"]:
            if len(event.keysym) > 2:
                return # Ignore special keys
            label.config(text=f"Detected a keypress\nKey: '{event.keysym}'", justify="center")
            currentbinding = {"deviceGUID": KEYBOARD_GUID, "buttonIndex": event.keysym}

    window.bind("<Key>", KeyboardEvent)
    window.protocol("WM_DELETE_WINDOW", lambda: SaveBind())

    def GetDistanceFromDefault(currentVal, defaultVal):
        return abs(currentVal - defaultVal)

    ignoredAxis = []
    ignoredButtons = []

    foundAxis = False
    while not save:
        # Check if any of the states change
        pygame.event.pump()
        for i in range(len(joysticks)):
            joystick = joysticks[i]
            defaultState = defaultStates[i]
            if not keybindToChange["shouldBeAxis"]:
                for j in range(joystick.get_numbuttons()):
                    if defaultState["buttons"][j] != joystick.get_button(j):
                        if ignore:
                            ignoredButtons.append(j)
                            ignore = False
                            label.config(text=f"Listening for input...\n(expecting a button)", justify="center")
                            continue
                        if j in ignoredButtons:
                            continue

                        label.config(text=f"Detected a button press\nButton: {j}", justify="center")
                        currentbinding = {"deviceGUID": joystick.get_guid(), "buttonIndex": j}

            if keybindToChange["shouldBeAxis"]:    
                for j in range(joystick.get_numaxes()):
                    if GetDistanceFromDefault(joystick.get_axis(j), defaultState["axes"][j]) > 0.2:
                        if ignore:
                            print("Ignoring axis " + str(j))    
                            ignoredAxis.append(j)
                            ignore = False
                            label.config(text=f"Listening for input...\n(expecting an axis)", justify="center")
                            axisSlider.set(0)
                            continue
                        if j in ignoredAxis:
                            print("Ignoring axis " + str(j))
                            continue

                        label.config(text=f"Detected an axis movement\nAxis: {j}", justify="center")
                        axisSlider.set(joystick.get_axis(j))
                        currentbinding = {"deviceGUID": joystick.get_guid(), "axisIndex": j}
                        foundAxis = True

        if not foundAxis and keybindToChange["shouldBeAxis"]:
            axisSlider.set(0)

        window.update()
        foundAxis = False

    if currentbinding != None:
        SaveKeybind(name, deviceGUID=currentbinding["deviceGUID"], buttonIndex=currentbinding["buttonIndex"] if "buttonIndex" in currentbinding else -1, axisIndex=currentbinding["axisIndex"] if "axisIndex" in currentbinding else -1)
        KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))] = {"name": name, 
                                                                                                     "callback": next((item for item in KEYBINDS if item["name"] == name), None)["callback"], 
                                                                                                     "description": next((item for item in KEYBINDS if item["name"] == name), None)["description"], 
                                                                                                     "deviceGUID": currentbinding["deviceGUID"], 
                                                                                                     "buttonIndex": currentbinding["buttonIndex"] if "buttonIndex" in currentbinding else -1, 
                                                                                                     "axisIndex": currentbinding["axisIndex"] if "axisIndex" in currentbinding else -1,
                                                                                                     "shouldBeAxis": next((item for item in KEYBINDS if item["name"] == name), None)["shouldBeAxis"],
                                                                                                     "notBoundInfo": next((item for item in KEYBINDS if item["name"] == name), None)["notBoundInfo"]}

        print(f"Saved keybind {name}")

    if callback != None:
        callback()
        
def UnbindKeybind(name):
    """Remove the binding of a keybind.

    Args:
        name (str): Keybind to remove (name).
        updateUI (bool, optional): Should the UI be updated (should be False if the function is called from other files). Defaults to True.
    """
    UpdateKeybindsFromSettings() # Make sure we have the latest keybinds
    SaveKeybind(name, deviceGUID=-1, buttonIndex=-1, axisIndex=-1)
    KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))] = {"name": name, 
                                                                                                 "callback": next((item for item in KEYBINDS if item["name"] == name), None)["callback"], 
                                                                                                 "description": next((item for item in KEYBINDS if item["name"] == name), None)["description"], 
                                                                                                 "deviceGUID": -1, 
                                                                                                 "buttonIndex": -1, 
                                                                                                 "axisIndex": -1,
                                                                                                 "shouldBeAxis": next((item for item in KEYBINDS if item["name"] == name), None)["shouldBeAxis"],
                                                                                                 "notBoundInfo": next((item for item in KEYBINDS if item["name"] == name), None)["notBoundInfo"]}


def GetKeybindValue(name:str):
    """Will get the value of a keybind.

    Args:
        name (str): The name of the keybind to fetch.

    Returns:
        float | bool | str: Depending on whether the keybind is a button, axis or key, the value will be either a float, bool or str.
    """
    keybind = None
    for bind in KEYBINDS:
        if bind["name"] == name:
            keybind = bind
            break
        
    if keybind == None:
        return False
    
    if keybind["deviceGUID"] == KEYBOARD_GUID:
        try:
            return True if keyboard.is_pressed(keybind["buttonIndex"]) else False
        except:
            return False
    
    if keybind["buttonIndex"] == -1 and keybind["axisIndex"] == -1:
        return False
    
    pygame.event.pump()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    try:
        for joystick in joysticks:
            if joystick.get_guid() == keybind["deviceGUID"]:
                if keybind["buttonIndex"] != -1:
                    return True if joystick.get_button(keybind["buttonIndex"]) == 1 else False
                elif keybind["axisIndex"] != -1:
                    return joystick.get_axis(keybind["axisIndex"])
    except:
        return False
    
    return False

def run():
    threading.Thread(target=plugin, daemon=True, ).start()
    logging.info(Translate("controls.listener_started"))