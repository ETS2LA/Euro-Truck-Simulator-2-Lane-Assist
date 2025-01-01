# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.AR.classes import *

# General imports
import ETS2LA.Utils.settings as settings
import time

class Plugin(ETS2LAPlugin):
    fps_cap = 5
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test"
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    steering = False
    
    @events.on("ToggleSteering")
    def on_toggle_steering(self, state):
        print("Steering toggled:", state)
        self.steering = state
    
    def imports(self):
        ...

    def run(self):
        self.globals.tags.AR = [
            Polygon(
                points=[
                    Coordinate(10363.160, 48.543, -9228.122),
                    Coordinate(10362.160, 47.543, -9224.122),
                    Coordinate(10363.160, 46.543, -9228.122),
                    Coordinate(10363.160, 48.543, -9228.122)
                ],
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 255 / 2),
                thickness=2
            ),
            Polygon(
                points=[
                    Coordinate(10343.160, 48.543, -9228.122),
                    Coordinate(10342.160, 47.543, -9224.122),
                    Coordinate(10343.160, 46.543, -9228.122),
                    Coordinate(10343.160, 48.543, -9228.122)
                ],
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 255 / 2),
                thickness=2
            ),
        ]
        time.sleep(1)