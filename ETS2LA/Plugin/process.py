from multiprocessing import JoinableQueue
from types import ModuleType

from ETS2LA.Utils.Console.logging import setup_process_logging
from ETS2LA.UI import ETS2LAPage
from ETS2LA.Plugin import *

import importlib
import logging
import os

class PluginProcess:
    queue: JoinableQueue
    """
    The queue that is connected between this process and
    the backend.
    """
    
    stack: list[PluginMessage] = []
    """
    The current stack of messages to process.
    """
    
    pages: list[ETS2LAPage] = []
    """
    The current plugin's pages. This is populated at init.
    """
    
    description: PluginDescription | None = None
    """
    This plugin's description. Can be accessed without
    first starting up the plugin.
    """
    
    plugin: ETS2LAPlugin | None = None
    """
    The ETS2LAPlugin instance of this plugin process.
    If the plugin instance is not runnin, this will be set to None.
    """
    
    file: ModuleType | None = None
    """
    The imported file of the plugin.
    """
    
    path: str = ""
    """
    The relative path of the files belonging to this process.
    """
    
    
    def update_plugin(self) -> None:
        logging.info(f"Importing plugin file from {self.path}")
        import_path = self.path.replace("\\", ".").replace("/", ".") + ".main"
        
        try:
            self.file = importlib.import_module(import_path)
        except ImportError as e:
            self.queue.put(PluginMessage(
                Channel.CRASHED, {
                    "message": f"Error importing plugin file: {e}"
                }
            ))
            logging.error(f"Error importing plugin file: {e}")
            raise ImportError(f"Error importing plugin file: {e}")
        
        logging.info(f"Plugin file imported successfully: {self.file}")
        self.description = self.file.Plugin.description
        
        # Pages need to be instantiated before use.
        self.pages = self.file.Plugin.pages
        self.pages = [page() for page in self.pages] # type: ignore
        
        return None
        
        
    def __init__(self, path: str, queue: JoinableQueue) -> None:
        self.queue = queue
        
        name = os.path.basename(path)
        setup_process_logging(
            name, 
            console_level=logging.WARNING,
            filepath=os.path.join(os.getcwd(), "logs", f"{name}.log")
        )
        
        files = os.listdir(path)
        if "main.py" not in files:
            self.queue.put(PluginMessage(
                Channel.CRASHED, {
                    "message": "No main.py found in the plugin directory."
                }
            ))
            raise Exception("PluginProcess: No main.py found in the plugin directory.")
        
        self.path = path
        self.update_plugin()
        
        self.queue.put(PluginMessage(
            Channel.SUCCESS, {}
        ))