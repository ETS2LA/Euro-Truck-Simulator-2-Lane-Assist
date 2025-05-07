from ETS2LA.Plugin.attributes import Global, Plugins, PluginDescription, State
from ETS2LA.Plugin.settings import Settings
from ETS2LA.Plugin.author import Author

from ETS2LA.Utils.Console.logging import setup_process_logging
import ETS2LA.Events as Events
from ETS2LA.UI import *

from ETS2LA.Controls import ControlEvent

from multiprocessing import JoinableQueue, Queue
import threading
import importlib

from types import SimpleNamespace
from typing import Literal, List
import logging
import json
import math
import time
import sys
import os

class ETS2LAPlugin(object):
    """
    This is the main plugin object, you will see a list of attributes below.
    
    
    :param int fps_cap: The maximum frames per second the plugin will run at.
    :param Description description: The description of the plugin.
    :param Author author: The author of the plugin.
    :param list[ControlEvent] controls: The list of control events to listen to.
    :param Global globals: The global settings and tags.
    :param State state: Send a persistent state to the backend.
    :param Settings settings: The settings of the plugin.
    :param Plugins plugins: Interactions with other plugins.
    
    Functions:
        **notify(text: str, type: str)** - Show a notification in the frontend.\n
        **ask(text: str, options: list, description: str)** - Show a question in the frontend.\n
        **dialog(dialog: object)** - Show a dialog in the frontend.
    """
    path: str

    fps_cap: int = 30
    
    description: PluginDescription = PluginDescription()
    author: List[Author]
    controls: List[ControlEvent] = []
    settings_menu: None
    
    return_queue: JoinableQueue
    plugins_queue: JoinableQueue
    plugins_return_queue: JoinableQueue
    settings_menu_queue: JoinableQueue
    settings_menu_return_queue: JoinableQueue
    frontend_queue: JoinableQueue
    frontend_return_queue: JoinableQueue
    immediate_queue: JoinableQueue
    immediate_return_queue: JoinableQueue
    state_queue: JoinableQueue
    performance_queue: JoinableQueue
    performance_return_queue: JoinableQueue
    event_queue: JoinableQueue
    event_return_queue: Queue
    control_queue: JoinableQueue
    control_return_queue: JoinableQueue
    
    performance: list[tuple[float, float]] = []
    
    state: State
    """
    The state of the plugin shown in the frontend.
    
    Example:
    ```python
    while HeavyOperation():
        percentage = 0.66
        self.state.text = f"Loading... ({round(percentage * 100)}%)"
        self.state.progress = percentage
    
    self.state.reset()
    # or
    self.state.text = ""
    self.state.progress = -1
    ```
    """
    
    globals: Global
    """
    Global class for the plugin to access global settings and
    
    :param GlobalSettings settings: Access to the global settings.
    :param Tags tags: Access to the global tags.
    """
    settings: Settings
    """
    Access the local plugins settings file.
    
    Example:
    ```python
    # Get a setting (doesn't read / write)
    value = self.settings.setting_name
    # Set a setting (does write, don't use each frame)
    self.settings.setting_name = value
    ```
    """
    plugins: Plugins
    """
    Access all the other running plugins' information.
    
    Example:
    ```python
    # Get the plugin return data
    data = self.plugins.plugin_name
    ```
    """
    modules: SimpleNamespace
    """
    Access to all running modules that were defined in the description object.
    
    Example:
    ```python
    
    ```
    """
    
    def ensure_settings_file(self) -> None:
        path = self.path
        if not os.path.exists(f"{path}/settings.json"):
            os.makedirs(path, exist_ok=True)
            with open(f"{path}/settings.json", "w") as file:
                json.dump({}, file)
    
    def ensure_functions(self) -> None:
        if type(self).before != ETS2LAPlugin.before:
            raise TypeError("'before' is a reserved function name")
        if type(self).after != ETS2LAPlugin.after:
            raise TypeError("'after' is a reserved function name")
        if type(self).plugin != ETS2LAPlugin.plugin:
            raise TypeError("'plugin' is a reserved function name, please use 'run' instead")
        if "run" not in dir(type(self)):
            raise TypeError("Your plugin has to have a 'run' function.")
        if type(self).__name__ != "Plugin":
            raise TypeError("Please make sure the class is named 'Plugin'")
    
    def __new__(cls, path: str, return_queue: JoinableQueue, 
                                plugins_queue: JoinableQueue, plugins_return_queue: JoinableQueue, 
                                tags_queue: JoinableQueue, tags_return_queue: JoinableQueue,
                                settings_menu_queue: JoinableQueue, settings_menu_return_queue: JoinableQueue,
                                frontend_queue: JoinableQueue, frontend_return_queue: JoinableQueue,
                                immediate_queue: JoinableQueue, immediate_return_queue: JoinableQueue,
                                state_queue: JoinableQueue,
                                performance_queue: JoinableQueue, performance_return_queue: JoinableQueue,
                                event_queue: JoinableQueue, event_return_queue: Queue,
                                control_queue: JoinableQueue, control_return_queue: JoinableQueue
                                ) -> object:
        instance = super().__new__(cls)
        instance.path = path
        
        instance.return_queue = return_queue
        instance.plugins_queue = plugins_queue
        instance.plugins_return_queue = plugins_return_queue
        instance.settings_menu_queue = settings_menu_queue
        instance.settings_menu_return_queue = settings_menu_return_queue
        instance.frontend_queue = frontend_queue
        instance.frontend_return_queue = frontend_return_queue
        instance.immediate_queue = immediate_queue
        instance.immediate_return_queue = immediate_return_queue
        instance.state_queue = state_queue
        instance.performance_queue = performance_queue
        instance.performance_return_queue = performance_return_queue
        instance.event_queue = event_queue
        instance.event_return_queue = event_return_queue
        instance.control_queue = control_queue
        instance.control_return_queue = control_return_queue
        
        instance.plugins = Plugins(plugins_queue, plugins_return_queue)
        instance.globals = Global(tags_queue, tags_return_queue)
        instance.state = State(state_queue)
        
        instance.ensure_settings_file()
        instance.settings = Settings(path)
        
        if type(instance.author) != list:
            instance.author = [instance.author] # type: ignore
        
        return instance
   
    def load_modules(self) -> None:
        Events.events.plugin_object = self
        
        self.modules = SimpleNamespace()
        module_names = self.description.modules
        for module_name in module_names:
            module_path = f"Modules/{module_name}/main.py"
            if os.path.exists(module_path):
                python_object = importlib.import_module(module_path.replace("/", ".").replace(".py", ""))
                module = python_object.Module(self)
                setattr(self.modules, module_name, module)
            else:
                logging.warning(f"Module '{module_name}' not found in '{module_path}'")
    
    def __init__(self, *args) -> None:
        self.ensure_functions()
        self.load_modules()
        
        if "settings_menu" in dir(type(self)) and self.settings_menu != None:
            self.settings_menu.plugin = self

        threading.Thread(target=self.settings_menu_thread, daemon=True).start()
        threading.Thread(target=self.frontend_thread, daemon=True).start()
        threading.Thread(target=self.performance_thread, daemon=True).start()
        threading.Thread(target=self.event_listener, daemon=True).start()
        threading.Thread(target=self.control_listener, daemon=True).start()

        try: self.imports() # type: ignore # Might or might not exist.
        except Exception as ex:
            if type(ex) != AttributeError:
                logging.exception("Error in 'imports' function")
                
        try: self.init() # type: ignore # Might or might not exist.
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'init' function")
        
        try: self.initialize() # type: ignore # Might or might not exist.
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'initialize' function")
        
        try: self.Initialize() # type: ignore # Might or might not exist.
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'Initialize' function")

        while True:
            self.plugin()
    
    def settings_menu_thread(self):
        if "settings_menu" in dir(type(self)) and self.settings_menu != None:
            while True:
                self.settings_menu_queue.get()
                self.settings_menu_queue.task_done()
                self.settings_menu_return_queue.put(self.settings_menu.render())
    
    def control_listener(self):
        while True:
            data = self.control_queue.get()
            self.control_queue.task_done()
            
            for event in self.controls:
                if event.alias in data:
                    event.update(data[event.alias])
    
    def event_listener(self):
        while True:
            data = self.event_queue.get()
            args = data["args"]
            kwargs = data["kwargs"]
            kwargs.update({"queue": False})
            
            Events.events.emit(data["name"], *args, **kwargs)
            self.event_queue.task_done()
    
    def try_call(self, function_name: str, *args, **kwargs):
        if args == ([], {}):
            args = []
            
        if hasattr(self, function_name):
            return getattr(self, function_name)(*args, **kwargs)
        if hasattr(self.settings_menu, function_name):
            return getattr(self.settings_menu, function_name)(*args, **kwargs)
        return None
    
    def frontend_thread(self):
        while True:
            data = self.frontend_queue.get()
            try:
                if data["operation"] == "function":
                    args = data["args"]
                    kwargs = data["kwargs"]
                    self.try_call(data["target"], *args, **kwargs)
            except:
                logging.exception("Error calling frontend function")
                pass
            
            self.frontend_queue.task_done()
            self.frontend_return_queue.put(None)
           
    def terminate(self):
        self.immediate_queue.put({
            "operation": "terminate"
        })
            
    def performance_thread(self):
        while True:
            self.performance_queue.get()
            
            last_60_seconds = math.floor(time.perf_counter() - 60)
            self.performance = [x for x in self.performance if x[0] > last_60_seconds]
            
            return_performance = []
            # Prepare 60 datapoints for the last 60 seconds
            if len(self.performance) < 60:
                return_performance = self.performance
            else:
                for i in range(60):
                    return_performance.append(self.performance[math.floor(i * len(self.performance) / 60)])
            
            self.performance_queue.task_done()
            self.performance_return_queue.put(return_performance)
            
    def notify(self, text: str, type: Literal["info", "warning", "error", "success"] = "info"):
        self.immediate_queue.put({
            "operation": "notify", 
            "options": {
                "text": text,
                "type": type
            }    
        })
        data = self.immediate_return_queue.get()
        self.immediate_return_queue.task_done()
        return data    
    
    def ask(self, text: str, options: list, description: str = "") -> str:
        self.immediate_queue.put({
            "operation": "ask", 
            "options": {
                "text": text,
                "description": description,
                "options": options
            }
        })
        return self.immediate_return_queue.get()["response"]

    def dialog(self, dialog: object) -> dict:
        self.immediate_queue.put({
            "operation": "dialog", 
            "options": {
                "dialog": dialog.build(), # type: ignore
                "no_response": False
            }
        })
        return self.immediate_return_queue.get()

    def plugin(self) -> None:
        self.before()
        data = self.run() # type: ignore
        self.after(data)
            
    def before(self) -> None:
        self.plugin_run_start_time = time.perf_counter()
        
    def after(self, data) -> None:
        if data is not None:
            self.return_queue.put(data, block=True)

        self.plugin_run_end_time = time.perf_counter()
        time_to_sleep = max(1/self.fps_cap - (self.plugin_run_end_time - self.plugin_run_start_time), 0)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        
        self.performance.append((self.plugin_run_start_time, time.perf_counter() - self.plugin_run_start_time))
        
        # Only keep 60s of performance data
        while self.performance[0][0] < self.plugin_run_start_time - 60:
            self.performance.pop(0)

class PluginRunner:
    def __init__(self, plugin_name: str, plugin_description: PluginDescription, 
                    return_queue: JoinableQueue, 
                    plugins_queue: JoinableQueue, plugins_return_queue: JoinableQueue,
                    tags_queue: JoinableQueue, tags_return_queue: JoinableQueue,
                    settings_menu_queue: JoinableQueue, settings_menu_return_queue: JoinableQueue,
                    frontend_queue: JoinableQueue, frontend_return_queue: JoinableQueue,
                    immediate_queue: JoinableQueue, immediate_return_queue: JoinableQueue,
                    state_queue: JoinableQueue,
                    performance_queue: JoinableQueue, performance_return_queue: JoinableQueue,
                    event_queue: JoinableQueue, event_return_queue: Queue,
                    control_queue: JoinableQueue, control_return_queue: JoinableQueue
                    ):
        
        setup_process_logging(
            plugin_name,
            filepath=os.path.join(os.getcwd(), "logs", f"{plugin_name}.log"),
            console_level=logging.WARNING
        )
        
        self.plugin_name = plugin_name
        self.plugin_description = plugin_description
        
        self.return_queue = return_queue
        self.plugins_queue = plugins_queue
        self.plugins_return_queue = plugins_return_queue
        self.tags_queue = tags_queue
        self.tags_return_queue = tags_return_queue
        self.settings_menu_queue = settings_menu_queue
        self.settings_menu_return_queue = settings_menu_return_queue
        self.frontend_queue = frontend_queue
        self.frontend_return_queue = frontend_return_queue
        self.immediate_queue = immediate_queue
        self.immediate_return_queue = immediate_return_queue
        self.state_queue = state_queue
        self.performance_queue = performance_queue
        self.performance_return_queue = performance_return_queue
        self.event_queue = event_queue  
        self.event_return_queue = event_return_queue
        self.control_queue = control_queue
        self.control_return_queue = control_return_queue
        
        Events.events = Events.EventSystem(plugin_object=None, queue=self.event_return_queue)

        sys.path.append(os.path.join(os.getcwd(), "Plugins", plugin_name))

        try:
            # Import the plugin module
            plugin_module = importlib.import_module(f"Plugins.{plugin_name}.main")

            # Instantiate the Plugin class
            if hasattr(plugin_module, 'Plugin'):
                self.plugin_instance = plugin_module.Plugin(f"Plugins/{plugin_name}", return_queue, 
                                                                plugins_queue, plugins_return_queue, 
                                                                tags_queue, tags_return_queue,
                                                                settings_menu_queue, settings_menu_return_queue,
                                                                frontend_queue, frontend_return_queue,
                                                                immediate_queue, immediate_return_queue,
                                                                state_queue,
                                                                performance_queue, performance_return_queue,
                                                                event_queue, event_return_queue,
                                                                control_queue, control_return_queue
                                                                )
            else:
                immediate_queue.put({
                    "operation": "terminate"
                })
                raise ImportError(f"No class 'Plugin' found in module 'Plugins.{plugin_name}.main'")
        except:
            logging.exception(f"Error loading plugin '{plugin_name}'")
            
            class CrashDialog(ETS2LADialog):
                def render(self):
                    import traceback
                    with Form(classname="max-w-screen-sm"):
                        Title("Plugin Crashed")
                        Markdown(f"An error occurred while running the plugin `{plugin_name}`. The plugin will now disable.", classname="text-sm text-dimmed-foreground")
                        Markdown(f"```python\n{traceback.format_exc()}```", classname="max-w-screen-sm")
                        Button("Confirm", "", "submit", border=False)
                    return RenderUI()
            
            dialog = CrashDialog()
            
            self.immediate_queue.put({
                "operation": "dialog", 
                "options": {
                    "dialog": dialog.build(),
                    "no_response": True
                }
            })

            immediate_queue.put({
                "operation": "crash"
            })