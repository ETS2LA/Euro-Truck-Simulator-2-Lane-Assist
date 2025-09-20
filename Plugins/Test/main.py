# Framework
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from Plugins.Test.events import MyEvent
from Plugins.AdaptiveCruiseControl.controls import enable_disable
from ETS2LA.Events import events

# In another plugin


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Traffic", "TruckSimAPI"],
        listen=["*.py"],
        fps_cap=0.1,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    @events.on(MyEvent)
    def on_my_event(
        self, event_instance: MyEvent, *args, **kwargs
    ): ...  # print("My event was triggered at", event_instance.current_time)

    def init(self): ...

    def run(self):
        # data = [Position().randomize() for _ in range(100)]
        # MyEvent.trigger(events, current_time=time.time(), data=data)
        events.trigger(enable_disable.alias, enable_disable, True)
