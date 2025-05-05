from ETS2LA.Plugin.process import PluginProcess, PluginDescription, PluginMessage
from ETS2LA.Plugin.message import Channel

import multiprocessing
import threading

import logging
import time
import os

search_folders: list[str] = [
    "Plugins"
]

# Discover all plugins in the search folders.
plugin_folders: list[str] = []
def discover_plugins() -> None:
    global plugin_folders
    plugin_folders = []
    
    for folder in search_folders:
        for root, dirs, files in os.walk(folder):
            if "main.py" in files:
                plugin_folders.append(root)
                

class Plugin:
    process: multiprocessing.Process
    """The physical running process of the plugin."""
    
    queue: multiprocessing.JoinableQueue
    """The queue used to send messages to the plugin."""
    
    return_queue: multiprocessing.JoinableQueue
    """The queue used to send messages back to the backend."""
    
    stack: dict[int, PluginMessage] = {}
    """All the messages that have arrived from the plugin."""
    
    description: PluginDescription
    """The description of the plugin."""
    
    def listener(self):
        """Send all messages into the stack."""
        while True:
            try: message: PluginMessage = self.return_queue.get(timeout=1)
            except: time.sleep(0.01); continue
            self.stack[message.id] = message
    
    def wait_for_id(self, id: int) -> PluginMessage:
        """Wait for a message with the given ID."""
        while id not in self.stack:
            time.sleep(0.01)
            
        message = self.stack.pop(id)
        return message
    
    def get_description(self) -> PluginDescription:
        """Get the plugin description from the plugin process."""
        message = PluginMessage(
            Channel.GET_DESCRIPTION, {}
        )
        self.queue.put(message)
        response: PluginMessage = self.wait_for_id(message.id)
        logging.info(f"Plugin {self.description.name} description: {response.data}")
        return response.data
    
    def __init__(self, folder: str) -> None:
        self.queue = multiprocessing.JoinableQueue()
        self.return_queue = multiprocessing.JoinableQueue()
        self.process = multiprocessing.Process(
            target=PluginProcess,
            args=(folder, self.queue, self.return_queue)
        )
        self.process.start()
        
        # Start to listen for messages from the plugin.
        threading.Thread(
            target=self.listener,
            daemon=True
        ).start()
        
        message = self.wait_for_id(1)
        if message.channel != Channel.SUCCESS:
            logging.error(f"Plugin {folder} failed to start: {message.data}")
            raise Exception("PluginProcess: Plugin failed to start.")
        
        print(f"Plugin {folder} started successfully.")
        self.get_description()
        
        
plugins: list[Plugin] = []
def create_processes() -> None:
    for folder in plugin_folders:
        logging.debug(f"Creating plugin process for {folder}")
        plugin = Plugin(folder)
        plugins.append(plugin)
    logging.info(f"Loaded {len(plugins)} plugins.")
  

def run() -> None:
    discover_plugins()
    threading.Thread(target=create_processes, daemon=True).start()