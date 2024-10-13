from ETS2LA.Plugin import *
import multiprocessing
import importlib
import threading
import inspect
import os

plugin_path = "plugins"
plugin_target_class = "Plugin"

AVAILABLE_PLUGINS = []
RUNNING_PLUGINS = []

class PluginHandler:
    def __init__(self, plugin_name: str, plugin_description: PluginDescription):
        self.plugin_name = plugin_name
        self.plugin_description = plugin_description
        self.return_queue = multiprocessing.Queue()
        self.plugin = multiprocessing.Process(target=__import__(f"{plugin_path}.{plugin_name}.main").Plugin, args=(f"{plugin_path}/{plugin_name}", self.return_queue,))

def get_plugin_class(module_name):
    module = __import__(module_name, fromlist=['*'])
    for name, cls in inspect.getmembers(module):
        if inspect.isclass(cls) and issubclass(cls, ETS2LAPlugin) and cls != ETS2LAPlugin:
            return cls
    return None

def find_plugins() -> list[tuple[str, PluginDescription, Author]]:
    folders = os.listdir(plugin_path)
    plugins = []
    for folder in folders:
        if "main.py" in os.listdir(f"{plugin_path}/{folder}"):
            plugin_class = get_plugin_class(f"{plugin_path}.{folder}.main")
            if plugin_class is not None:
                information = getattr(plugin_class, "information", None)
                author = getattr(plugin_class, "author", None)
                plugins.append((folder, information, author))
            del plugin_class
            
    return plugins

def run():
    global AVAILABLE_PLUGINS
    AVAILABLE_PLUGINS = find_plugins()