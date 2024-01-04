"""
The main file.
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="SDKController", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Send data to the game with the SDK.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before UI" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.controls as controls # use controls.RegisterKeybind() and controls.GetKeybindValue()
import struct
import time
import keyboard
from src.translator import Translate

mmName = r"Local\SCSControls"
floatCount = 4
floatSize = 4
boolCount = 15
boolSize = 1
size = floatCount * floatSize + boolCount * boolSize

def tryExceptDefault(data, dataPath, default):
    """Tries to get data from the data variable, if it fails returns the default value."""
    # Datapath is an array of strings
    try:
        workingData = data
        for i in dataPath:
            workingData = workingData[i]
        return workingData
    except:
        return default

"""
Values that the sdk accepts:

Name,Index,Type,Control Name In File
Steering,0,float,steering
Acceleration,1,float,aforward
Braking,2,float,abackward
Clutch,3,float,clutch
Pause Game,4,bool,
Parking Brake,5,bool,parkingbrake
Wipers,6,bool,wipers
Cruise Control,7,bool,cruiectrl
Cruise Control Increase,8,bool,cruiectrlinc
Cruise Control Decrease,9,bool,cruiectrldec
Cruise Control Reset,10,bool,cruiectrlres
Lights,11,bool,light
High Beams,12,bool,hblight
Left Blinker,13,bool,lblinker
Right Blinker,14,bool,rblinker
Quickpark,15,bool,quickpark
Drive (Gear),16,bool,drive
Reverse (Gear),17,bool,reverse
Cycle Zoom (map?),18,bool,cycl_zoom
"""

import mmap
# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
lastPress = time.time()
def plugin(data):
    """Available controls are 
    ```
    data["sdk"]["steering"], float
    data["sdk"]["acceleration"], float
    data["sdk"]["brake"], float
    data["sdk"]["clutch"], float
    data["sdk"]["Pause"], bool
    data["sdk"]["ParkingBrake"], bool
    data["sdk"]["Wipers"], bool
    data["sdk"]["CruiseControl"], bool
    data["sdk"]["CruiseControlIncrease"], bool
    data["sdk"]["CruiseControlDecrease"], bool
    data["sdk"]["CruiseControlReset"], bool
    data["sdk"]["Lights"], bool
    data["sdk"]["HighBeams"], bool
    data["sdk"]["LeftBlinker"], bool
    data["sdk"]["RightBlinker"], bool
    data["sdk"]["Quickpark"], bool
    data["sdk"]["Drive"], bool
    data["sdk"]["Reverse"], bool
    data["sdk"]["CycleZoom"], bool
    ```
    """
    if settings.GetSettings("sdk", "firstTime") == None:
        from tkinter import messagebox
        messagebox.showinfo("SDK Controller", Translate("IMPORTANT NOTE:\nIf the plugin has been added by an update, and you've not run the first time setup after updating. Please either run it, or copy the file from the\n'plugins/FirstTimeSetup/sdkPlugin'\nfolder to the game plugin folder.\n\nThis can be found by opening steam, right clicking on the game, manage, browse local files, and then opening the bin/win_x64/plugins folder.\n\nIf you've already run the first time setup, you can ignore this message."))
        settings.CreateSettings("sdk", "firstTime", False)
    
    global lastPress
    buf = None

    try:
        buf = mmap.mmap(0, size, "Local\SCSControls")  # 3 floats, 4 bytes each
    except:
        return data
    
    if buf == None:
        return data

    # For steering accel and brake we have to support the old controller system data variable
    try:
        steering = data["sdk"]["acceleration"]
    except:
        steering = tryExceptDefault(data, ["controller","leftStick"], 0.0)
    
    try:
        acceleration = data["sdk"]["acceleration"]
    except:
        acceleration = tryExceptDefault(data, ["controller","righttrigger"], 0.0)
        
    try:
        brake = data["sdk"]["brake"]
    except:
        brake = tryExceptDefault(data, ["controller","lefttrigger"], 0.0)
    
    clutch = tryExceptDefault(data, ["sdk","Clutch"], 0.0)
    
    # Get bools
    pause = tryExceptDefault(data, ["sdk","Pause"], False)
    parkingbrake = tryExceptDefault(data, ["sdk","ParkingBrake"], False)
    wipers = tryExceptDefault(data, ["sdk","Wipers"], False)
    cruiectrl = tryExceptDefault(data, ["sdk","CruiseControl"], False)
    cruiectrlinc = tryExceptDefault(data, ["sdk","CruiseControlIncrease"], False)
    cruiectrldec = tryExceptDefault(data, ["sdk","CruiseControlDecrease"], False)
    cruiectrlres = tryExceptDefault(data, ["sdk","CruiseControlReset"], False)
    light = tryExceptDefault(data, ["sdk","Lights"], False)
    hblight = tryExceptDefault(data, ["sdk","HighBeams"], False)
    lblinker = tryExceptDefault(data, ["sdk","LeftBlinker"], False)
    rblinker = tryExceptDefault(data, ["sdk","RightBlinker"], False)
    quickpark = tryExceptDefault(data, ["sdk","Quickpark"], False)
    drive = tryExceptDefault(data, ["sdk","Drive"], False)
    reverse = tryExceptDefault(data, ["sdk","Reverse"], False)
    cycl_zoom = tryExceptDefault(data, ["sdk","CycleZoom"], False)
    
    
    # Write three floats to memory
    buf[:] = struct.pack('ffff15?', steering, acceleration, brake, clutch,
                         pause, parkingbrake, wipers, cruiectrl, cruiectrlinc, cruiectrldec, 
                         cruiectrlres, light, hblight, lblinker, rblinker, quickpark, drive, 
                         reverse, cycl_zoom)

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass
