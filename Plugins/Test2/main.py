# Framework
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from Plugins.Test.events import MyEvent
from ETS2LA.Events import events
import time


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Test2",
        version="1.0",
        description="Test",
        modules=["Camera"],
        listen=["*.py"],
        fps_cap=99999,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    def init(self): ...

    def run(self):
        args, kwargs = events.wait_for(MyEvent, timeout=20)
        print("My event was triggered at", time.time())
