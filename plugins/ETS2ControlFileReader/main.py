"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ETS2ControlFileReader", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
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
import getpass

USERNAME = getpass.getuser()
profileName = settings.GetSettings("ControlReader", "profile", value="")
filepath = "C:/Users/"+USERNAME+"/Documents/Euro Truck Simulator 2/steam_profiles/"

def GetControlSettings():
    try:
        with open(filepath+profileName+"/controls.sii", "r") as f:
            data = f.read()
            outputData = []
            for line in data.splitlines():
                if line.startswith(" config_lines["):
                    # Remove the leading and trailing spaces and the "config_lines[" and "]" from the line
                    line = line.strip()[18:-1]
                    if line[0] == ' ' and line[1] == '"':
                        line = line[2:-1]
                    if line[0] == '"':
                        line = line[1:-1]
                    outputData.append(line)
                    
            return outputData
    except:
        return False

def ParseDeviceData():
    if controlData:
        deviceData = []
        for line in controlData:
            if line.startswith("device"):
                deviceData.append(line)
        return deviceData
    else:
        return False

def ParseMixData():
    if controlData:
        mixData = []
        for line in controlData:
            if line.startswith("mix"):
                data = line.replace("mix ", "")
                key = data.split(" ")[0]
                value = data.replace(key+" ", "")
                value = value.split(" | ")
                for i in range(len(value)):
                    value[i] = value[i].replace("'", "")
                    value[i] = value[i].replace('`', "")
                    
                mixData.append([key, value])
        return mixData
    else:
        return False
    

def UpdateData(profile=""):
    if profile:
        global profileName
        profileName = profile
        settings.CreateSettings("ControlReader", "profile", profileName)
    global controlData, deviceData, mixData
    controlData = GetControlSettings()
    deviceData = ParseDeviceData()
    mixData = ParseMixData()   
    print("Controls data updated") 

    
def GetAvailableProfiles():
    try:
        profiles = os.listdir(filepath)
        return profiles
    except:
        return False

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def UpdateProfileData(self):
            profile = self.profileList.get("active")
            UpdateData(profile)
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.profiles = GetAvailableProfiles()
            # Make a listbox with the profiles
            self.profileList = tk.Listbox(self.root, width=25, height=10)
            self.profileList.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            for profile in self.profiles:
                self.profileList.insert("end", profile)
            # self.profileList.bind("<Double-Button-1>", self.profileListDoubleClick)
            
            helpers.MakeButton(self.root, "Select profile", lambda: self.UpdateProfileData(), 1, 0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)