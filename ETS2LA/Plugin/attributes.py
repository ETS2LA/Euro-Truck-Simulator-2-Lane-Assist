from multiprocessing import JoinableQueue
from typing import Literal
import logging
import json

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
    compatible_os: list[Literal["Windows", "Linux"]] = ["Windows", "Linux"]
    compatible_game: list[Literal["ETS2", "ATS"]] = ["ETS2", "ATS"]
    update_log: dict[str, str] = {}
    
    def __init__(self, name: str = "", version: str = "", description: str = "", dependencies: list[str] = [], compatible_os: list[Literal["Windows", "Linux"]] = ["Windows", "Linux"], compatible_game: list[Literal["ETS2", "ATS"]] = ["ETS2", "ATS"], update_log: dict[str, str] ={}) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies
        self.compatible_os = compatible_os
        self.compatible_game = compatible_game
        self.update_log = update_log