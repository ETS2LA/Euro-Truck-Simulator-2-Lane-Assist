# Framework
from ETS2LA.Plugin import *
from ETS2LA.UI import * 

# General imports
import ETS2LA.backend.settings as settings
import time
        
class FOVDialog(ETS2LADialog):
    def render(self):
        with Form():
            Title("events.vehicle_change.vehicle_change")
            Description("events.vehicle_change.vehicle_change_description")
            Input("events.vehicle_change.vehicle_change", "fov", "number", default=settings.Get("global", "FOV", 77))
        return RenderUI()

class Plugin(ETS2LAPlugin):
    fps_cap = 15
    
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
    
    def imports(self):
        ...

    def run(self):
        return_values = self.dialog(FOVDialog())
        print(return_values)
        time.sleep(5)