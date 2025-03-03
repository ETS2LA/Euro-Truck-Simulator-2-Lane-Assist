from multiprocessing import Queue
import time

if not __name__ == '__main__':
    class EventSystem:
        queue: Queue
        plugin_object = None
        
        def __init__(self, plugin_object=None, queue=None):
            self.plugin_object = plugin_object
            if queue is None:
                queue = Queue()
            self.queue = queue
            self.listeners = {}

        def on(self, event_name):
            def decorator(fn):
                if event_name not in self.listeners:
                    self.listeners[event_name] = []
                self.listeners[event_name].append(fn)
                return fn
            return decorator

        def emit(self, event_name, *args, **kwargs):
            """
            Call with queue=False to NOT emit the event into the queue 
            for the main thread to distribute.
            
            Essentially only the Plugin class itself should do it, as it's
            normal for the plugin to emit events globally.
            """

            if args is None:
                args = []
                
            if type(args) == tuple:
                args = list(args)

            if kwargs is None:
                kwargs = {}

            if "queue" not in kwargs or kwargs["queue"]:
                if self.queue is not None:
                    self.queue.put({
                        "name": event_name,
                        "args": args,
                        "kwargs": kwargs
                    })
                    #time.sleep(0.0001) # don't remove, it's black magic
                
            if "queue" in kwargs:
                del kwargs["queue"]
                
            if self.plugin_object != None:
                args.insert(0, self.plugin_object) # type: ignore
            
            if event_name in self.listeners:
                for listener in self.listeners[event_name]:
                    listener(*args, **kwargs)
        
        def trigger(self, event_name, *args, **kwargs):
            self.emit(event_name, *args, **kwargs)

    # Global (for the plugin) event system instance
    events = EventSystem()

else:
    print('event_system.py is not meant to be run directly.')