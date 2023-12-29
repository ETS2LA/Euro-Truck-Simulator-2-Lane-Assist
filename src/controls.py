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
def RegisterKeybind(name, callback=None, notBoundInfo="", description="", axis=False, defaultButtonIndex=-1, defaultAxisIndex=-1):
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
def plugin(data):
    """Handles calling back the keybinds. Should not be called directly.

    Args:
        data (dict): Data dictionary from main.py

    Returns:
        dict: Data dictionary to main.py
    """
    pygame.event.pump()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for keybind in KEYBINDS:
        if keybind["callback"] != None:
            for joystick in joysticks:
                if joystick.get_guid() == keybind["deviceGUID"]:
                    if keybind["buttonIndex"] == type(""): # We are expecting a key
                        if keyboard.is_pressed(keybind["buttonIndex"]):
                            keybind["callback"]()
                    else: # We are expecting a controller button or axis
                        if keybind["buttonIndex"] != -1:
                            if joystick.get_button(keybind["buttonIndex"]):
                                keybind["callback"]()
                        elif keybind["axisIndex"] != -1:
                            if abs(joystick.get_axis(keybind["axisIndex"])) > 0.4:
                                keybind["callback"]()
            pass
    
    return data

def ChangeKeybind(name):
    """Will run the keybind change window code.

    Args:
        name (str): Keybind to change (name).
    """
    global save
    global currentbinding
    
    print("Changing keybind " + name)
    # Make a new window to get the keybind on
    window = tk.Toplevel()
    window.title("Change keybind")
    window.geometry("300x130")
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
    
    def SaveBind():
        global save
        save = True
        window.destroy()
    
    # Save button
    saveButton = ttk.Button(window, text="Save", command=lambda: SaveBind(), width=30)
    saveButton.pack()
    
    # Get all devices from pygame
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    
    # For all devices, save the default state
    defaultStates = []
    pygame.event.pump()
    for joystick in joysticks:
        defaultStates.append({"name": joystick.get_name(), "buttons": [joystick.get_button(i) for i in range(joystick.get_numbuttons())], "axes": [joystick.get_axis(i) for i in range(joystick.get_numaxes())]})
    
    save = False
    currentbinding = None
    
    def KeyboardEvent(event):
        global currentbinding
        if not keybindToChange["shouldBeAxis"]:
            label.config(text=f"Key: '{event.keysym}'")
            currentbinding = {"deviceGUID": KEYBOARD_GUID, "buttonIndex": event.keysym}
    
    window.bind("<Key>", KeyboardEvent)
    window.protocol("WM_DELETE_WINDOW", lambda: SaveBind())
    
    while not save:
        # Check if any of the states change
        pygame.event.pump()
        for i in range(len(joysticks)):
            joystick = joysticks[i]
            defaultState = defaultStates[i]
            if not keybindToChange["shouldBeAxis"]:
                for j in range(joystick.get_numbuttons()):
                    if defaultState["buttons"][j] != joystick.get_button(j):
                        label.config(text=f"Button: {j}")
                        currentbinding = {"deviceGUID": joystick.get_guid(), "buttonIndex": j}

            if keybindToChange["shouldBeAxis"]:    
                for j in range(joystick.get_numaxes()):
                    if abs(defaultState["axes"][j] - joystick.get_axis(j)) > 0.4:
                        label.config(text=f"Axis: {j}")
                        axisSlider.set(joystick.get_axis(j))
                        currentbinding = {"deviceGUID": joystick.get_guid(), "axisIndex": j}


        mainUI.root.update()
        window.update()
        
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

    mainUI.closeTabName("controls")
    mainUI.switchSelectedPlugin("src.controls")
    
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


def GetKeybindValue(name):
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
        return None
    
    pygame.event.pump()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        if joystick.get_guid() == keybind["deviceGUID"]:
            if keybind["buttonIndex"] != -1:
                return True if joystick.get_button(keybind["buttonIndex"]) == 1 else False
            elif keybind["axisIndex"] != -1:
                return joystick.get_axis(keybind["axisIndex"])
    return None

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
                    if keybind["deviceGUID"] == KEYBOARD_GUID:
                        helpers.MakeLabel(frame, "Device: Keyboard", 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"])
                    for joystick in joysticks:
                        if joystick.get_guid() == keybind["deviceGUID"]:
                            helpers.MakeLabel(frame, "Device: " + joystick.get_name(), 0, 2, sticky="w", padx=10, pady=0, font=["Segoe UI", 10, "bold"], tooltip=f"GUID: {str(joystick.get_guid())}")
                            break
                        
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