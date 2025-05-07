from multiprocessing import JoinableQueue
from types import ModuleType

from ETS2LA.Utils.Console.logging import setup_process_logging
from ETS2LA.UI import ETS2LAPage
from ETS2LA.Plugin import *

import threading
import importlib
import logging
import time
import os

class PluginProcess:
    queue: JoinableQueue
    """
    The queue that is connected between this process and
    the backend. This one is for sending messages to the plugin.
    """
    
    return_queue: JoinableQueue
    """
    The queue that is connected between this process and
    the backend. This one is for sending messages to the backend.
    """
    
    stack: dict[int, PluginMessage] = {}
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
    If the plugin instance is not running, this will be set to None.
    """
    
    file: ModuleType | None = None
    """
    The imported file of the plugin.
    """
    
    path: str = ""
    """
    The relative path of the files belonging to this process.
    """
    
    output_needs_update: bool = False
    pending_output_update: bool = False
    output_tags: dict = {}
    """
    Output tags are tags that this plugin wants to send to others.
    """
    
    input_tags_that_need_update: list[str] = []
    pending_input_update: bool = False
    input_tags: dict = {}
    """
    Input tags are tags that this plugin wants to get from others.
    """
    
    def get_tag(self, name: str) -> dict:
        """
        Get the tags from the plugin. This is used to get the
        tags from the plugin and send them to the backend.
        """
        if name not in self.input_tags_that_need_update:
            self.input_tags_that_need_update.append(name)
            
        if name not in self.input_tags:
            self.input_tags[name] = None
            
        return self.input_tags[name]
    
    def set_tag(self, name: str, value) -> None:
        """
        Set a tag in the plugin. This is used to set a tag
        in the plugin and send it to the backend.
        """
        self.output_tags[name] = value
        self.output_needs_update = True
        return None
    
    def update_plugin(self) -> None:
        logging.info(f"Importing plugin file from {self.path}")
        import_path = self.path.replace("\\", ".").replace("/", ".") + ".main"
        
        try:
            self.file = importlib.import_module(import_path)
        except ImportError as e:
            self.return_queue.put(PluginMessage(
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
        
    def listener(self) -> None:
        """Send all messages into the stack."""
        while True:
            try: message: PluginMessage = self.queue.get(timeout=1)
            except: time.sleep(0.01); continue
            # Handle the message based on the channel
            match message.channel:
                case Channel.GET_DESCRIPTION:
                    Description(self)(message)
                case Channel.ENABLE_PLUGIN | Channel.STOP_PLUGIN | Channel.RESTART_PLUGIN:
                    PluginManagement(self)(message)
                case Channel.GET_TAGS | Channel.UPDATE_TAGS:
                    Tags(self)(message)
                case _:
                    self.stack[message.id] = message
        
    def wait_for_id(self, id: int) -> PluginMessage:
        """Wait for a message with the given ID."""
        while id not in self.stack:
            time.sleep(0.01)
            
        message = self.stack.pop(id)
        return message
    
    def tag_updater(self) -> None:
        while True:
            if self.input_tags_that_need_update and not self.pending_input_update:
                self.pending_input_update = True
                message = PluginMessage(
                    Channel.GET_TAGS, {
                        "tags": self.input_tags_that_need_update
                    }
                )
                
                self.input_tags_that_need_update = []
                self.return_queue.put(message, block=False)
                
            if self.output_needs_update and not self.pending_output_update:
                self.pending_output_update = True
                message = PluginMessage(
                    Channel.UPDATE_TAGS, self.output_tags
                )
                
                self.output_needs_update = False
                self.return_queue.put(message, block=False)
                
            time.sleep(0.01)
    
    def keep_alive(self) -> None:
        """Keep the process alive."""
        while True:
            if not self.plugin:
                time.sleep(1)
                continue
            
            self.plugin.before()
            
            try:
                data = self.plugin.run() # type: ignore
            except:
                logging.exception("Error in plugin process.")
            
            self.plugin.after()
        
    def __init__(self, path: str, queue: JoinableQueue, return_queue: JoinableQueue) -> None:
        self.queue = queue
        self.return_queue = return_queue
        
        name = os.path.basename(path)
        setup_process_logging(
            name, 
            console_level=logging.WARNING,
            filepath=os.path.join(os.getcwd(), "logs", f"{name}.log")
        )
        
        files = os.listdir(path)
        if "main.py" not in files:
            self.return_queue.put(PluginMessage(
                Channel.CRASHED, {
                    "message": "No main.py found in the plugin directory."
                }
            ))
            raise Exception("PluginProcess: No main.py found in the plugin directory.")
        
        self.path = path
        self.update_plugin()
        
        self.return_queue.put(PluginMessage(
            Channel.SUCCESS, {}
        ))
        
        threading.Thread(
            target=self.listener,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.tag_updater,
            daemon=True
        ).start()
        
        self.keep_alive()
        
        
        
# MARK: Handlers
class ChannelHandler:
    """
    A handler for a specific channel. These are
    used by the plugin process to respond to backend
    messages.
    """
    
    plugin: PluginProcess
    
    def __init__(self, plugin: PluginProcess):
        self.plugin = plugin
        
    def __call__(self, message: PluginMessage):
        """
        Handle a message from the plugin process.
        This function is called by the plugin process
        when a message is received.
        """
        pass

class Description(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            message.data = self.plugin.description
            message.state = State.DONE
            self.plugin.return_queue.put(message)
        except:
            message.state = State.ERROR
            message.data = "Error getting plugin description"
            logging.exception("Error getting plugin description")
            self.plugin.return_queue.put(message)
            
class PluginManagement(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.channel == Channel.ENABLE_PLUGIN:
                try:
                    self.plugin.plugin = self.plugin.file.Plugin( # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,  
                        self.plugin.get_tag,
                        self.plugin.set_tag  
                    )
                    message.state = State.DONE
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error enabling plugin")
                    
            elif message.channel == Channel.STOP_PLUGIN:
                try:
                    self.plugin.plugin = None
                    message.state = State.DONE
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error stopping plugin")
                    
            elif message.channel == Channel.RESTART_PLUGIN:
                try:
                    self.plugin.plugin = None
                    self.plugin.update_plugin()
                    self.plugin.plugin = self.plugin.file.Plugin( # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,    
                    )
                    message.state = State.DONE
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error restarting plugin")
                    
            else:
                message.state = State.ERROR
                message.data = "Invalid channel"
                
            self.plugin.return_queue.put(message)
        except Exception as e:
            message.state = State.ERROR
            message.data = e.args
            logging.exception("Error handling plugin state")
            self.plugin.return_queue.put(message)
            
class Tags(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.state == State.ERROR:
                logging.error("Error getting tags, " + message.data)
                return None
            
            if message.channel == Channel.GET_TAGS:
                for tag, value in message.data.items():
                    self.plugin.input_tags[tag] = value
                    
                self.plugin.pending_input_update = False
                    
            if message.channel == Channel.UPDATE_TAGS:
                self.plugin.pending_output_update = False
            
        except Exception as e:
            logging.exception("Error handling tags")