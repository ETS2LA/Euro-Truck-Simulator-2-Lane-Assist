"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
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
import os
import math

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
API = None
lastX = 0
lastY = 0
def plugin(data):
    global API
    global lastX
    global lastY
    
    if API == None:
        API = ets2sdkclient()
    
    API.update()    
    
    # Save all data from the api to the data variable
    updateData(data)
    # Fix the speed to be km/h
    data["api"]["speed"] = API.speed * 3.6
    data["api"]["speedLimit"] = API.speedLimit * 3.6
    data["api"]["cruiseControlSpeed"] = API.cruiseControlSpeed * 3.6
    
    # Calculate the current driving angle based on this and last frames coordinates
    try:
        x = API.coordinateX
        y = API.coordinateZ
        
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


def updateData(data):
    data["api"] = {}
    data["api"]["time"] = API.time
    data["api"]["paused"] = API.paused
    data["api"]["ets2_telemetry_plugin_revision"] = API.ets2_telemetry_plugin_revision
    data["api"]["ets2_version_major"] = API.ets2_version_major
    data["api"]["ets2_version_minor"] = API.ets2_version_minor
    data["api"]["flags"] = API.flags
    data["api"]["speed"] = API.speed
    data["api"]["accelerationX"] = API.accelerationX
    data["api"]["accelerationY"] = API.accelerationY
    data["api"]["accelerationZ"] = API.accelerationZ
    data["api"]["coordinateX"] = API.coordinateX
    data["api"]["coordinateY"] = API.coordinateY
    data["api"]["coordinateZ"] = API.coordinateZ
    data["api"]["rotationX"] = API.rotationX
    data["api"]["rotationY"] = API.rotationY
    data["api"]["rotationZ"] = API.rotationZ
    data["api"]["gear"] = API.gear
    data["api"]["gears"] = API.gears
    data["api"]["gearRanges"] = API.gearRanges
    data["api"]["gearRangeActive"] = API.gearRangeActive
    data["api"]["engineRpm"] = API.engineRpm
    data["api"]["engineRpmMax"] = API.engineRpmMax
    data["api"]["fuel"] = API.fuel
    data["api"]["fuelCapacity"] = API.fuelCapacity
    data["api"]["fuelRate"] = API.fuelRate
    data["api"]["fuelAvgConsumption"] = API.fuelAvgConsumption
    data["api"]["userSteer"] = API.userSteer
    data["api"]["userThrottle"] = API.userThrottle
    data["api"]["userBrake"] = API.userBrake
    data["api"]["userClutch"] = API.userClutch
    data["api"]["gameSteer"] = API.gameSteer
    data["api"]["gameThrottle"] = API.gameThrottle
    data["api"]["gameBrake"] = API.gameBrake
    data["api"]["gameClutch"] = API.gameClutch
    data["api"]["truckWeight"] = API.truckWeight
    data["api"]["trailerWeight"] = API.trailerWeight
    data["api"]["modelOffset"] = API.modelOffset
    data["api"]["modelLength"] = API.modelLength
    data["api"]["trailerOffset"] = API.trailerOffset
    data["api"]["trailerLength"] = API.trailerLength
    data["api"]["timeAbsolute"] = API.timeAbsolute
    data["api"]["gearsReverse"] = API.gearsReverse
    data["api"]["trailerMass"] = API.trailerMass
    data["api"]["trailerId"] = API.trailerId
    data["api"]["trailerName"] = API.trailerName
    data["api"]["jobIncome"] = API.jobIncome
    data["api"]["jobDeadline"] = API.jobDeadline
    data["api"]["jobCitySource"] = API.jobCitySource
    data["api"]["jobCityDestination"] = API.jobCityDestination
    data["api"]["jobCompanySource"] = API.jobCompanySource
    data["api"]["jobCompanyDestination"] = API.jobCompanyDestination
    data["api"]["retarderBrake"] = API.retarderBrake
    data["api"]["shifterSlot"] = API.shifterSlot
    data["api"]["shifterToggle"] = API.shifterToggle
    data["api"]["aux"] = API.aux
    data["api"]["airPressure"] = API.airPressure
    data["api"]["brakeTemperature"] = API.brakeTemperature
    data["api"]["fuelWarning"] = API.fuelWarning
    data["api"]["adblue"] = API.adblue
    data["api"]["adblueConsumption"] = API.adblueConsumption
    data["api"]["oilPressure"] = API.oilPressure
    data["api"]["oilTemperature"] = API.oilTemperature
    data["api"]["waterTemperature"] = API.waterTemperature
    data["api"]["batteryVoltage"] = API.batteryVoltage
    data["api"]["lightsDashboard"] = API.lightsDashboard
    data["api"]["wearEngine"] = API.wearEngine
    data["api"]["wearTransmission"] = API.wearTransmission
    data["api"]["wearCabin"] = API.wearCabin
    data["api"]["wearChassis"] = API.wearChassis
    data["api"]["wearWheels"] = API.wearWheels
    data["api"]["wearTrailer"] = API.wearTrailer
    data["api"]["truckOdometer"] = API.truckOdometer
    data["api"]["cruiseControlSpeed"] = API.cruiseControlSpeed
    data["api"]["truckMake"] = API.truckMake
    data["api"]["truckMakeId"] = API.truckMakeId
    data["api"]["truckModel"] = API.truckModel
    data["api"]["speedLimit"] = API.speedLimit
    data["api"]["routeDistance"] = API.routeDistance
    data["api"]["routeTime"] = API.routeTime
    data["api"]["fuelRange"] = API.fuelRange
    data["api"]["gearRatioDifferential"] = API.gearRatioDifferential
    data["api"]["gearDashboard"] = API.gearDashboard
    data["api"]["CruiseControl"] = API.CruiseControl
    data["api"]["Wipers"] = API.Wipers
    data["api"]["ParkBrake"] = API.ParkBrake
    data["api"]["MotorBrake"] = API.MotorBrake
    data["api"]["ElectricEnabled"] = API.ElectricEnabled
    data["api"]["EngineEnabled"] = API.EngineEnabled
    data["api"]["BlinkerLeftActive"] = API.BlinkerLeftActive
    data["api"]["BlinkerRightActive"] = API.BlinkerRightActive
    data["api"]["BlinkerLeftOn"] = API.BlinkerLeftOn
    data["api"]["BlinkerRightOn"] = API.BlinkerRightOn
    data["api"]["LightsParking"] = API.LightsParking
    data["api"]["LightsBeamLow"] = API.LightsBeamLow
    data["api"]["LightsBeamHigh"] = API.LightsBeamHigh
    data["api"]["LightsAuxFront"] = API.LightsAuxFront
    data["api"]["LightsAuxRoof"] = API.LightsAuxRoof
    data["api"]["LightsBeacon"] = API.LightsBeacon
    data["api"]["LightsBrake"] = API.LightsBrake
    data["api"]["LightsReverse"] = API.LightsReverse
    data["api"]["BatteryVoltageWarning"] = API.BatteryVoltageWarning
    data["api"]["AirPressureWarning"] = API.AirPressureWarning
    data["api"]["AirPressureEmergency"] = API.AirPressureEmergency
    data["api"]["AdblueWarning"] = API.AdblueWarning
    data["api"]["OilPressureWarning"] = API.OilPressureWarning
    data["api"]["WaterTemperatureWarning"] = API.WaterTemperatureWarning
    data["api"]["TrailerAttached"] = API.TrailerAttached
    
    return data

# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    
    global API
    if API == None:
        API = ets2sdkclient()
    
    API.update()
    
    print("Plugin version: " + str(API.ets2_telemetry_plugin_revision))
    
    if API.ets2_telemetry_plugin_revision < 2:
        print("Plugin not installed")
        from tkinter import messagebox
        import webbrowser
        from plugins.PluginManager.main import UI
        if messagebox.askyesno("Plugin not installed", "SDK Plugin not installed, do you want to open the instructions?\nPlease re-enable the app plugin after installation.\nAlso make sure that the game is open!"):
            webbrowser.open("https://github.com/nlhans/ets2-sdk-plugin#installation")
            UI.disablePlugin(self=None, plugin = __import__("plugins.TruckSimAPI.main", fromlist=["PluginInformation", "onDisable", "onEnable"]))
        else:
            UI.disablePlugin(self=None, plugin = __import__("plugins.TruckSimAPI.main", fromlist=["PluginInformation", "onDisable", "onEnable"]))
    

def onDisable():
    pass

import mmap
import struct


class Ets2SdkBoolean():
    CruiseControl = 0
    Wipers = 1
    ParkBrake = 2
    MotorBrake = 3 
    ElectricEnabled = 4
    EngineEnabled = 5 

    BlinkerLeftActive = 6
    BlinkerRightActive = 7
    BlinkerLeftOn = 8
    BlinkerRightOn = 9

    LightsParking = 10
    LightsBeamLow = 11
    LightsBeamHigh = 12
    LightsAuxFront = 13
    LightsAuxRoof = 14
    LightsBeacon = 15
    LightsBrake = 16 
    LightsReverse = 17

    BatteryVoltageWarning = 18
    AirPressureWarning = 19
    AirPressureEmergency = 20
    AdblueWarning = 21
    OilPressureWarning = 22
    WaterTemperatureWarning = 23
    TrailerAttached = 24
        
class ets2sdkclient:
    def GetBool(self, i):
        if (i == Ets2SdkBoolean.TrailerAttached):
            return int(str(self.flags[1]), 16) > 0
        else:
            return int(str(self.aux[i]), 16) > 0
            
    def update(self):
        self.mm = mmap.mmap(0, 1024, "Local\SimTelemetryETS2")
        
        #[FieldOffset(0)]
        self.time = struct.unpack("I", self.mm[0:4])[0]
        #[FieldOffset(4)]
        self.paused = struct.unpack("I", self.mm[4:8])[0]
        
        
        #[FieldOffset(8)]
        self.ets2_telemetry_plugin_revision = struct.unpack("I", self.mm[8:12])[0]
        #[FieldOffset(12)]
        self.ets2_version_major = struct.unpack("I", self.mm[12:16])[0]
        #[FieldOffset(16)]
        self.ets2_version_minor = struct.unpack("I", self.mm[16:20])[0]
        
        #[FieldOffset(20)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 4)]
        self.flags = self.mm[20:24]
        
        #[FieldOffset(24)]
        self.speed = struct.unpack("f", self.mm[24:28])[0]
        #[FieldOffset(28)]
        self.accelerationX = struct.unpack("f", self.mm[28:32])[0]
        #[FieldOffset(32)]
        self.accelerationY = struct.unpack("f", self.mm[32:36])[0]
        #[FieldOffset(36)]
        self.accelerationZ = struct.unpack("f", self.mm[36:40])[0]


        #[FieldOffset(40)]
        self.coordinateX  = struct.unpack("f", self.mm[40:44])[0]
        #[FieldOffset(44)]
        self.coordinateY  = struct.unpack("f", self.mm[44:48])[0]
        #[FieldOffset(48)]
        self.coordinateZ = struct.unpack("f", self.mm[48:52])[0]


        #[FieldOffset(52)]
        self.rotationX = struct.unpack("f", self.mm[52:56])[0]
        #[FieldOffset(56)]
        self.rotationY = struct.unpack("f", self.mm[56:60])[0]
        #[FieldOffset(60)]
        self.rotationZ = struct.unpack("f", self.mm[60:64])[0]
        
        #[FieldOffset(64)]
        self.gear = struct.unpack("I", self.mm[64:68])[0]
        #[FieldOffset(68)]
        self.gears = struct.unpack("I", self.mm[68:72])[0]
        #[FieldOffset(72)]
        self.gearRanges = struct.unpack("I", self.mm[72:76])[0]
        #[FieldOffset(76)]
        self.gearRangeActive = struct.unpack("I", self.mm[76:80])[0]

        #[FieldOffset(80)]
        self.engineRpm = struct.unpack("f", self.mm[80:84])[0]
        #[FieldOffset(84)]
        self.engineRpmMax = struct.unpack("f", self.mm[84:88])[0]

        #[FieldOffset(88)]
        self.fuel = struct.unpack("f", self.mm[88:92])[0]
        #[FieldOffset(92)]
        self.fuelCapacity = struct.unpack("f", self.mm[92:96])[0]
        #[FieldOffset(96)]
        self.fuelRate = struct.unpack("f", self.mm[96:100])[0]
        #[FieldOffset(100)]
        self.fuelAvgConsumption = struct.unpack("f", self.mm[100:104])[0]
        
        #[FieldOffset(104)]
        self.userSteer = struct.unpack("f", self.mm[104:108])[0]
        #[FieldOffset(108)]
        self.userThrottle = struct.unpack("f", self.mm[108:112])[0]
        #[FieldOffset(112)]
        self.userBrake = struct.unpack("f", self.mm[112:116])[0]
        #[FieldOffset(116)]
        self.userClutch = struct.unpack("f", self.mm[116:120])[0]


        #[FieldOffset(120)]
        self.gameSteer = struct.unpack("f", self.mm[120:124])[0]
        #[FieldOffset(124)]
        self.gameThrottle = struct.unpack("f", self.mm[124:128])[0]
        #[FieldOffset(128)]
        self.gameBrake = struct.unpack("f", self.mm[128:132])[0]
        #[FieldOffset(132)]
        self.gameClutch = struct.unpack("f", self.mm[132:136])[0]
        
        
        #[FieldOffset(136)]
        self.truckWeight = struct.unpack("f", self.mm[136:140])[0]
        #[FieldOffset(140)]
        self.trailerWeight = struct.unpack("f", self.mm[140:144])[0]

        #[FieldOffset(144)]
        self.modelOffset = struct.unpack("I", self.mm[144:148])[0]
        #[FieldOffset(148)]
        self.modelLength = struct.unpack("I", self.mm[148:152])[0]

        #[FieldOffset(152)]
        self.trailerOffset = struct.unpack("I", self.mm[152:156])[0]
        #[FieldOffset(156)]
        self.trailerLength = struct.unpack("I", self.mm[156:160])[0]
        
        #[FieldOffset(160)]
        self.timeAbsolute = struct.unpack("I", self.mm[160:164])[0]
        #[FieldOffset(164)]
        self.gearsReverse = struct.unpack("I", self.mm[164:168])[0]

        #[FieldOffset(168)]
        self.trailerMass = struct.unpack("f", self.mm[168:172])[0]
        
        #[FieldOffset(172)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.trailerId = self.mm[172:236]
        
        #[FieldOffset(236)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self. trailerName = self.mm[236:300]

        #[FieldOffset(300)]
        self.jobIncome = struct.unpack("I", self.mm[300:304])[0]
        #[FieldOffset(304)]
        self.jobDeadline = struct.unpack("I", self.mm[304:308])[0]

        #[FieldOffset(308)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.jobCitySource = self.mm[308:372]
        
        #[FieldOffset(372)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.jobCityDestination = self.mm[372:436]

        #[FieldOffset(436)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.jobCompanySource = self.mm[436:500]
        
        #[FieldOffset(500)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.jobCompanyDestination = self.mm[500:564]
        
        #[FieldOffset(564)]
        self.retarderBrake = struct.unpack("I", self.mm[564:568])[0]
        #[FieldOffset(568)]
        self.shifterSlot = struct.unpack("I", self.mm[568:572])[0]
        #[FieldOffset(572)]
        self.shifterToggle = struct.unpack("I", self.mm[572:576])[0]
        #//#[FieldOffset(576)]
        #//self.fill;
        
        #[FieldOffset(580)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 24)]
        self.aux = self.mm[580:604]
        #[FieldOffset(604)]
        self.airPressure = struct.unpack("f", self.mm[604:608])[0]
        #[FieldOffset(608)]
        self.brakeTemperature = struct.unpack("f", self.mm[608:612])[0]
        #[FieldOffset(612)]
        self.fuelWarning = struct.unpack("I", self.mm[612:616])[0]
        #[FieldOffset(616)]
        self.adblue = struct.unpack("f", self.mm[616:620])[0]
        #[FieldOffset(620)]
        self.adblueConsumption = struct.unpack("f", self.mm[620:624])[0]
        #[FieldOffset(624)]
        self.oilPressure = struct.unpack("f", self.mm[624:628])[0]
        #[FieldOffset(628)]
        self.oilTemperature = struct.unpack("f", self.mm[628:632])[0]
        #[FieldOffset(632)]
        self.waterTemperature = struct.unpack("f", self.mm[632:636])[0]
        #[FieldOffset(636)]
        self.batteryVoltage = struct.unpack("f", self.mm[636:640])[0]
        #[FieldOffset(640)]
        self.lightsDashboard = struct.unpack("f", self.mm[640:644])[0]
        #[FieldOffset(644)]
        self.wearEngine = struct.unpack("f", self.mm[644:648])[0]
        #[FieldOffset(648)]
        self.wearTransmission = struct.unpack("f", self.mm[648:652])[0]
        #[FieldOffset(652)]
        self.wearCabin = struct.unpack("f", self.mm[652:656])[0]
        #[FieldOffset(656)]
        self.wearChassis = struct.unpack("f", self.mm[656:660])[0]
        #[FieldOffset(660)]
        self.wearWheels = struct.unpack("f", self.mm[660:664])[0]
        #[FieldOffset(664)]
        self.wearTrailer = struct.unpack("f", self.mm[664:668])[0]
        #[FieldOffset(668)]
        self.truckOdometer = struct.unpack("f", self.mm[668:672])[0]
        #[FieldOffset(672)]
        self.cruiseControlSpeed = struct.unpack("f", self.mm[672:676])[0]

        #[FieldOffset(676)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.truckMake = self.mm[676:740]
        #[FieldOffset(740)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.truckMakeId = self.mm[740:804]
        #[FieldOffset(804)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 64)]
        self.truckModel = self.mm[804:868]

        #[FieldOffset(868)]
        self.speedLimit = struct.unpack("f", self.mm[868:872])[0]

        #[FieldOffset(872)]
        self.routeDistance = struct.unpack("f", self.mm[872:876])[0]

        #[FieldOffset(876)]
        self.routeTime = struct.unpack("f", self.mm[876:880])[0]

        #[FieldOffset(880)]
        self.fuelRange = struct.unpack("f", self.mm[880:884])[0]

        #[FieldOffset(884)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 24)]
        #public float[] gearRatioForward;

        #[FieldOffset(980)]
        #[MarshalAs(UnmanagedType.ByValArray, SizeConst = 8)]
        #public float[] gearRatioReverse;

        #[FieldOffset(1012)]
        self.gearRatioDifferential = struct.unpack("f", self.mm[1012:1016])[0]

        #[FieldOffset(1016)]
        self.gearDashboard  = struct.unpack("I", self.mm[1016:1020])[0]
        
        # variables mapping from Ets2SdkClient 1.4.0
        self.CruiseControl = self.GetBool(Ets2SdkBoolean.CruiseControl)
        self.Wipers = self.GetBool(Ets2SdkBoolean.Wipers)
        self.ParkBrake = self.GetBool(Ets2SdkBoolean.ParkBrake)
        self.MotorBrake = self.GetBool(Ets2SdkBoolean.MotorBrake)
        self.ElectricEnabled = self.GetBool(Ets2SdkBoolean.ElectricEnabled)
        self.EngineEnabled = self.GetBool(Ets2SdkBoolean.EngineEnabled)

        self.BlinkerLeftActive = self.GetBool(Ets2SdkBoolean.BlinkerLeftActive)
        self.BlinkerRightActive = self.GetBool(Ets2SdkBoolean.BlinkerRightActive)
        self.BlinkerLeftOn = self.GetBool(Ets2SdkBoolean.BlinkerLeftOn)
        self.BlinkerRightOn = self.GetBool(Ets2SdkBoolean.BlinkerRightOn)

        self.LightsParking = self.GetBool(Ets2SdkBoolean.LightsParking)
        self.LightsBeamLow = self.GetBool(Ets2SdkBoolean.LightsBeamLow)
        self.LightsBeamHigh = self.GetBool(Ets2SdkBoolean.LightsBeamHigh)
        self.LightsAuxFront = self.GetBool(Ets2SdkBoolean.LightsAuxFront)
        self.LightsAuxRoof = self.GetBool(Ets2SdkBoolean.LightsAuxRoof)
        self.LightsBeacon = self.GetBool(Ets2SdkBoolean.LightsBeacon)
        self.LightsBrake = self.GetBool(Ets2SdkBoolean.LightsBrake)
        self.LightsReverse = self.GetBool(Ets2SdkBoolean.LightsReverse)

        self.BatteryVoltageWarning = self.GetBool(Ets2SdkBoolean.BatteryVoltageWarning)
        self.AirPressureWarning = self.GetBool(Ets2SdkBoolean.AirPressureWarning)
        self.AirPressureEmergency = self.GetBool(Ets2SdkBoolean.AirPressureEmergency)
        self.AdblueWarning = self.GetBool(Ets2SdkBoolean.AdblueWarning)
        self.OilPressureWarning = self.GetBool(Ets2SdkBoolean.OilPressureWarning)
        self.WaterTemperatureWarning = self.GetBool(Ets2SdkBoolean.WaterTemperatureWarning)
        self.TrailerAttached = self.GetBool(Ets2SdkBoolean.TrailerAttached)
        
        self.mm.close()
        
    def printall(self):
        attrs = vars(self)
        # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
        # now dump this in some way or another
        print(', \n'.join("%s: %s" % item for item in list(attrs.items())))

