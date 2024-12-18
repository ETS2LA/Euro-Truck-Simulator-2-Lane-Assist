from ETS2LA.Plugin import *
from ETS2LA.UI import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"


def CheckForUploads():
    CurrentTime = time.time()
    for File in os.listdir(f"{variables.PATH}Data-Collection-End-To-End-Driving"):
        if str(File).endswith(".json") and str(File).replace(".json", ".png") not in os.listdir(f"{variables.PATH}Data-Collection-End-To-End-Driving"):
            try:
                os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}")
            except:
                pass
        if str(File).endswith(".png") and str(File).replace(".png", ".json") not in os.listdir(f"{variables.PATH}Data-Collection-End-To-End-Driving"):
            try:
                os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}")
            except:
                pass

    FilesReadyForUpload = []
    for File in os.listdir(f"{variables.PATH}Data-Collection-End-To-End-Driving"):
        if str(File).endswith(".json"):
            try:
                with open(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}", "r") as F:
                    Data = json.load(F)
                    Time = float(Data["Time"])
                    if Time + 604800 < CurrentTime:
                        FilesReadyForUpload.append(str(File))

                    # MARK: This can be removed in some days:
                    if "Game" not in Data:
                        1/0

            except:
                try:
                    os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}")
                except:
                    pass
                try:
                    os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File).replace('.json', '.png')}")
                except:
                    pass

    for File in FilesReadyForUpload:
        try:
            # MARK: Here the code for the uploading to the ets2la server

            # For now, just delete the files, because the cloud code is not ready yet
            try:
                os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}")
            except:
                pass
            try:
                os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File).replace('.json', '.png')}")
            except:
                pass
        except:
            pass
        try:
            os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File)}")
        except:
            pass
        try:
            os.remove(f"{variables.PATH}Data-Collection-End-To-End-Driving/{str(File).replace('.json', '.png')}")
        except:
            pass


class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "Data Collection End-To-End Driving"
    def Callback(self):
        print("test")
        self.plugin.DeleteAllData()
    def DeleteAllData(self):
        print("This is what is called when you press with this setup")
    def render(self):
        import ETS2LA.variables as variables
        Title("Data Collection End-To-End Driving")
        Label("This plugins sends annoymous driving data for our end-to-end driving model.\nAll the collected data will be available open source on Hugging Face:")
        Link("-> View current datasets on Huggingface", "https://huggingface.co/Glas42/End-To-End/tree/main/files")
        Separator()
        Label(f"The plugin sends images of your game window with data like current steering angle or driving speed to our server.\nIf you play your game in windowed mode, the plugin will still only capture the game. The capture of data will be paused when you are currently not actively playing the game, for example when you are currently AFK, paused the game or are not focusing the game window. Be aware that the plugin captures overlays over the game window for example the discord voice channel overlay.\n\nIf you have think that the plugin captured something you don't want in the public dataset, you have 7 days to delete the data before being uploaded to our server.\n\nThe data will be saved for the 7 days in this folder on your PC:\n{variables.PATH}Data-Collection-End-To-End-Driving\n\nIf you want to delete the data, just delete the files or the entire folder and they won't be uploaded to our server.")
        return RenderUI()


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Data Collection End-To-End Driving",
        version="1.0",
        description="This plugins sends annoymous driving data for our end-to-end driving model. All the collected data will be open source.",
        modules=["TruckSimAPI"],
    )

    author = Author(
        name="Glas42",
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 10
    settings_menu = SettingsMenu()

    def imports(self):
        global SCSTelemetry, ScreenCapture, variables, datetime, json, math, time, cv2, os

        from modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import modules.BetterScreenCapture.main as ScreenCapture
        import ETS2LA.variables as variables
        import threading
        import datetime
        import json
        import math
        import time
        import cv2
        import os

        global FOVValue
        global TruckSimAPI

        global LastCaptureTime
        global LastCaptureLocation

        FOVValue = self.globals.settings.FOV
        if FOVValue == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for the 'Data Collection End-To-End Driving' plugin! The plugin will disable itself.{NORMAL}\n")
            self.terminate()

        TruckSimAPI = SCSTelemetry()

        LastCaptureTime = 0
        LastCaptureLocation = 0, 0, 0

        X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
        Screen = ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2)
        ScreenCapture.Initialize(Screen=Screen - 1, Area=(X1, Y1, X2, Y2))

        threading.Thread(target=CheckForUploads, daemon=True).start()

    def run(self):
        CurrentTime = time.time()

        global TruckSimAPI

        global LastCaptureTime
        global LastCaptureLocation


        APIDATA = TruckSimAPI.update()

        CurrentLocation = APIDATA["truckPlacement"]["coordinateX"], APIDATA["truckPlacement"]["coordinateY"], APIDATA["truckPlacement"]["coordinateZ"]


        if (CurrentTime - LastCaptureTime < 3 or
            ScreenCapture.IsForegroundWindow(Name="Truck Simulator", Blacklist=["Discord"]) == False or
            APIDATA["sdkActive"] == False or
            APIDATA["pause"] == True or
            math.sqrt((LastCaptureLocation[0] - CurrentLocation[0])**2 + (LastCaptureLocation[1] - CurrentLocation[1])**2 + (LastCaptureLocation[2] - CurrentLocation[2])**2) < 0.5):
            time.sleep(0.2)
            return


        LastCaptureTime = CurrentTime
        LastCaptureLocation = APIDATA["truckPlacement"]["coordinateX"], APIDATA["truckPlacement"]["coordinateY"], APIDATA["truckPlacement"]["coordinateZ"]


        X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
        ScreenX, ScreenY, _, _ = ScreenCapture.GetScreenDimensions(ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2))
        if ScreenCapture.MonitorX1 != X1 - ScreenX or ScreenCapture.MonitorY1 != Y1 - ScreenY or ScreenCapture.MonitorX2 != X2 - ScreenX or ScreenCapture.MonitorY2 != Y2 - ScreenY:
            ScreenIndex = ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2)
            if ScreenCapture.Display != ScreenIndex - 1:
                if ScreenCapture.CaptureLibrary == "WindowsCapture":
                    ScreenCapture.StopWindowsCapture = True
                    while ScreenCapture.StopWindowsCapture == True:
                        time.sleep(0.01)
            MonitorX1, MonitorY1, MonitorX2, MonitorY2 = ScreenCapture.ValidateCaptureArea(ScreenIndex, X1 - ScreenX, Y1 - ScreenY, X2 - ScreenX, Y2 - ScreenY)
            ScreenCapture.Initialize(Screen=ScreenIndex - 1, Area=(MonitorX1, MonitorY1, MonitorX2, MonitorY2))

        Frame = ScreenCapture.Capture(ImageType="cropped")
        if type(Frame) == type(None) or Frame.shape[0] <= 0 or Frame.shape[1] <= 0:
            return


        GameValue = str(APIDATA["scsValues"]["game"]).lower()

        SpeedValue = float(APIDATA["truckFloat"]["speed"])
        SpeedLimitValue = float(APIDATA["truckFloat"]["speedLimit"])
        CruiseControlEnabledValue = bool(APIDATA["truckBool"]["cruiseControl"])
        CruiseControlSpeedValue = float(APIDATA["truckFloat"]["cruiseControlSpeed"])

        SteeringValue = float(APIDATA["truckFloat"]["gameSteer"])
        ThrottleValue = float(APIDATA["truckFloat"]["gameThrottle"])
        BrakeValue = float(APIDATA["truckFloat"]["gameBrake"])
        ClutchValue = float(APIDATA["truckFloat"]["gameClutch"])

        ParkBrakeValue = bool(APIDATA["truckBool"]["parkBrake"])
        WipersValue = bool(APIDATA["truckBool"]["wipers"])
        GearValue = int(APIDATA["truckInt"]["gear"])
        GearsValue = int(APIDATA["configUI"]["gears"])
        ReverseGearsValue = int(APIDATA["configUI"]["gearsReverse"])
        EngineRPMValue = float(APIDATA["truckFloat"]["engineRpm"])

        LeftIndicatorValue = bool(APIDATA["truckBool"]["blinkerLeftActive"])
        RightIndicatorValue = bool(APIDATA["truckBool"]["blinkerRightActive"])
        HazardLightsValue = bool(APIDATA["truckBool"]["lightsHazard"])
        ParkingLightsValue = bool(APIDATA["truckBool"]["lightsParking"])
        LowBeamLightsValue = bool(APIDATA["truckBool"]["lightsBeamLow"])
        HighBeamLightsValue = bool(APIDATA["truckBool"]["lightsBeamHigh"])
        BeaconLightsValue = bool(APIDATA["truckBool"]["lightsBeacon"])
        BrakeLightsValue = bool(APIDATA["truckBool"]["lightsBrake"])
        ReverseLightsValue = bool(APIDATA["truckBool"]["lightsReverse"])

        PositionXValue = float(APIDATA["truckPlacement"]["coordinateX"])
        PositionYValue = float(APIDATA["truckPlacement"]["coordinateY"])
        PositionZValue = float(APIDATA["truckPlacement"]["coordinateZ"])
        RotationXValue = float(APIDATA["truckPlacement"]["rotationX"])
        RotationYValue = float(APIDATA["truckPlacement"]["rotationY"])
        RotationZValue = float(APIDATA["truckPlacement"]["rotationZ"])

        CabinXValue = float(APIDATA["headPlacement"]["cabinOffsetX"] + APIDATA["configVector"]["cabinPositionX"])
        CabinYValue = float(APIDATA["headPlacement"]["cabinOffsetY"] + APIDATA["configVector"]["cabinPositionY"])
        CabinZValue = float(APIDATA["headPlacement"]["cabinOffsetZ"] + APIDATA["configVector"]["cabinPositionZ"])
        CabinRotationXValue = float(APIDATA["headPlacement"]["cabinOffsetrotationX"])
        CabinRotationYValue = float(APIDATA["headPlacement"]["cabinOffsetrotationY"])
        CabinRotationZValue = float(APIDATA["headPlacement"]["cabinOffsetrotationZ"])

        HeadXValue = float(APIDATA["headPlacement"]["headOffsetX"] + APIDATA["configVector"]["headPositionX"] + APIDATA["headPlacement"]["cabinOffsetX"] + APIDATA["configVector"]["cabinPositionX"])
        HeadYValue = float(APIDATA["headPlacement"]["headOffsetY"] + APIDATA["configVector"]["headPositionY"] + APIDATA["headPlacement"]["cabinOffsetY"] + APIDATA["configVector"]["cabinPositionY"])
        HeadZValue = float(APIDATA["headPlacement"]["headOffsetZ"] + APIDATA["configVector"]["headPositionZ"] + APIDATA["headPlacement"]["cabinOffsetZ"] + APIDATA["configVector"]["cabinPositionZ"])
        HeadRotationXValue = float(APIDATA["headPlacement"]["headOffsetrotationX"])
        HeadRotationYValue = float(APIDATA["headPlacement"]["headOffsetrotationY"])
        HeadRotationZValue = float(APIDATA["headPlacement"]["headOffsetrotationZ"])


        Data = {
            "Time": CurrentTime,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Game": GameValue,
            "FOVValue": FOVValue,
            "SpeedValue": SpeedValue,
            "SpeedLimitValue": SpeedLimitValue,
            "CruiseControlEnabledValue": CruiseControlEnabledValue,
            "CruiseControlSpeedValue": CruiseControlSpeedValue,
            "SteeringValue": SteeringValue,
            "ThrottleValue": ThrottleValue,
            "BrakeValue": BrakeValue,
            "ClutchValue": ClutchValue,
            "ParkBrakeValue": ParkBrakeValue,
            "WipersValue": WipersValue,
            "GearValue": GearValue,
            "GearsValue": GearsValue,
            "ReverseGearsValue": ReverseGearsValue,
            "EngineRPMValue": EngineRPMValue,
            "LeftIndicatorValue": LeftIndicatorValue,
            "RightIndicatorValue": RightIndicatorValue,
            "HazardLightsValue": HazardLightsValue,
            "ParkingLightsValue": ParkingLightsValue,
            "LowBeamLightsValue": LowBeamLightsValue,
            "HighBeamLightsValue": HighBeamLightsValue,
            "BeaconLightsValue": BeaconLightsValue,
            "BrakeLightsValue": BrakeLightsValue,
            "ReverseLightsValue": ReverseLightsValue,
            "PositionXValue": PositionXValue,
            "PositionYValue": PositionYValue,
            "PositionZValue": PositionZValue,
            "RotationXValue": RotationXValue,
            "RotationYValue": RotationYValue,
            "RotationZValue": RotationZValue,
            "CabinXValue": CabinXValue,
            "CabinYValue": CabinYValue,
            "CabinZValue": CabinZValue,
            "CabinRotationXValue": CabinRotationXValue,
            "CabinRotationYValue": CabinRotationYValue,
            "CabinRotationZValue": CabinRotationZValue,
            "HeadXValue": HeadXValue,
            "HeadYValue": HeadYValue,
            "HeadZValue": HeadZValue,
            "HeadRotationXValue": HeadRotationXValue,
            "HeadRotationYValue": HeadRotationYValue,
            "HeadRotationZValue": HeadRotationZValue
        }


        if os.path.exists(f"{variables.PATH}Data-Collection-End-To-End-Driving") == False:
            os.mkdir(f"{variables.PATH}Data-Collection-End-To-End-Driving")

        Name = str(CurrentTime)

        with open(f"{variables.PATH}Data-Collection-End-To-End-Driving/{Name}.json", "w") as F:
            json.dump(Data, F, indent=4)

        cv2.imwrite(f"{variables.PATH}Data-Collection-End-To-End-Driving/{Name}.png", Frame)