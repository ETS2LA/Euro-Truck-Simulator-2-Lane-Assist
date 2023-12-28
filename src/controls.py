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
def RegisterKeybind(name, callback=None, description=""):
    try:
        deviceGUID = settings.GetSettings("Input", name)["deviceGUID"] if settings.GetSettings("Input", name) != None else -1
        buttonIndex = settings.GetSettings("Input", name)["buttonIndex"] if settings.GetSettings("Input", name) != None else -1
        axisIndex = settings.GetSettings("Input", name)["axisIndex"] if settings.GetSettings("Input", name) != None else -1
        KEYBINDS.append({"name": name, "callback": callback, "description": description, "deviceGUID": deviceGUID, "buttonIndex": buttonIndex, "axisIndex": axisIndex})
        SaveKeybind(KEYBINDS[-1]["name"], description=KEYBINDS[-1]["description"], deviceGUID=KEYBINDS[-1]["deviceGUID"], buttonIndex=KEYBINDS[-1]["buttonIndex"], axisIndex=KEYBINDS[-1]["axisIndex"])
    except:
        import traceback
        traceback.print_exc()

def SaveKeybind(name, description="", deviceGUID=-1, buttonIndex=-1, axisIndex=-1):
    settings.UpdateSettings("Input", name, {"description": description, "deviceGUID": deviceGUID, "buttonIndex": buttonIndex, "axisIndex": axisIndex})    

pygame.init()
pygame.joystick.init()
def plugin(data):
    pygame.event.pump()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for keybind in KEYBINDS:
        if keybind["callback"] != None:
            # TODO: Implement checking
            for joystick in joysticks:
                if joystick.get_guid() == keybind["deviceGUID"]:
                    if keybind["buttonIndex"] != -1:
                        if joystick.get_button(keybind["buttonIndex"]):
                            print(joystick.get_button(keybind["buttonIndex"]))
                            keybind["callback"]()
                    elif keybind["axisIndex"] != -1:
                        if abs(joystick.get_axis(keybind["axisIndex"])) > 0.4:
                            keybind["callback"]()
            pass
    
    return data

def ChangeKeybind(name):
    global save
    print("Changing keybind " + name)
    # Make a new window to get the keybind on
    window = tk.Toplevel()
    window.title("Change keybind")
    window.geometry("300x110")
    window.resizable(False, False)
    window.grab_set()
    window.focus_set()
    
    # Make a label to show the current keybind
    label = ttk.Label(window, text="Press a key to change the keybind")
    label.pack()
    
    ttk.Label(window, text="   ").pack()
    
    # Slider for the axis
    axisSlider = tk.Scale(window, from_=-1, to=1, orient="horizontal", length=200, resolution=0.01)
    axisSlider.pack()
    
    def SaveBind():
        global save
        save = True
        window.destroy()
        pass
    
    # Save button
    saveButton = ttk.Button(window, text="Save", command=lambda: SaveBind(), width=10)
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
    while not save:
        # Check if any of the states change
        pygame.event.pump()
        for i in range(len(joysticks)):
            joystick = joysticks[i]
            defaultState = defaultStates[i]
            for j in range(joystick.get_numbuttons()):
                if defaultState["buttons"][j] != joystick.get_button(j):
                    print("Button " + str(j) + " pressed" + f" ({defaultState['buttons'][j]} - {joystick.get_button(j)})")
                    # A button was pressed
                    # SaveKeybind(name, deviceGUID=joystick.get_guid(), buttonIndex=j)
                    label.config(text=f"Button: {j}")
                    currentbinding = {"deviceGUID": joystick.get_guid(), "buttonIndex": j}
                    # window.destroy()
            for j in range(joystick.get_numaxes()):
                if abs(defaultState["axes"][j] - joystick.get_axis(j)) > 0.4:
                    print("Axis " + str(j) + " pressed" + f" ({defaultState['axes'][j]} - {joystick.get_axis(j)})")
                    # An axis was pressed
                    # SaveKeybind(name, deviceGUID=joystick.get_guid(), axisIndex=j)
                    label.config(text=f"Axis: {j}")
                    axisSlider.set(joystick.get_axis(j))
                    currentbinding = {"deviceGUID": joystick.get_guid(), "axisIndex": j}
                    # window.destroy()

        mainUI.root.update()
        window.update()
        
    if currentbinding != None:
        SaveKeybind(name, deviceGUID=currentbinding["deviceGUID"], buttonIndex=currentbinding["buttonIndex"] if "buttonIndex" in currentbinding else -1, axisIndex=currentbinding["axisIndex"] if "axisIndex" in currentbinding else -1)
        KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))] = {"name": name, "callback": next((item for item in KEYBINDS if item["name"] == name), None)["callback"], "description": next((item for item in KEYBINDS if item["name"] == name), None)["description"], "deviceGUID": currentbinding["deviceGUID"], "buttonIndex": currentbinding["buttonIndex"] if "buttonIndex" in currentbinding else -1, "axisIndex": currentbinding["axisIndex"] if "axisIndex" in currentbinding else -1}

    mainUI.switchSelectedPlugin("src.controls")
    
def UnbindKeybind(name):
    SaveKeybind(name, deviceGUID=-1, buttonIndex=-1, axisIndex=-1)
    KEYBINDS[KEYBINDS.index(next((item for item in KEYBINDS if item["name"] == name), None))] = {"name": name, "callback": next((item for item in KEYBINDS if item["name"] == name), None)["callback"], "description": next((item for item in KEYBINDS if item["name"] == name), None)["description"], "deviceGUID": -1, "buttonIndex": -1, "axisIndex": -1}
    mainUI.switchSelectedPlugin("src.controls")

def GetKeybindValue(name):
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
                return joystick.get_button(keybind["buttonIndex"])
            elif keybind["axisIndex"] != -1:
                return joystick.get_axis(keybind["axisIndex"])
    return None

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
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
                frame = ttk.LabelFrame(pages[page], text=keybind["name"])
                
                # Make labels for the keybind information
                if keybind["deviceGUID"] != -1:
                    for joystick in joysticks:
                        if joystick.get_guid() == keybind["deviceGUID"]:
                            ttk.Label(frame, text="Device Name: " + str(joystick.get_name() + "   ")).grid(row=i, column=0, sticky="w")
                            break
                if keybind["buttonIndex"] != -1:
                    ttk.Label(frame, text="Button index: " + str(keybind["buttonIndex"])).grid(row=i, column=1, sticky="w")
                elif keybind["axisIndex"] != -1:
                    ttk.Label(frame, text="Axis index: " + str(keybind["axisIndex"])).grid(row=i, column=1, sticky="w")
                
                helpers.MakeButton(frame, "Change", lambda i=i: ChangeKeybind(KEYBINDS[i]["name"]), i, 10, sticky="e")
                helpers.MakeButton(frame, "Remove", lambda i=i: UnbindKeybind(KEYBINDS[i]["name"]), i, 11, sticky="e")
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