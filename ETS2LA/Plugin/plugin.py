from ETS2LA.Plugin.settings import Settings
from ETS2LA.Plugin.author import Author

from multiprocessing import JoinableQueue
from typing import Literal
import json
import os

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


class ETS2LAPlugin(object):
    settings: Settings
    path: str
    
    information: PluginDescription = PluginDescription()
    author: Author
    
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
            raise TypeError("'plugin' is a reserved function name")
        if "run" not in dir(type(self)):
            raise TypeError("Your plugin has to have a 'run' function.")
        if type(self).__name__ != "Plugin":
            raise TypeError("Please make sure the class is named 'Plugin'")
    
    def __new__(cls, path: str, return_queue: JoinableQueue) -> None:
        instance = super().__new__(cls)
        instance.path = path
        instance.return_queue = return_queue
        instance.ensure_settings_file()
        instance.settings = Settings(path)
        return instance
    
    def __init__(self, *args) -> None:
        self.ensure_functions()
        try:
            self.imports()
        except: pass
    
    def plugin(self) -> None:
        self.before()
        data = self.run()
        self.after(data)
            
    def before(self) -> None:
        ...
        
    def after(self, data) -> None:
        ...