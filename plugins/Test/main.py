# Framework
from ETS2LA.Plugin import *
from ETS2LA.UI import * 

# General imports
import ETS2LA.backend.settings as settings
import time
        

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
        self.state.text = "Doing something..."
        self.state.progress = 0
        time.sleep(1)
        self.state.progress = 20
        time.sleep(1)
        self.state.progress = 40
        time.sleep(1)
        self.state.progress = 60
        time.sleep(1)
        self.state.progress = 80
        time.sleep(1)
        self.state.progress = 100
        time.sleep(1)
        self.state.reset()
        time.sleep(3)