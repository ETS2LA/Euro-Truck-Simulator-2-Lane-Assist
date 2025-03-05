# Framework
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *

event = ControlEvent(
    "test",
    "Test",
    "button",
    default="k"
)

class Plugin(ETS2LAPlugin):
    fps_cap = 5
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Camera"],
        listen=["*.py"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    controls = [
        event
    ]
    
    steering = False
    
    @events.on("test")
    def on_test(self, state):
        print("Value changed to:", state)
    
    def imports(self):
        ...

    def run(self):
        print(event.pressed())