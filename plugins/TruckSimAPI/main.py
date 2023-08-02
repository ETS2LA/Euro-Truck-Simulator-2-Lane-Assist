"""
Available values are : (in data["api"]["value"])
1. time
2. paused
3. ets2_telemetry_plugin_revision
4. ets2_version_major
5. ets2_version_minor
6. flags
7. speed
8. accelerationX
9. accelerationY
10. accelerationZ
11. coordinateX
12. coordinateY
13. coordinateZ
14. rotationX
15. rotationY
16. rotationZ
17. gear
18. gears
19. gearRanges
20. gearRangeActive
21. engineRpm
22. engineRpmMax
23. fuel
24. fuelCapacity
25. fuelRate
26. fuelAvgConsumption
27. userSteer
28. userThrottle
29. userBrake
30. userClutch
31. gameSteer
32. gameThrottle
33. gameBrake
34. gameClutch
35. truckWeight
36. trailerWeight
37. modelOffset
38. modelLength
39. trailerOffset
40. trailerLength
41. timeAbsolute
42. gearsReverse
43. trailerMass
44. trailerId
45. trailerName
46. jobIncome
47. jobDeadline
48. jobCitySource
49. jobCityDestination
50. jobCompanySource
51. jobCompanyDestination
52. retarderBrake
53. shifterSlot
54. shifterToggle
55. aux
56. airPressure
57. brakeTemperature
58. fuelWarning
59. adblue
60. adblueConsumption
61. oilPressure
62. oilTemperature
63. waterTemperature
64. batteryVoltage
65. lightsDashboard
66. wearEngine
67. wearTransmission
68. wearCabin
69. wearChassis
70. wearWheels
71. wearTrailer
72. truckOdometer
73. cruiseControlSpeed
74. truckMake
75. truckMakeId
76. truckModel
77. speedLimit
78. routeDistance
79. routeTime
80. fuelRange
81. gearRatioDifferential
82. gearDashboard
83. CruiseControl
84. Wipers
85. ParkBrake
86. MotorBrake
87. ElectricEnabled
88. EngineEnabled
89. BlinkerLeftActive
90. BlinkerRightActive
91. BlinkerLeftOn
92. BlinkerRightOn
93. LightsParking
94. LightsBeamLow
95. LightsBeamHigh
96. LightsAuxFront
97. LightsAuxRoof
98. LightsBeacon
99. LightsBrake
100. LightsReverse
101. BatteryVoltageWarning
102. AirPressureWarning
103. AirPressureEmergency
104. AdblueWarning
105. OilPressureWarning
106. WaterTemperatureWarning
107. TrailerAttached
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="TruckSimAPI", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="API for the app to communicate with ETS2 and ATS.",
    version="0.1",
    author="Cloud-121",
    url="https://github.com/Cloud-121/ETS2-Python-Api",
    type="dynamic", # = Panel
    dynamicOrder="before image capture" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.loading import LoadingWindow
import src.mainUI as mainUI
import time
import os
import math
from plugins.TruckSimAPI.scsPlugin import scsTelemetry

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
API = None
lastX = 0
lastY = 0
isConnected = False

def plugin(data):
    global API
    global lastX
    global lastY
    
    checkAPI()
    
    apiData = API.update()    
    data["api"] = apiData
    
    # Calculate the current driving angle based on this and last frames coordinates
    try:
        x = apiData["truckPosition"]["coordinateX"]
        y = apiData["truckPosition"]["coordinateZ"]
        
        dx = x - lastX
        dy = y - lastY
        
        # Make them a unit vector
        velocity = math.sqrt(dx**2 + dy**2)
        
        # Calculate the angle
        angle = math.degrees(math.atan2(dy, dx))
        
        # Add some smoothening to the angle
        try:
            angle = angle * 0.025 + data["last"]["api"]["angle"] * 0.975
        except: pass
        data["api"]["angle"] = angle
        data["api"]["velocity"] = [dx, dy]
        
        lastY = y
        lastX = x
        
    except: pass

    return data # Plugins need to ALWAYS return the data

def checkAPI():
    global API
    global loading
    global stop
    global isConnected
    stop = False
    
    if API == None:
        API = scsTelemetry()
        
    data = API.update()
    
    if data["scsValues"]["telemetryPluginRevision"] < 2:
        loading = LoadingWindow("Waiting for ETS2 connection...")
    while data["scsValues"]["telemetryPluginRevision"] < 2 and not stop: 
        isConnected = False
        data = API.update()
        loading.update()
        mainUI.root.update()
        time.sleep(0.1)

    try:
        loading.destroy()
    except: pass
    
    isConnected = True


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    
    global API
    if API == None:
        API = scsTelemetry()
    
    data = API.update()
    
    print("Plugin version: " + str(data["scsValues"]["telemetryPluginRevision"]))
    
    if data["scsValues"]["telemetryPluginRevision"] < 2:
        print("Plugin not installed")
        from tkinter import messagebox
        import webbrowser
        from plugins.PluginManager.main import UI
        if messagebox.askyesno("Plugin not installed", "SDK Plugin not installed or the game is not running, do you want to open the instructions?"):
            webbrowser.open("https://wiki.tumppi066.xyz/en/LaneAssist/InGame")
    

def onDisable():
    global stop
    global loading
    
    stop = True
    try:
        loading.destroy()
    except: pass
    

import mmap
import struct


# OLD CODE

#class Ets2SdkBoolean():
#    CruiseControl = 0
#    Wipers = 1
#    ParkBrake = 2
#    MotorBrake = 3 
#    ElectricEnabled = 4
#    EngineEnabled = 5 
#
#    BlinkerLeftActive = 6
#    BlinkerRightActive = 7
#    BlinkerLeftOn = 8
#    BlinkerRightOn = 9
#
#    LightsParking = 10
#    LightsBeamLow = 11
#    LightsBeamHigh = 12
#    LightsAuxFront = 13
#    LightsAuxRoof = 14
#    LightsBeacon = 15
#    LightsBrake = 16 
#    LightsReverse = 17
#
#    BatteryVoltageWarning = 18
#    AirPressureWarning = 19
#    AirPressureEmergency = 20
#    AdblueWarning = 21
#    OilPressureWarning = 22
#    WaterTemperatureWarning = 23
#    TrailerAttached = 24
#        
#class ets2sdkclient:
#            
#    def update(self):
#        self.mm = mmap.mmap(0, 1024, "Local\SimTelemetryETS2")
#        
#        #[FieldOffset(0)]
#        self.time = struct.unpack("I", self.mm[0:4])[0]
#        #[FieldOffset(4)]
#        self.paused = struct.unpack("I", self.mm[4:8])[0]
#        
#        
#        #[FieldOffset(8)]
#        self.ets2_telemetry_plugin_revision = struct.unpack("I", self.mm[8:12])[0]
#        #[FieldOffset(12)]
#        self.ets2_version_major = struct.unpack("I", self.mm[12:16])[0]
#        #[FieldOffset(16)]
#        self.ets2_version_minor = struct.unpack("I", self.mm[16:20])[0]
#        
#        #[FieldOffset(20)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
#        self.flags = self.mm[20:24]
#        
#        #[FieldOffset(24)]
#        self.speed = struct.unpack("f", self.mm[24:28])[0]
#        #[FieldOffset(28)]
#        self.accelerationX = struct.unpack("f", self.mm[28:32])[0]
#        #[FieldOffset(32)]
#        self.accelerationY = struct.unpack("f", self.mm[32:36])[0]
#        #[FieldOffset(36)]
#        self.accelerationZ = struct.unpack("f", self.mm[36:40])[0]
#
#
#        #[FieldOffset(40)]
#        self.coordinateX  = struct.unpack("f", self.mm[40:44])[0]
#        #[FieldOffset(44)]
#        self.coordinateY  = struct.unpack("f", self.mm[44:48])[0]
#        #[FieldOffset(48)]
#        self.coordinateZ = struct.unpack("f", self.mm[48:52])[0]
#
#
#        #[FieldOffset(52)]
#        self.rotationX = struct.unpack("f", self.mm[52:56])[0]
#        #[FieldOffset(56)]
#        self.rotationY = struct.unpack("f", self.mm[56:60])[0]
#        #[FieldOffset(60)]
#        self.rotationZ = struct.unpack("f", self.mm[60:64])[0]
#        
#        #[FieldOffset(64)]
#        self.gear = struct.unpack("I", self.mm[64:68])[0]
#        #[FieldOffset(68)]
#        self.gears = struct.unpack("I", self.mm[68:72])[0]
#        #[FieldOffset(72)]
#        self.gearRanges = struct.unpack("I", self.mm[72:76])[0]
#        #[FieldOffset(76)]
#        self.gearRangeActive = struct.unpack("I", self.mm[76:80])[0]
#
#        #[FieldOffset(80)]
#        self.engineRpm = struct.unpack("f", self.mm[80:84])[0]
#        #[FieldOffset(84)]
#        self.engineRpmMax = struct.unpack("f", self.mm[84:88])[0]
#
#        #[FieldOffset(88)]
#        self.fuel = struct.unpack("f", self.mm[88:92])[0]
#        #[FieldOffset(92)]
#        self.fuelCapacity = struct.unpack("f", self.mm[92:96])[0]
#        #[FieldOffset(96)]
#        self.fuelRate = struct.unpack("f", self.mm[96:100])[0]
#        #[FieldOffset(100)]
#        self.fuelAvgConsumption = struct.unpack("f", self.mm[100:104])[0]
#        
#        #[FieldOffset(104)]
#        self.userSteer = struct.unpack("f", self.mm[104:108])[0]
#        #[FieldOffset(108)]
#        self.userThrottle = struct.unpack("f", self.mm[108:112])[0]
#        #[FieldOffset(112)]
#        self.userBrake = struct.unpack("f", self.mm[112:116])[0]
#        #[FieldOffset(116)]
#        self.userClutch = struct.unpack("f", self.mm[116:120])[0]
#
#
#        #[FieldOffset(120)]
#        self.gameSteer = struct.unpack("f", self.mm[120:124])[0]
#        #[FieldOffset(124)]
#        self.gameThrottle = struct.unpack("f", self.mm[124:128])[0]
#        #[FieldOffset(128)]
#        self.gameBrake = struct.unpack("f", self.mm[128:132])[0]
#        #[FieldOffset(132)]
#        self.gameClutch = struct.unpack("f", self.mm[132:136])[0]
#        
#        
#        #[FieldOffset(136)]
#        self.truckWeight = struct.unpack("f", self.mm[136:140])[0]
#        #[FieldOffset(140)]
#        self.trailerWeight = struct.unpack("f", self.mm[140:144])[0]
#
#        #[FieldOffset(144)]
#        self.modelOffset = struct.unpack("I", self.mm[144:148])[0]
#        #[FieldOffset(148)]
#        self.modelLength = struct.unpack("I", self.mm[148:152])[0]
#
#        #[FieldOffset(152)]
#        self.trailerOffset = struct.unpack("I", self.mm[152:156])[0]
#        #[FieldOffset(156)]
#        self.trailerLength = struct.unpack("I", self.mm[156:160])[0]
#        
#        #[FieldOffset(160)]
#        self.timeAbsolute = struct.unpack("I", self.mm[160:164])[0]
#        #[FieldOffset(164)]
#        self.gearsReverse = struct.unpack("I", self.mm[164:168])[0]
#
#        #[FieldOffset(168)]
#        self.trailerMass = struct.unpack("f", self.mm[168:172])[0]
#        
#        #[FieldOffset(172)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.trailerId = self.mm[172:236]
#        
#        #[FieldOffset(236)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self. trailerName = self.mm[236:300]
#
#        #[FieldOffset(300)]
#        self.jobIncome = struct.unpack("I", self.mm[300:304])[0]
#        #[FieldOffset(304)]
#        self.jobDeadline = struct.unpack("I", self.mm[304:308])[0]
#
#        #[FieldOffset(308)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.jobCitySource = self.mm[308:372]
#        
#        #[FieldOffset(372)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.jobCityDestination = self.mm[372:436]
#
#        #[FieldOffset(436)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.jobCompanySource = self.mm[436:500]
#        
#        #[FieldOffset(500)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.jobCompanyDestination = self.mm[500:564]
#        
#        #[FieldOffset(564)]
#        self.retarderBrake = struct.unpack("I", self.mm[564:568])[0]
#        #[FieldOffset(568)]
#        self.shifterSlot = struct.unpack("I", self.mm[568:572])[0]
#        #[FieldOffset(572)]
#        self.shifterToggle = struct.unpack("I", self.mm[572:576])[0]
#        #//#[FieldOffset(576)]
#        #//self.fill;
#        
#        #[FieldOffset(580)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 24)]
#        self.aux = self.mm[580:604]
#        #[FieldOffset(604)]
#        self.airPressure = struct.unpack("f", self.mm[604:608])[0]
#        #[FieldOffset(608)]
#        self.brakeTemperature = struct.unpack("f", self.mm[608:612])[0]
#        #[FieldOffset(612)]
#        self.fuelWarning = struct.unpack("I", self.mm[612:616])[0]
#        #[FieldOffset(616)]
#        self.adblue = struct.unpack("f", self.mm[616:620])[0]
#        #[FieldOffset(620)]
#        self.adblueConsumption = struct.unpack("f", self.mm[620:624])[0]
#        #[FieldOffset(624)]
#        self.oilPressure = struct.unpack("f", self.mm[624:628])[0]
#        #[FieldOffset(628)]
#        self.oilTemperature = struct.unpack("f", self.mm[628:632])[0]
#        #[FieldOffset(632)]
#        self.waterTemperature = struct.unpack("f", self.mm[632:636])[0]
#        #[FieldOffset(636)]
#        self.batteryVoltage = struct.unpack("f", self.mm[636:640])[0]
#        #[FieldOffset(640)]
#        self.lightsDashboard = struct.unpack("f", self.mm[640:644])[0]
#        #[FieldOffset(644)]
#        self.wearEngine = struct.unpack("f", self.mm[644:648])[0]
#        #[FieldOffset(648)]
#        self.wearTransmission = struct.unpack("f", self.mm[648:652])[0]
#        #[FieldOffset(652)]
#        self.wearCabin = struct.unpack("f", self.mm[652:656])[0]
#        #[FieldOffset(656)]
#        self.wearChassis = struct.unpack("f", self.mm[656:660])[0]
#        #[FieldOffset(660)]
#        self.wearWheels = struct.unpack("f", self.mm[660:664])[0]
#        #[FieldOffset(664)]
#        self.wearTrailer = struct.unpack("f", self.mm[664:668])[0]
#        #[FieldOffset(668)]
#        self.truckOdometer = struct.unpack("f", self.mm[668:672])[0]
#        #[FieldOffset(672)]
#        self.cruiseControlSpeed = struct.unpack("f", self.mm[672:676])[0]
#
#        #[FieldOffset(676)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.truckMake = self.mm[676:740]
#        #[FieldOffset(740)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.truckMakeId = self.mm[740:804]
#        #[FieldOffset(804)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
#        self.truckModel = self.mm[804:868]
#
#        #[FieldOffset(868)]
#        self.speedLimit = struct.unpack("f", self.mm[868:872])[0]
#
#        #[FieldOffset(872)]
#        self.routeDistance = struct.unpack("f", self.mm[872:876])[0]
#
#        #[FieldOffset(876)]
#        self.routeTime = struct.unpack("f", self.mm[876:880])[0]
#
#        #[FieldOffset(880)]
#        self.fuelRange = struct.unpack("f", self.mm[880:884])[0]
#
#        #[FieldOffset(884)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 24)]
#        #public float[] gearRatioForward;
#
#        #[FieldOffset(980)]
#        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
#        #public float[] gearRatioReverse;
#
#        #[FieldOffset(1012)]
#        self.gearRatioDifferential = struct.unpack("f", self.mm[1012:1016])[0]
#
#        #[FieldOffset(1016)]
#        self.gearDashboard  = struct.unpack("I", self.mm[1016:1020])[0]
#        
#        # variables mapping from Ets2SdkClient 1.4.0
#        self.CruiseControl = self.GetBool(Ets2SdkBoolean.CruiseControl)
#        self.Wipers = self.GetBool(Ets2SdkBoolean.Wipers)
#        self.ParkBrake = self.GetBool(Ets2SdkBoolean.ParkBrake)
#        self.MotorBrake = self.GetBool(Ets2SdkBoolean.MotorBrake)
#        self.ElectricEnabled = self.GetBool(Ets2SdkBoolean.ElectricEnabled)
#        self.EngineEnabled = self.GetBool(Ets2SdkBoolean.EngineEnabled)
#
#        self.BlinkerLeftActive = self.GetBool(Ets2SdkBoolean.BlinkerLeftActive)
#        self.BlinkerRightActive = self.GetBool(Ets2SdkBoolean.BlinkerRightActive)
#        self.BlinkerLeftOn = self.GetBool(Ets2SdkBoolean.BlinkerLeftOn)
#        self.BlinkerRightOn = self.GetBool(Ets2SdkBoolean.BlinkerRightOn)
#
#        self.LightsParking = self.GetBool(Ets2SdkBoolean.LightsParking)
#        self.LightsBeamLow = self.GetBool(Ets2SdkBoolean.LightsBeamLow)
#        self.LightsBeamHigh = self.GetBool(Ets2SdkBoolean.LightsBeamHigh)
#        self.LightsAuxFront = self.GetBool(Ets2SdkBoolean.LightsAuxFront)
#        self.LightsAuxRoof = self.GetBool(Ets2SdkBoolean.LightsAuxRoof)
#        self.LightsBeacon = self.GetBool(Ets2SdkBoolean.LightsBeacon)
#        self.LightsBrake = self.GetBool(Ets2SdkBoolean.LightsBrake)
#        self.LightsReverse = self.GetBool(Ets2SdkBoolean.LightsReverse)
#
#        self.BatteryVoltageWarning = self.GetBool(Ets2SdkBoolean.BatteryVoltageWarning)
#        self.AirPressureWarning = self.GetBool(Ets2SdkBoolean.AirPressureWarning)
#        self.AirPressureEmergency = self.GetBool(Ets2SdkBoolean.AirPressureEmergency)
#        self.AdblueWarning = self.GetBool(Ets2SdkBoolean.AdblueWarning)
#        self.OilPressureWarning = self.GetBool(Ets2SdkBoolean.OilPressureWarning)
#        self.WaterTemperatureWarning = self.GetBool(Ets2SdkBoolean.WaterTemperatureWarning)
#        self.TrailerAttached = self.GetBool(Ets2SdkBoolean.TrailerAttached)
#        
#        self.mm.close()
#        
#    def printall(self):
#        attrs = vars(self)
#        # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
#        # now dump this in some way or another
#        print(', \n'.join("%s: %s" % item for item in list(attrs.items())))



class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def updateData(self):
            self.list.delete(0, tk.END)
            for key, value in self.data["api"].items():
                self.list.insert(tk.END, str(key) + ": " + str(value))
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            
            ttk.Button(self.root, text="Update Data", command=self.updateData).pack()
            ttk.Label(self.root, text="Will only work when the app is enabled -> scrollable").pack()
            # Create a list to hold all of the API data
            self.listVar = tk.StringVar()
            self.list = tk.Listbox(self.root, width=600, height=520, border=0, highlightthickness=0, listvariable=self.listVar)
            self.list.pack()
            
            
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
            self.data = data
    
    except Exception as ex:
        print(ex.args)