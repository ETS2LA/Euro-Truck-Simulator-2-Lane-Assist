from ETS2LA.utils.dictionaries import merge
from multiprocessing import JoinableQueue
from typing import Literal
import threading
import logging
import json
import time

class Plugins:
    def __init__(self, plugins_queue: JoinableQueue, plugins_return_queue: JoinableQueue):
        self.plugins_queue = plugins_queue
        self.plugins_return_queue = plugins_return_queue

    def __getattr__(self, name):
        self.plugins_queue.put(name, block=True)
        response = self.plugins_return_queue.get()
        return response
    
class Tags:
    def __init__(self, tags_queue: JoinableQueue, tags_return_queue: JoinableQueue):
        self.tags_queue = tags_queue
        self.tags_return_queue = tags_return_queue

    def __getattr__(self, name):
        if name in ["tags_queue", "tags_return_queue"]:
            return super().__getattr__(name)
        
        tag_dict = {
            "operation": "read",
            "tag": name
        }
        self.tags_queue.put(tag_dict, block=True)
        response = self.tags_return_queue.get()
        return response
    
    def __setattr__(self, name, value):
        if name in ["tags_queue", "tags_return_queue"]:
            return super().__setattr__(name, value)
        
        tag_dict = {
            "operation": "write",
            "tag": name,
            "value": value
        }
        self.tags_queue.put(tag_dict, block=True)
        response = self.tags_return_queue.get()
        return response
    
    def merge(self, tag_dict: dict):
        if tag_dict is None:
            return None
        
        plugins = tag_dict.keys()
        count = len(plugins)
                
        data = {}
        for plugin in tag_dict:
            if type(tag_dict[plugin]) == dict:
                if count > 1:
                    data = merge(data, tag_dict[plugin])
                else:
                    data = tag_dict[plugin]
                    break
            else: 
                data = tag_dict[plugin]
        return data
    
class GlobalSettings:  # read only instead of the plugin settings
    def __init__(self) -> None:
        self._path = "ETS2LA/global.json"
        self._settings = {}
        self._load()

    def _load(self):
        with open(self._path, "r") as file:
            self._settings = json.load(file)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        
        if name in self._settings:
            return self._settings[name]
        
        logging.warning(f"Setting '{name}' not found in settings file")
        return None
    
    def __setattr__(self, name: str, value: any) -> None:
        if name in ["_path", "_settings"]:
            self.__dict__[name] = value
        else:
            raise TypeError("Global settings are read-only")
    
class State:
    text: str
    progress: float
    
    timeout: int = -1
    timeout_thread: threading.Thread = None
    last_update: int = 0
    
    state_queue: JoinableQueue
    
    def timeout_thread_func(self):
        while time.time() - self.last_update < self.timeout:
            time.sleep(0.1)
        self.reset()
    
    def __init__(self, state_queue: JoinableQueue):
        self.state_queue = state_queue
        self.text = ""
        self.progress = -1
    
    def __setattr__(self, name, value):
        if name in ["text", "status", "state"]:
            self.last_update = time.time()
            state_dict = {
                "status": value
            }
            self.state_queue.put(state_dict, block=False)
            super().__setattr__("text", value)
            return 
        
        if name in ["value", "progress"]:
            self.last_update = time.time()
            state_dict = {
                "progress": value
            }
            self.state_queue.put(state_dict, block=False)
            super().__setattr__("progress", value)
            return 
        
        if name in ["timeout"]:
            self.last_update = time.time()
            super().__setattr__("timeout", value)
            if self.timeout_thread is None:
                print("Starting timeout thread")
                self.timeout_thread = threading.Thread(target=self.timeout_thread_func, daemon=True)
                self.timeout_thread.start()
            return
        
        super().__setattr__(name, value)
            
    def reset(self):
        self.text = ""
        self.progress = -1
    
class Global:
    settings: GlobalSettings
    """
    You can use this to access the global settings with dot notation.
    
    Example:
    ```python
    # Get Data
    setting_data = self.globals.settings.setting_name
    # Set Data
    self.globals.settings.setting_name = 5
    -> TypeError: Global settings are read only
    ```
    """
    tags: Tags
    """
    You can access the tags by using dot notation.
    
    Example:
    ```python
    # Get Data
    tag_data = self.globals.tags.tag_name
    
    # Set Data
    self.globals.tags.tag_name = 5
    ```
    """
    
    def __init__(self, tags_queue: JoinableQueue, tags_return_queue: JoinableQueue):
        self.settings = GlobalSettings()
        self.tags = Tags(tags_queue, tags_return_queue) 
        
class PluginDescription:
    name: str
    version: str
    description: str
    dependencies: list[str]
    modules: list[str]
    compatible_os: list[Literal["Windows", "Linux"]] = ["Windows", "Linux"]
    compatible_game: list[Literal["ETS2", "ATS"]] = ["ETS2", "ATS"]
    update_log: dict[str, str] = {}
    
    def __init__(self, name: str = "", version: str = "", description: str = "", dependencies: list[str] = [], compatible_os: list[Literal["Windows", "Linux"]] = ["Windows", "Linux"], compatible_game: list[Literal["ETS2", "ATS"]] = ["ETS2", "ATS"], update_log: dict[str, str] ={}, modules: list[str] = []) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies
        self.compatible_os = compatible_os
        self.compatible_game = compatible_game
        self.update_log = update_log
        self.modules = modules