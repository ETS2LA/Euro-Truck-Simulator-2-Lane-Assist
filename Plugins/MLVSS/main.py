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
        global SCS_telemetry; from Modules.TruckSimAPI.main import scsTelemetry as SCS_telemetry
        global ScreenCapture; import Modules.BetterScreenCapture.main as ScreenCapture
        global Settings; import ETS2LA.Utils.settings as settings
        global variables; import ETS2LA.variables as variables
        global time; import time

        global MLVSS_variables; import variables as MLVSS_variables
        global MLVSS_mapping; import mapping as MLVSS_mapping
        global MLVSS_utils; import utils as MLVSS_utils
        global MLVSS_UI; import ui as MLVSS_UI

        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for MLVSS! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling MLVSS...")
            time.sleep(1)
            self.terminate()

        MLVSS_variables.plugin_self = self
        MLVSS_variables.FOV = FOV
        MLVSS_variables.SCS_telemetry = SCS_telemetry()

        ScreenCapture.Initialize()

        MLVSS_UI.initialize()

        MLVSS_mapping.initialize()
        MLVSS_utils.launch(MLVSS_mapping)

    def run(self):
        ScreenCapture.TrackWindow(Name="Truck Simulator", Blacklist=["Discord"])

        MLVSS_utils.update_telemetry()

        frame = ScreenCapture.Capture(ImageType="cropped")
        if type(frame) != type(None) and frame.shape[0] > 0 and frame.shape[1] > 0:
            MLVSS_variables.latest_frame = frame