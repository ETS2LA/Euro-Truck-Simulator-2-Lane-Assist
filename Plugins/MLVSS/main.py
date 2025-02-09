from ETS2LA.Plugin import *
from ETS2LA.UI import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="MLVSS",
        version="1.0",
        description="ML Vision Sensor System. In Development.",
        modules=["TruckSimAPI"]
    )

    author = Author(
        name="Glas42",
        url="https://github.com/OleFranz",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 1000

    def imports(self):
        global SCSTelemetry; from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        global ScreenCapture; import Modules.BetterScreenCapture.main as ScreenCapture
        global MLVSSVariables; import variables as MLVSSVariables
        global Settings; import ETS2LA.Utils.settings as Settings
        global Variables; import ETS2LA.variables as Variables
        global MLVSSUtils; import utils as MLVSSUtils
        global Mapping; import mapping as Mapping
        global UI; import ui as UI
        global time; import time

        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for MLVSS! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling MLVSS...")
            time.sleep(1)
            self.terminate()

        MLVSSVariables.self = self
        MLVSSVariables.FOV = FOV
        MLVSSVariables.TruckSimAPI = SCSTelemetry()

        ScreenCapture.Initialize()

        UI.Initialize()
        Mapping.Initialize()

        MLVSSUtils.Launch(Mapping)

    def run(self):
        ScreenCapture.TrackWindow(Name="Truck Simulator", Blacklist=["Discord"])

        MLVSSUtils.UpdateAPI()

        Frame = ScreenCapture.Capture(ImageType="cropped")
        if type(Frame) != type(None) and Frame.shape[0] > 0 and Frame.shape[1] > 0:
            MLVSSVariables.LatestFrame = Frame