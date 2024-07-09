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
    global AutoEnable
    global AutoAccelerate
    global WaitForResponse
    global WaitForResponseTimer

    TruckSimAPI = runner.modules.TruckSimAPI

    AutoEnable = settings.Get("CruiseControl", "AutoEnable", True)
    AutoAccelerate = settings.Get("CruiseControl", "AutoAccelerate", False)

    WaitForResponse = False
    WaitForResponseTimer = 0


def plugin():
    global WaitForResponse
    global WaitForResponseTimer

    CurrentTime = time.time()

    data = {}
    data["api"] = TruckSimAPI.run()

    try:
        Speed = round(data["api"]["truckFloat"]["speed"]*3.6, 1)
        SpeedLimit = round(data["api"]["truckFloat"]["speedLimit"]*3.6, -1)
        CruiseControlSpeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)
        Throttle = data["api"]["truckFloat"]["userThrottle"]
        Brake = data["api"]["truckFloat"]["userBrake"]
        ParkBrake = data["api"]["truckBool"]["parkBrake"]
        GamePaused = data["api"]["pause"]
    except:
        return

    tld_data = runner.GetData(["TrafficLightDetection"])
    print(tld_data)