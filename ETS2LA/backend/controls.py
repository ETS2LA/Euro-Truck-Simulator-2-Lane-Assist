"""
Input manager for other plugins. This plugin will handle all the inputs and provide a way for other plugins to use them.

```python
# Will register a keybind to the input manager. This is necessary to use the keybind.
RegisterKeybind(name, callback=None, description="") 

# Will get the value of a keybind.
GetKeybindValue(name)
```
"""
import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
from plugins.plugin import PluginInformation
import math
import pygame
import keyboard
from tktooltip import ToolTip
from src.logger import print

PluginInfo = PluginInformation(
    name="controls", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Provides a way to manage inputs unified for all plugins.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

KEYBOARD_GUID = 1
KEYBINDS = []
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
    keybind = settings.GetSettings("Input", name)
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
    settings.CreateSettings("Input", name, {"description": description, "deviceGUID": deviceGUID, "buttonIndex": buttonIndex, "axisIndex": axisIndex, "shouldBeAxis": shouldBeAxis, "notBoundInfo": notBoundInfo})    

pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
def plugin(data):
    """Handles calling back the keybinds. Should not be called directly.

    Args:
        data (dict): Data dictionary from main.py

    Returns:
        dict: Data dictionary to main.py
    """
    pygame.event.pump()
    for keybind in KEYBINDS:
        if keybind["callback"] != None:
            if keybind["deviceGUID"] == KEYBOARD_GUID:
                try:
                    if keyboard.is_pressed(keybind["buttonIndex"]):
                        keybind["callback"]()
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
    
    return data

def ChangeKeybind(name:str, updateUI:bool=True, callback=None):
    """Will run the keybind change window code.

    Args:
        name (str): Keybind to change (name).
        updateUI (bool): Whether the UI should be updated (should be False if the function is called from other files).
        callback (function): Callback to run after the keybind has been changed.
    """
    global save
    global ignore
    global currentbinding
    
    print("Changing keybind " + name)
    # Make a new window to get the keybind on
    window = tk.Toplevel()
    window.title("Change keybind")
    mainUIPos = mainUI.root.winfo_x(), mainUI.root.winfo_y()
    window.geometry(f"300x200+{mainUIPos[0] + 100}+{mainUIPos[1] + 100}")
    window.resizable(False, False)
    window.grab_set()
    window.focus_set()
    keybindToChange = KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))]
    if keybindToChange == None:
        print("Keybind not found")
        return
    
    
    
    # Slider for the axis
    if keybindToChange["shouldBeAxis"]:
        axisSlider = tk.Scale(window, from_=-1, to=1, orient="horizontal", length=200, resolution=0.01)
        axisSlider.pack()
        # Make a label to show the current keybind
        label = ttk.Label(window, text="Listening for input...\n(expecting an axis)")
        label.pack()
    else:
        # Make a label to show the current keybind
        label = ttk.Label(window, text="Listening for input...\n(expecting a button)")
        label.pack()
    
    ttk.Label(window, text="   ").pack()
    
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
            label.config(text=f"Key: '{event.keysym}'")
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
                            label.config(text=f"Listening for input...\n(expecting a button)")
                            continue
                        if j in ignoredButtons:
                            continue
                        
                        label.config(text=f"Button: {j}")
                        currentbinding = {"deviceGUID": joystick.get_guid(), "buttonIndex": j}

            if keybindToChange["shouldBeAxis"]:    
                for j in range(joystick.get_numaxes()):
                    if GetDistanceFromDefault(joystick.get_axis(j), defaultState["axes"][j]) > 0.2:
                        if ignore:
                            print("Ignoring axis " + str(j))    
                            ignoredAxis.append(j)
                            ignore = False
                            label.config(text=f"Listening for input...\n(expecting an axis)")
                            axisSlider.set(0)
                            continue
                        if j in ignoredAxis:
                            print("Ignoring axis " + str(j))
                            continue
                        
                        label.config(text=f"Axis: {j}")
                        axisSlider.set(joystick.get_axis(j))
                        currentbinding = {"deviceGUID": joystick.get_guid(), "axisIndex": j}
                        foundAxis = True

        if not foundAxis and keybindToChange["shouldBeAxis"]:
            axisSlider.set(0)

        mainUI.root.update()
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

    if updateUI:
        mainUI.closeTabName("controls")
        mainUI.switchSelectedPlugin("src.controls")
        
    if callback != None:
        callback()
        
    helpers.ShowPopup("\nKeybind change successful.", "Controls", timeout=3)
        
def UnbindKeybind(name, updateUI=True):
    """Remove the binding of a keybind.

    Args:
        name (str): Keybind to remove (name).
        updateUI (bool, optional): Should the UI be updated (should be False if the function is called from other files). Defaults to True.
    """
    SaveKeybind(name, deviceGUID=-1, buttonIndex=-1, axisIndex=-1)
    KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))] = {"name": name, 
                                                                                                 "callback": next((item for item in KEYBINDS if item["name"] == name), None)["callback"], 
                                                                                                 "description": next((item for item in KEYBINDS if item["name"] == name), None)["description"], 
                                                                                                 "deviceGUID": -1, 
                                                                                                 "buttonIndex": -1, 
                                                                                                 "axisIndex": -1,
                                                                                                 "shouldBeAxis": next((item for item in KEYBINDS if item["name"] == name), None)["shouldBeAxis"],
                                                                                                 "notBoundInfo": next((item for item in KEYBINDS if item["name"] == name), None)["notBoundInfo"]}
    if updateUI:
        mainUI.closeTabName("controls")
        mainUI.switchSelectedPlugin("src.controls")


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

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            # Check if the KEYBINDS list is empty. If so, then don't load the UI
            self.loadUI()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def loadUI(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=700, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.controlsNotebook = ttk.Notebook(self.root, width=700, height=600)
            
            keybindCount = len(KEYBINDS)
            pages = []
            for i in range(math.ceil(keybindCount/6)):
                pages.append(ttk.Frame(self.controlsNotebook))
                self.controlsNotebook.add(pages[i], text="Page " + str(i+1))
                self.controlsNotebook.pack(anchor="center", expand=False)
                
            i = 0
            page = 0
            
            pygame.init()
            pygame.joystick.init()
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            
            for i in range(keybindCount):
                keybind = KEYBINDS[i]
                frame = ttk.LabelFrame(pages[page], text="Keybind  -  " + keybind["name"], width=700)
                
                # Make labels for the keybind information
                if keybind["deviceGUID"] != -1:
                    noDevice = True
                    
                    if keybind["deviceGUID"] == KEYBOARD_GUID:
                        label = helpers.MakeLabel(frame, "Device: Keyboard", 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                        ToolTip(label, msg="GUID: " + str(KEYBOARD_GUID) + "\nThis is the keyboard connected to the computer.")
                        noDevice = False
                        
                    for joystick in joysticks:
                        if joystick.get_guid() == keybind["deviceGUID"]:
                            label = helpers.MakeLabel(frame, "Device: " + joystick.get_name(), 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"], tooltip=f"GUID: {str(joystick.get_guid())}")
                            ToolTip(label, msg=f"GUID: {str(joystick.get_guid())}")
                            noDevice = False
                            break
                        
                    if noDevice:
                        label = helpers.MakeLabel(frame, "Device: Missing", 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"], fg="yellow")
                        ToolTip(label, msg="The device that was used to bind this keybind is not connected to the computer.\nGUID: " + str(keybind["deviceGUID"]))
                        
                if keybind["buttonIndex"] != -1:
                    if type(keybind["buttonIndex"]) == type(""):
                        helpers.MakeLabel(frame, "Key: " + keybind["buttonIndex"], 1, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                    else:
                        helpers.MakeLabel(frame, "Button index: " + str(keybind["buttonIndex"]), 1, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                elif keybind["axisIndex"] != -1:
                    helpers.MakeLabel(frame, "Axis index: " + str(keybind["axisIndex"]), 1, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                
                if keybind["deviceGUID"] == -1:
                    helpers.MakeLabel(frame, "Not bound", 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"], fg="red")
                    if keybind["notBoundInfo"] != "":
                        helpers.MakeLabel(frame, keybind["notBoundInfo"], 1, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                
                button = helpers.MakeButton(frame, "Change" if not keybind["deviceGUID"] == -1 else "Bind", lambda i=i: ChangeKeybind(KEYBINDS[i]["name"]), 0, 0, sticky="e", rowspan=3)
                
                if keybind["description"] != "":
                    ToolTip(button, msg=keybind["description"])
                
                helpers.MakeButton(frame, "Remove", lambda i=i: UnbindKeybind(KEYBINDS[i]["name"]), 0, 1, sticky="e", rowspan=3, state="disabled" if keybind["deviceGUID"] == -1 else "!disabled")
                
                frame.pack(anchor="w", fill="x", expand=False)
                i += 1
                if i % 6 == 0:
                    page += 1
                    i = 0
            
            for i in range(len(pages)):
                self.controlsNotebook.tab(i, text="Page " + str(i+1))
                
            
            
            self.controlsNotebook.pack(anchor="center", expand=False)
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)