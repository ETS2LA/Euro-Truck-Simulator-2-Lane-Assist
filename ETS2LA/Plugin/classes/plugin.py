from ETS2LA.Plugin.classes.attributes import Global, PluginDescription, State
from ETS2LA.Plugin.classes.settings import Settings
from ETS2LA.Plugin.classes.author import Author

from ETS2LA.Plugin.message import Channel, PluginMessage

import ETS2LA.Events as Events
from ETS2LA.UI import *

from ETS2LA.Controls import ControlEvent

from multiprocessing import Queue
import importlib

from types import SimpleNamespace
from typing import Literal, List
import logging
import json
import math
import time
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
        **notify(text: str, type: str)** - Show a notification in the frontend.
    """
    path: str

    fps_cap: int = 30
    
    description: PluginDescription = PluginDescription()
    author: List[Author]
    controls: List[ControlEvent] = []
    pages: List[ETS2LAPage] = []
    
    queue: Queue
    return_queue: Queue
    
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
        if "run" not in dir(type(self)):
            raise TypeError("Your plugin has to have a 'run' function.")
        if type(self).__name__ != "Plugin":
            raise TypeError("Please make sure the class is named 'Plugin'")
    
    def __new__(cls, path: str, queue: Queue, return_queue: Queue, get_tag: Callable, set_tag: Callable) -> object:
        instance = super().__new__(cls)
        instance.path = path
        
        instance.queue = queue
        instance.return_queue = return_queue
                
        instance.globals = Global(get_tag, set_tag)
        instance.state = State(return_queue)
        
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
            
        if "pages" in dir(type(self)) and self.pages != None:
            for page in self.pages:
                page.plugin = self
                page.settings = self.settings

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
    
    # def event_listener(self):
    #     while True:
    #         data = self.event_queue.get()
    #         args = data["args"]
    #         kwargs = data["kwargs"]
    #         kwargs.update({"queue": False})
    #         
    #         Events.events.emit(data["name"], *args, **kwargs)
    #         self.event_queue.task_done()
    
    def try_call(self, function_name: str, *args, **kwargs):
        if args == ([], {}):
            args = []
            
        if hasattr(self, function_name):
            return getattr(self, function_name)(*args, **kwargs)
        if hasattr(self.settings_menu, function_name):
            return getattr(self.settings_menu, function_name)(*args, **kwargs)
        return None
           
    def terminate(self):
        self.return_queue.put(PluginMessage(
            Channel.STOP_PLUGIN, {}
        ), block=False)
        
        # Wait for the plugin to be terminated
        while True:
            time.sleep(1)
            
    def notify(self, text: str, type: Literal["info", "warning", "error", "success"] = "info"):
        self.return_queue.put(PluginMessage(
            Channel.NOTIFICATION, {
                "text": text,
                "type": type
            }
        ), block=False)
            
    def before(self) -> None:
        self.plugin_run_start_time = time.perf_counter()
        
    def after(self) -> None:
        self.plugin_run_end_time = time.perf_counter()
        time_to_sleep = max(1/self.fps_cap - (self.plugin_run_end_time - self.plugin_run_start_time), 0)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        
        self.performance.append((self.plugin_run_start_time, time.perf_counter() - self.plugin_run_start_time))
        
        # Only save last 60 seconds of performance data
        while self.performance[0][0] < time.perf_counter() - 60:
            self.performance.pop(0)