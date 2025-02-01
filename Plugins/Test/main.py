# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.AR.classes import *
from ETS2LA.Events.classes import FinishedJob

# General imports
from ETS2LA.Utils.umami import TriggerEvent
import ETS2LA.Utils.settings as settings
import time

class Plugin(ETS2LAPlugin):
    fps_cap = 5
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Camera"],
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
            Line(
                Coordinate(0, 0, 0, True),
                Coordinate(0, 0, 0, True),
                Color(255, 255, 255, 100),
                3,
                fade=Fade(0, 100, 100, 200)
            )
            for i in range(9)
        ]
        time.sleep(10)