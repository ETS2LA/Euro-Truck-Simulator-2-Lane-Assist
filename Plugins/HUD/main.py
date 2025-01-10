# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.AR.classes import *

# General imports
import ETS2LA.Utils.settings as settings
import time

class Plugin(ETS2LAPlugin):
    fps_cap = 2
    
    description = PluginDescription(
        name="HUD",
        version="1.0",
        description="Creates a heads up display on the windshield. Needs the AR plugin to work.",
        modules=["TruckSimAPI"]
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    def imports(self):
        ...

    def run(self):
        data = self.modules.TruckSimAPI.run()
        
        speed = data["truckFloat"]["speed"] * 3.6
        speed_text = Coordinate(-0.225, -1.8, -10, relative=True, rotation_relative=True)
        unit_text = Coordinate(-0.225, -2.15, -10, relative=True, rotation_relative=True)   
        
        self.globals.tags.AR = [
            Text(
                unit_text,
                "km/h",
                size=16,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            ),
            Text(
                speed_text,
                f"{speed:.0f}",
                size=30,
                color=Color(255, 255, 255),
                fade=Fade(prox_fade_end=0, prox_fade_start=0, dist_fade_end=100, dist_fade_start=100),
            )
        ]