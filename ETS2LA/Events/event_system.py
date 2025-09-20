import logging
import inspect
import uuid
import time


class EventSystem:
    plugin_object = None
    emit_event: callable

    def __init__(self, plugin_object: object = None, emit_event: callable = None):
        self.listeners = {}
        self.waiters = {}
        self.plugin_object = plugin_object
        self.emit_event = emit_event

    def on(self, event):
        if not isinstance(event, str):
            event = event.alias  # Assume it's an Event object

        def decorator(fn):
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(fn)
            return fn

        return decorator

    def emit(self, event_name, event_object, *args, **kwargs):
        """Call with `queue=False` to NOT emit the event into the queue
        for the main thread to distribute.

        Essentially only the Plugin class itself should do it, as it's
        normal for the plugin to emit events globally.
        """
        if args is None:
            args = []

        if isinstance(args, tuple):
            args = list(args)

        if kwargs is None:
            kwargs = {}

        if "queue" not in kwargs or kwargs["queue"]:
            if "queue" in kwargs:
                del kwargs["queue"]
            if self.emit_event:
                self.emit_event(event_name, event_object, *args, **kwargs)
            else:
                logging.warning(
                    "EventSystem.emit called with queue=True but no emit_event function provided!"
                )

        if "queue" in kwargs:
            del kwargs["queue"]

        if self.plugin_object is None:
            logging.info("EventSystem.emit called but no plugin_object provided!")
            return

        if event_name in self.listeners:
            for function in self.listeners[event_name]:
                sig = inspect.signature(function)
                params = list(sig.parameters.keys())
                if params and params[0] == "self":
                    call_args = [self.plugin_object, event_object] + args
                else:
                    call_args = [event_object] + args
                function(*call_args, **kwargs)

        if event_name in self.waiters:
            for waiter in self.waiters[event_name]:
                waiter["result"] = (event_object, args, kwargs)

    def trigger(self, event_name, event_object, *args, **kwargs):
        self.emit(event_name, event_object, *args, **kwargs)

    def wait_for(self, event, timeout=5) -> tuple[object, list, dict]:
        """This function will return a tuple of (event_instance, args, kwargs)
        when the event is triggered, or raise TimeoutError if timed out."""
        if not isinstance(event, str):
            event = event.alias  # Assume it's an Event object

        id = str(uuid.uuid4())
        if not self.waiters.get(event):
            self.waiters[event] = []

        self.waiters[event].append({"id": id, "result": None})
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for event {event}")
            for waiter in self.waiters[event]:
                if waiter["id"] == id and waiter["result"] is not None:
                    self.waiters[event].remove(waiter)
                    return waiter["result"]


# Global (for the plugin) event system instance
events = EventSystem()
