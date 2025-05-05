from ETS2LA.Plugin.process import PluginProcess, PluginDescription, PluginMessage
from ETS2LA.Plugin.message import Channel, State

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
    
    stack: dict[Channel, dict[int, PluginMessage]] = {}
    """All the messages that have arrived from the plugin."""
    
    description: PluginDescription
    """The description of the plugin."""
    
    folder: str
    """Where the plugin is located."""
    
    def listener(self):
        """Send all messages into the stack."""
        while True:
            try: message: PluginMessage = self.return_queue.get(timeout=1)
            except: time.sleep(0.01); continue
            if message.channel not in self.stack:
                self.stack[message.channel] = {}
            self.stack[message.channel][message.id] = message
    
    def wait_for_channel_message(self, channel: Channel, id: int, timeout: float = -1) -> PluginMessage | None:
        """Wait for a message with the given ID."""
        start_time = time.perf_counter()
        end_time = start_time + timeout if timeout > 0 else -1
        while channel not in self.stack:
            time.sleep(0.01)
            if end_time > 0 and time.perf_counter() > end_time:
                return None
        while id not in self.stack[channel]:
            time.sleep(0.01)
            if end_time > 0 and time.perf_counter() > end_time:
                return None
            
        message = self.stack[channel].pop(id)
        return message
    
    def get_description(self) -> PluginDescription:
        """Get the plugin description from the plugin process."""
        message = PluginMessage(
            Channel.GET_DESCRIPTION, {}
        )
        self.queue.put(message)
        response = self.wait_for_channel_message(message.channel, message.id, timeout=5)
        if response is None:
            logging.error(f"Plugin {self.folder} failed to get description: Timeout.")
            plugins.remove(self)
            quit(1)
        if response.state == State.ERROR:
            logging.error(f"Plugin {self.folder} failed to get description: {response.data}")
            plugins.remove(self)
            quit(1)
        
        self.description = response.data
        logging.info(f"Plugin {self.description.name} loaded successfully.")
        return response.data
    
    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.queue = multiprocessing.JoinableQueue()
        self.return_queue = multiprocessing.JoinableQueue()
        self.process = multiprocessing.Process(
            target=PluginProcess,
            args=(self.folder, self.queue, self.return_queue),
            daemon=True
        )
        self.process.start()
        
        # Start to listen for messages from the plugin.
        threading.Thread(
            target=self.listener,
            daemon=True
        ).start()
        
        message = self.wait_for_channel_message(Channel.SUCCESS, 1)
        if message.data != {}:
            plugins.remove(self)
            logging.error(f"Plugin {folder} failed to start: {message.data}")
            raise Exception("PluginProcess: Plugin failed to start.")
        
        plugins.append(self)
        self.get_description()
        
plugins: list[Plugin] = []
def create_processes() -> None:
    for folder in plugin_folders:
        logging.debug(f"Creating plugin process for {folder}")
        threading.Thread(target=Plugin, args=(folder,), daemon=True).start()
        time.sleep(2)

    logging.info(f"Loaded {len(plugins)} plugins.")
  
def run() -> None:
    discover_plugins()
    threading.Thread(target=create_processes, daemon=True).start()