from ETS2LA.Plugin.attributes import Global, Plugins, PluginDescription
from ETS2LA.Plugin.settings import Settings
from ETS2LA.Plugin.author import Author

from ETS2LA.utils.logging import SetupProcessLogging
from multiprocessing import JoinableQueue
import importlib
import logging
import json
import time
import sys
import os

class ETS2LAPlugin(object):
    """
    This is the main plugin object, you will see a list of attributes below.
    
    :param int fps_cap: The maximum frames per second the plugin will run at.
    :param Description description: The description of the plugin.
    :param Author author: The author of the plugin.
    :param Global globals: The global settings and tags.
    :param Settings settings: The settings of the plugin.
    :param Plugins plugins: Interactions with other plugins.
    """
    path: str

    fps_cap: int = 30
    
    description: PluginDescription = PluginDescription()
    author: Author
    
    return_queue: JoinableQueue
    plugins_queue: JoinableQueue
    plugins_return_queue: JoinableQueue
    
    globals: Global
    """
    Global class for the plugin to access global settings and
    
    :param GlobalSettings settings: Access to the global settings.
    :param Tags tags: Access to the global tags.
    """
    settings: Settings
    plugins: Plugins
    
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
        if "imports" not in dir(type(self)):
            raise TypeError("Your plugin has to have an 'imports' function.")
        if type(self).__name__ != "Plugin":
            raise TypeError("Please make sure the class is named 'Plugin'")
    
    def __new__(cls, path: str, return_queue: JoinableQueue, 
                                plugins_queue: JoinableQueue, plugins_return_queue: JoinableQueue, 
                                tags_queue: JoinableQueue, tags_return_queue: JoinableQueue
                                ) -> object:
        instance = super().__new__(cls)
        instance.path = path
        instance.return_queue = return_queue
        instance.plugins_queue = plugins_queue
        instance.plugins_return_queue = plugins_return_queue
        instance.plugins = Plugins(plugins_queue, plugins_return_queue)
        instance.globals = Global(tags_queue, tags_return_queue)
        instance.ensure_settings_file()
        instance.settings = Settings(path)
        return instance
    
    def __init__(self, *args) -> None:
        self.ensure_functions()
        self.imports()

        while True:
            self.plugin()
    
    def plugin(self) -> None:
        self.before()
        data = self.run()
        self.after(data)
            
    def before(self) -> None:
        self.start_time = time.time()
        
    def after(self, data) -> None:
        if data is not None:
            self.return_queue.put(data, block=True)

        self.end_time = time.time()
        time_to_sleep = max(1/self.fps_cap - (self.end_time - self.start_time), 0)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

class PluginRunner:
    def __init__(self, plugin_name: str, plugin_description: PluginDescription, 
                    return_queue: JoinableQueue, 
                    plugins_queue: JoinableQueue, plugins_return_queue: JoinableQueue,
                    tags_queue: JoinableQueue, tags_return_queue: JoinableQueue
                    ):
        
        SetupProcessLogging(
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

        sys.path.append(os.path.join(os.getcwd(), "plugins", plugin_name))

        # Import the plugin module
        plugin_module = importlib.import_module(f"plugins.{plugin_name}.main")

        # Instantiate the Plugin class
        if hasattr(plugin_module, 'Plugin'):
            self.plugin_instance = plugin_module.Plugin(f"plugins/{plugin_name}", return_queue, 
                                                            plugins_queue, plugins_return_queue, 
                                                            tags_queue, tags_return_queue)
        else:
            raise ImportError(f"No class 'Plugin' found in module 'plugins.{plugin_name}.main'")