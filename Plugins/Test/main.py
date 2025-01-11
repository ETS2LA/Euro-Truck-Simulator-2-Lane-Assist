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
        description="Test",
        listen=["*.py", "test.json"],
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
                    Coordinate(10358.160, 48.543, -9228.122),
                    Coordinate(10357.160, 47.543, -9224.122),
                    Coordinate(10358.160, 46.543, -9228.122),
                    Coordinate(10358.160, 48.543, -9228.122)
                ],
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 255 / 2),
                thickness=2,
                fade=Fade(
                    prox_fade_end=0,
                    prox_fade_start=0,
                    dist_fade_start=200,
                    dist_fade_end=200
                )
            ),
            Polygon(
                points=[
                    Coordinate(10348.160, 48.543, -9228.122),
                    Coordinate(10347.160, 47.543, -9224.122),
                    Coordinate(10348.160, 46.543, -9228.122),
                    Coordinate(10348.160, 48.543, -9228.122)
                ],
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 255 / 2),
                thickness=2
            ),
        ]
        time.sleep(1)