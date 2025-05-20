from ETS2LA.Plugin.process import PluginProcess, PluginDescription, PluginMessage, Author
from ETS2LA.Plugin.message import Channel, State
from ETS2LA.Utils.translator import Translate

import multiprocessing
import threading

import logging
import time
import os

if os.name == "nt":
    import ctypes

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

# MARK: Class
class Plugin:
    process: multiprocessing.Process
    """The physical running process of the plugin."""
    
    queue: multiprocessing.Queue
    """The queue used to send messages to the plugin."""
    
    return_queue: multiprocessing.Queue
    """The queue used to send messages back to the backend."""
    
    stack: dict[Channel, dict[int, PluginMessage]]
    """All the messages that have arrived from the plugin."""
    
    description: PluginDescription
    """The description of the plugin."""
    
    authors: list[Author]
    """All authors of the plugin."""
    
    folder: str
    """Where the plugin is located."""
    
    stop: bool
    """Whether the plugin should stop or not."""
    
    running: bool
    """Whether the plugin is running or not."""
    
    tags: dict = {}
    """All plugins share this same tags dictionary. This way they can easily share tag data."""
    
    state: dict
    """The current plugin state used by the frontend."""
    
    pages: dict = {}
    """All plugins share the same pages dictionary. This way they can easily share page data."""
    
    def start_plugin(self) -> None:
        # First initialize / reset the variables
        self.stack = {}
        self.state = {
            "status": "",
            "progress": -1
        }
        self.stop = False
        self.running = False
        
        self.queue = multiprocessing.Queue()
        self.return_queue = multiprocessing.Queue()
        
        # Then kill and start the new process
        if "process" in self.__dict__ and self.process.is_alive():
            self.process.kill()
            self.process.join()
            self.process.close()
            self.process = None # type: ignore
            
        self.process = multiprocessing.Process(
            target=PluginProcess,
            args=(self.folder, self.queue, self.return_queue),
            daemon=True,
            name=f"Plugin {self.folder.split('/')[-1]} Process",
        )
        
        self.process.start()
        
    
    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.start_plugin()
        
        # Start to listen for messages from the plugin.
        threading.Thread(
            target=self.listener,
            daemon=True
        ).start()
        
        message = self.wait_for_channel_message(Channel.SUCCESS, 1, timeout=30)
        if message is None:
            logging.error(f"Plugin {folder} failed to start: Timeout.")
            self.stop = True
            quit(1)
        
        if message.data != {}:
            logging.error(f"Plugin {folder} failed to start: {message.data}")
            self.stop = True
            quit(1)
        
        plugins.append(self)
        self.get_description()
        
        threading.Thread(
            target=self.tag_handler,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.state_handler,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.page_handler,
            daemon=True
        ).start()

        self.keep_alive()
        

    def keep_alive(self) -> None:
        """Keep the process alive."""
        logging.debug(f"Plugin [yellow]{Translate(self.description.name, return_original=True)}[/yellow] loaded successfully.")
        while not self.stop:
            time.sleep(1)
    
    def listener(self):
        """Send all messages into the stack."""
        while True:
            try: message: PluginMessage = self.return_queue.get(timeout=1)
            except: time.sleep(0.01); continue
            
            if message.channel == Channel.STOP_PLUGIN:
                threading.Thread(
                    target=stop_plugin,
                    kwargs={
                        "description": self.description
                    }
                ).start()
                continue
            
            if message.channel not in self.stack:
                self.stack[message.channel] = {}
            self.stack[message.channel][message.id] = message
    
    def tag_handler(self):
        while True:            
            if Channel.GET_TAGS in self.stack:
                while self.stack[Channel.GET_TAGS]:
                    message = self.stack[Channel.GET_TAGS].popitem()[1]
                    
                    tags = message.data["tags"]
                    response = {}
                    for tag in tags:
                        response[tag] = self.tags.get(tag, None)
                    
                    message.state = State.DONE
                    message.data = response
                    self.queue.put(message)
            
            if Channel.UPDATE_TAGS in self.stack:
                while self.stack[Channel.UPDATE_TAGS]:
                    message = self.stack[Channel.UPDATE_TAGS].popitem()[1]
                    data = message.data
                    
                    for tag, value in data.items():
                        if tag not in self.tags:
                            self.tags[tag] = {}
                            
                        if self.description.name not in self.tags[tag]:
                            self.tags[tag][self.description.name] = {}
                            
                        self.tags[tag][self.description.name] = value
                    
                    message.state = State.DONE
                    message.data = "success" # clear data for faster transmit
                    self.queue.put(message)
            
            time.sleep(0.01)
    
    def state_handler(self):
        while True:
            if Channel.STATE_UPDATE in self.stack:
                while self.stack[Channel.STATE_UPDATE]:
                    message = self.stack[Channel.STATE_UPDATE].popitem()[1]
                    if "progress" in message.data:
                        self.state["progress"] = message.data["progress"]
                    if "status" in message.data:
                        self.state["status"] = message.data["status"]
            
            time.sleep(0.01)
            
    def page_handler(self):
        while True:
            if Channel.UPDATE_PAGE in self.stack:
                while self.stack[Channel.UPDATE_PAGE]:
                    message = self.stack[Channel.UPDATE_PAGE].popitem()[1]
                    if "url" in message.data:
                        url = message.data["url"]
                        self.pages[url] = message.data["data"]

            time.sleep(0.01)
    
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
            self.stop = True
            plugins.remove(self)
            quit(1)
        if response.state == State.ERROR:
            logging.error(f"Plugin {self.folder} failed to get description: {response.data}")
            plugins.remove(self)
            self.stop = True
            quit(1)
            
        self.description, self.authors = response.data
        return response.data
  
  

# MARK: Startup      
plugins: list[Plugin] = []
def create_processes() -> None:
    for folder in plugin_folders:
        logging.debug(f"Creating plugin process for {folder}")
        threading.Thread(target=Plugin, name=f"Backend for {folder.split('/')[-1]}",
                         args=(folder,), daemon=True).start()

    time.sleep(10)
    logging.info(f"Loaded {len(plugins)} plugins.")
  
def run() -> None:
    discover_plugins()
    threading.Thread(target=create_processes, daemon=True).start()
    
    
    
    
# MARK: Plugin Matching
def match_plugin_by_description(description: PluginDescription) -> Plugin | None:
    """Match a plugin by its description."""
    for plugin in plugins:
        if plugin.description == description:
            return plugin
    return None
    
def match_plugin_by_name(name: str) -> Plugin | None:
    """Match a plugin by its name."""
    for plugin in plugins:
        if plugin.description.name == name:
            return plugin
    return None

def match_plugin_by_folder(folder: str) -> Plugin | None:
    """Match a plugin by its folder."""
    for plugin in plugins:
        if plugin.folder == folder:
            return plugin
    return None
    
def match_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None) -> Plugin | None:
    """Match a plugin by its description, name or folder."""
    if description is not None:
        return match_plugin_by_description(description)
    if name is not None:
        return match_plugin_by_name(name)
    if folder is not None:
        return match_plugin_by_folder(folder)
    
    return None
    
    
    
    
# MARK: Enable/Disable
def start_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None) -> bool:
    """Start a plugin based on one of the parameters."""
    plugin: Plugin | None = match_plugin(
        description=description,
        name=name,
        folder=folder
    )
    if not plugin:
        logging.error(f"Plugin not found.")
        return False
    
    logging.info(f"Starting plugin [yellow]{Translate(plugin.description.name, return_original=True)}[/yellow]")
    if plugin.process.is_alive():
        message = PluginMessage(
            Channel.ENABLE_PLUGIN, {}
        )
        plugin.queue.put(message)
        response = plugin.wait_for_channel_message(message.channel, message.id, timeout=30)
        if response and response.state == State.DONE:
            plugin.running = True
            logging.info(f"Plugin [yellow]{Translate(plugin.description.name, return_original=True)}[/yellow] started successfully.")
            return True
        else:
            plugin.running = False
            logging.error(f"Failed to start plugin: {response.data if response else 'Timeout'}")
            return False
        
    return False

def stop_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None) -> bool:
    """Stop a plugin based on one of the parameters."""
    plugin: Plugin | None = match_plugin(
        description=description,
        name=name,
        folder=folder
    )
    if not plugin:
        logging.error(f"Plugin not found.")
        return False
    
    logging.info(f"Stopping plugin [yellow]{Translate(plugin.description.name, return_original=True)}[/yellow]")
    plugin.start_plugin()
    response = plugin.wait_for_channel_message(Channel.SUCCESS, 1, timeout=30)
    plugin.running = False
    if response and response.state == State.DONE:
        logging.info(f"Plugin [yellow]{Translate(plugin.description.name, return_original=True)}[/yellow] stopped successfully.")
        return True
    else:
        logging.error(f"Failed to stop plugin: {response.data if response else 'Timeout'}")
        return False
        
    return False

def restart_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None) -> bool:
    """Restart a plugin based on one of the parameters."""
    try:
        stop_plugin(
            description=description,
            name=name,
            folder=folder
        )
        start_plugin(
            description=description,
            name=name,
            folder=folder
        )
        return True
    except Exception as e:
        logging.error(f"Failed to restart plugin: {e}")
        return False



# MARK: Pages
def get_page_data(url: str) -> dict:
    """Get the page data from all plugins."""
    for plugin in plugins:
        if url in plugin.pages:
            return plugin.pages[url]
    return {}

def get_page_list() -> dict[str, dict]:
    """Get the list of all pages from all plugins."""
    pages = {}
    for plugin in plugins:
        for url, data in plugin.pages.items():
            if url not in pages:
                pages[url] = data[0] # metadata
                
    return pages



# MARK: General Utils
def get_tag_data(tag: str) -> dict:
    """Get the tag data from all plugins."""
    
    # We only need the tags dict from the first plugin as they 
    # all share the same pointer.
    if not plugins:
        return {}
    
    plugin = plugins[0]
    return plugin.tags.get(tag, {})

def get_states() -> dict:
    """Get the state data from all plugins."""
    states = {}
    for plugin in plugins:
        if plugin.state["status"] != "":
            states[Translate(plugin.description.name, return_original=True)] = plugin.state
        
    return states