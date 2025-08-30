# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *

import time

class Plugin(ETS2LAPlugin):
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Traffic", "TruckSimAPI"],
        listen=["*.py"],
        fps_cap=2
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    def init(self):
        ...

    def run(self):
        running = self.globals.tags.get_tag("running")
        print(running)