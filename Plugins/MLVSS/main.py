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
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 1000

    def imports(self):
        global Variables, Settings, time, UI

        import ETS2LA.Utils.settings as Settings
        import ETS2LA.variables as Variables
        import ui as UI
        import time

        global FOV

        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for MLVSS! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling MLVSS...")
            self.terminate()

        UI.Initialize()

    def run(self):
        CurrentTime = time.time()

        time.sleep(1/60)