"""
The plugin event system.

Example:
````python
from ETS2LA.Events import events

class MyPlugin(ETS2LAPlugin):
    ...
    # Listen for events
    @events.on('my_event')
    def on_my_event(self, *args, **kwargs):
        print('My event was triggered with args:', args, 'and kwargs:', kwargs)

    # Trigger events
    def run(self):
        events.emit('my_event', True, do_something='important')
        # events.trigger also works
        events.trigger('my_event', False, do_something='else')
```

Please note that all events are global. So listening or triggering events will affect the entire plugin system.

WARNING: This system will be rewritten completely in the future, it doesn't even work with the new plugin system yet!
"""
from .event_system import events, EventSystem