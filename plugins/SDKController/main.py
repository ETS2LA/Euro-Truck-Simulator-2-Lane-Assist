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
from src.translator import Translate
import src.controls as controls

controls.RegisterKeybind("Test SDK button", notBoundInfo="This is intended for developers.", description="Will test the button selected in the SDK Controller UI.")

mmName = r"Local\SCSControls"
floatCount = 4
floatSize = 4
boolCount = 38
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
Name, Index, Type, Control Name In File

Steering, 0, float, steering
Acceleration, 1, float, aforward
Braking, 2, float, abackward
Clutch, 3, float, clutch
Pause Game, 4, bool,
Parking Brake, 5, bool, parkingbrake
Wipers, 6, bool, wipers
Cruise Control, 7, bool, cruiectrl
Cruise Control Increase, 8, bool, cruiectrlinc
Cruise Control Decrease, 9, bool, cruiectrldec
Cruise Control Reset, 10, bool, cruiectrlres
Lights, 11, bool, light
High Beams, 12, bool, hblight
Left Blinker, 13, bool, lblinker
Right Blinker, 14, bool, rblinker
Quickpark, 15, bool, quickpark
Drive(Gear), 16, bool, drive
Reverse(Gear), 17, bool, reverse
Cycle Zoom(map ? ), 18, bool, cycl_zoom
Reset Trip, 19, bool, tripreset
Rear Wipers, 20, bool, wipersback
Wiper LVL 0, 21, bool, wipers0
Wiper LVL 1, 22, bool, wipers1
Wiper LVL 2, 23, bool, wipers2
Wiper LVL 3, 24, bool, wipers3
Wiper LVL 4, 25, bool, wipers4
Horn, 26, bool, horn
Airhorn, 27, bool, airhorn
Light Horn, 28, bool, lighthorn
Camera 1, 29, bool, cam1
Camera 2, 30, bool, cam2
Camera 3, 31, bool, cam3
Camera 4, 32, bool, cam4
Camera 5, 33, bool, cam5
Camera 6, 34, bool, cam6
Camera 7, 35, bool, cam7
Camera 8, 36, bool, cam8
Zoom Map In, 37, bool, mapzoom_in
Zoom Map Out, 38, bool, mapzoom_out
ACC Mode, 39, bool, accmode
Show Mirrors, 40, bool, showmirrors
Hazard Lights, 41, bool, flasher4way
"""

# This is used for the UI to test each button.
buttonNames = [
    "Pause",
    "ParkingBrake",
    "Wipers",
    "CruiseControl",
    "CruiseControlIncrease",
    "CruiseControlDecrease",
    "CruiseControlReset",
    "Lights",
    "HighBeams",
    "LeftBlinker",
    "RightBlinker",
    "Quickpark",
    "Drive",
    "Reverse",
    "CycleZoom",
    "TripReset",
    "WipersBack",
    "Wipers0",
    "Wipers1",
    "Wipers2",
    "Wipers3",
    "Wipers4",
    "Horn",
    "Airhorn",
    "LightHorn",
    "Cam1",
    "Cam2",
    "Cam3",
    "Cam4",
    "Cam5",
    "Cam6",
    "Cam7",
    "Cam8",
    "MapZoomIn",
    "MapZoomOut",
    "ACCMode",
    "ShowMirrors",
    "Hazards"
]

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
    data["sdk"]["TripReset"], bool
    data["sdk"]["WipersBack"], bool
    data["sdk"]["Wipers0"], bool
    data["sdk"]["Wipers1"], bool
    data["sdk"]["Wipers2"], bool
    data["sdk"]["Wipers3"], bool
    data["sdk"]["Wipers4"], bool
    data["sdk"]["Horn"], bool
    data["sdk"]["Airhorn"], bool
    data["sdk"]["LightHorn"], bool
    data["sdk"]["Cam1"], bool
    data["sdk"]["Cam2"], bool
    data["sdk"]["Cam3"], bool
    data["sdk"]["Cam4"], bool
    data["sdk"]["Cam5"], bool
    data["sdk"]["Cam6"], bool
    data["sdk"]["Cam7"], bool
    data["sdk"]["Cam8"], bool
    data["sdk"]["MapZoomIn"], bool
    data["sdk"]["MapZoomOut"], bool
    data["sdk"]["ACCMode"], bool
    data["sdk"]["ShowMirrors"], bool
    data["sdk"]["Hazards"], bool
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
        steering = data["sdk"]["steering"]
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
    tripreset = tryExceptDefault(data, ["sdk","TripReset"], False)
    wipersback = tryExceptDefault(data, ["sdk","WipersBack"], False)
    wipers0 = tryExceptDefault(data, ["sdk","Wipers0"], False)
    wipers1 = tryExceptDefault(data, ["sdk","Wipers1"], False)
    wipers2 = tryExceptDefault(data, ["sdk","Wipers2"], False)
    wipers3 = tryExceptDefault(data, ["sdk","Wipers3"], False)
    wipers4 = tryExceptDefault(data, ["sdk","Wipers4"], False)
    horn = tryExceptDefault(data, ["sdk","Horn"], False)
    airhorn = tryExceptDefault(data, ["sdk","Airhorn"], False)
    lighthorn = tryExceptDefault(data, ["sdk","LightHorn"], False)
    cam1 = tryExceptDefault(data, ["sdk","Cam1"], False)
    cam2 = tryExceptDefault(data, ["sdk","Cam2"], False)
    cam3 = tryExceptDefault(data, ["sdk","Cam3"], False)
    cam4 = tryExceptDefault(data, ["sdk","Cam4"], False)
    cam5 = tryExceptDefault(data, ["sdk","Cam5"], False)
    cam6 = tryExceptDefault(data, ["sdk","Cam6"], False)
    cam7 = tryExceptDefault(data, ["sdk","Cam7"], False)
    cam8 = tryExceptDefault(data, ["sdk","Cam8"], False)
    mapzoom_in = tryExceptDefault(data, ["sdk","MapZoomIn"], False)
    mapzoom_out = tryExceptDefault(data, ["sdk","MapZoomOut"], False)
    accmode = tryExceptDefault(data, ["sdk","ACCMode"], False)
    showmirrors = tryExceptDefault(data, ["sdk","ShowMirrors"], False)
    hazards = tryExceptDefault(data, ["sdk","Hazards"], False)
    
    # Write three floats to memory
    buf[:] = struct.pack('ffff38?', steering, acceleration, brake, clutch,
                         pause, parkingbrake, wipers, cruiectrl, cruiectrlinc, cruiectrldec, 
                         cruiectrlres, light, hblight, lblinker, rblinker, quickpark, drive, 
                         reverse, cycl_zoom, tripreset, wipersback, wipers0, wipers1, wipers2,
                         wipers3, wipers4, horn, airhorn, lighthorn, cam1, cam2, cam3, cam4,
                         cam5, cam6, cam7, cam8, mapzoom_in, mapzoom_out, accmode, showmirrors,
                         hazards)

    return data # Plugins need to ALWAYS return the data



# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass

lastPress = time.time()
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Create text
            self.text = tk.Label(self.root, text="Please select a button to test using the keybind in the controls.\nOnly works when this panel is open.")
            self.text.pack(side="top", fill="both", expand=True)
            
            # Create a toggle button to select whether to add a delay between presses
            self.delay = tk.BooleanVar()
            self.delay.set(False)
            self.delayButton = tk.Checkbutton(self.root, text="Add delay between presses", variable=self.delay)
            self.delayButton.pack(side="top", fill="both", expand=True)
            
            # Create a selector for the buttons
            self.buttonSelector = tk.Listbox(self.root, width=30, height=20)
            self.buttonSelector.pack(side="left", fill="both", expand=True)
            
            # Load the buttons
            for i in buttonNames:
                self.buttonSelector.insert("end", i)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            global lastPress
            try:
                if controls.GetKeybindValue("Test SDK button"):
                    if time.time() - lastPress > 0.25 or self.delay.get() == False:
                        lastPress = time.time()
                        variables.APPENDDATANEXTFRAME = {"sdk":
                                                            {self.buttonSelector.get("active"):
                                                                True}}
                        print("Pressed " + self.buttonSelector.get("active"))
            except: pass
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)