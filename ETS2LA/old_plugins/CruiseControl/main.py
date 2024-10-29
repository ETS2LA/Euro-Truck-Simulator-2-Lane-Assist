from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import time


controls.RegisterKeybind("Pause/Resume Actions",
                         notBoundInfo="You can pause and resume the actions of\nthe CruiseControl plugin with this keybind.",
                         description="You can pause and resume the actions of\nthe CruiseControl plugin with this keybind.")

controls.RegisterKeybind("Cruise Control Speed Increase",
                         notBoundInfo="If you use the CruiseControl plugin,\nyou can increase the speed with this keybind.",
                         description="If you use the CruiseControl plugin,\nyou can increase the speed with this keybind.")

controls.RegisterKeybind("Cruise Control Speed Decrease",
                         notBoundInfo="If you use the CruiseControl plugin,\nyou can decrease the speed with this keybind.",
                         description="If you use the CruiseControl plugin,\nyou can decrease the speed with this keybind.")


runner:PluginRunner = None


def Initialize():
    global TruckSimAPI
    global SDKController
    global AutoEnable
    global AutoAccelerate
    global StepSize
    global LastCruiseControlSpeed
    global WaitForResponse
    global WaitForResponseTimer

    TruckSimAPI = runner.modules.TruckSimAPI
    SDKController = runner.modules.SDKController

    AutoEnable = settings.Get("CruiseControl", "AutoEnable", True)
    AutoAccelerate = settings.Get("CruiseControl", "AutoAccelerate", False)

    StepSize = "UNKNOWN"
    LastCruiseControlSpeed = None

    WaitForResponse = False
    WaitForResponseTimer = 0


def plugin():
    global StepSize
    global LastCruiseControlSpeed
    global WaitForResponse
    global WaitForResponseTimer
    global SDKController

    CurrentTime = time.time()

    data = {}
    data["api"] = TruckSimAPI.run()

    try:
        Speed = round(data["api"]["truckFloat"]["speed"], 2)
        SpeedLimit = round(data["api"]["truckFloat"]["speedLimit"], 2)
        CruiseControlSpeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"], 2)
        Throttle = data["api"]["truckFloat"]["userThrottle"]
        Brake = data["api"]["truckFloat"]["userBrake"]
        ParkBrake = data["api"]["truckBool"]["parkBrake"]
        GamePaused = data["api"]["pause"]
    except:
        return

    TargetSpeed = SpeedLimit

    TrafficLight = runner.GetData(["TrafficLightDetection"])[0]
    if TrafficLight != None and TrafficLight != "Plugin has not returned any data yet.":
        (TrafficLight, _) = TrafficLight

        if TrafficLight == "Red":
            TargetSpeed = 0

    Intersection = runner.GetData(["NavigationDetection"])[0]
    if Intersection == True:
        TargetSpeed = 9

    if Speed > 11.25 and LastCruiseControlSpeed != None and LastCruiseControlSpeed != CruiseControlSpeed:
        if abs(CruiseControlSpeed - LastCruiseControlSpeed) < 2.25:
            print(f"CruiseControl - Speed changed from {LastCruiseControlSpeed} to {CruiseControlSpeed}")
    LastCruiseControlSpeed = CruiseControlSpeed

    if Speed >= 9 and AutoEnable == True and WaitForResponse == False:
        SDKController.cruiectrl = bool(True)
        print("test")
        WaitForResponse = True
        WaitForResponseTimer = CurrentTime

    if WaitForResponseTimer + 1 < CurrentTime:
        WaitForResponse = False