from settings import Settings
from author import Author

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
    
    author: Author
    information: PluginDescription = PluginDescription()
    
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
    
    def __new__(cls, path: str) -> None:
        instance = super().__new__(cls)
        instance.path = path
        instance.settings = Settings(path)
        instance.ensure_settings_file()
        return instance
    
    def __init__(self, *args) -> None:
        self.ensure_functions()
        while True:
            try:
                self.before()
            except Exception as e:
                print(e)
    
    def before(self) -> None:
        data = self.run()
        self.after(data)
        
    def after(self, data) -> None:
        ...
            
class TestClass(ETS2LAPlugin):
    def run(self) -> any:
        print("Hello")
        
test = TestClass("cache")
test.before()