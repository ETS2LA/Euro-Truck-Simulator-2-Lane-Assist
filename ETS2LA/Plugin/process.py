from multiprocessing import Queue
from types import ModuleType

from ETS2LA.Utils.Console.logging import setup_process_logging
from ETS2LA.Controls import ControlEvent
from ETS2LA.UI import ETS2LAPage
from ETS2LA.Plugin import *

import threading
import importlib
import logging
import time
import os

class PluginProcess:
    queue: Queue
    """
    The queue that is connected between this process and
    the backend. This one is for sending messages to the plugin.
    """
    
    return_queue: Queue
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
    last_dictionaries: dict[str, dict] = {}
    """
    Last page dictionaries. This is used to check if the page
    has changed.
    """
    
    controls: list[ControlEvent] = []
    """
    The current plugin's controls. This is populated at init.
    """
    
    description: PluginDescription | None = None
    """
    This plugin's description. Can be accessed without
    first starting up the plugin.
    """
    
    authors: list[Author] = []
    """
    This plugin's authors. Can be accessed without
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
        self.authors = self.file.Plugin.author
        
        # Pages need to be instantiated before use.
        self.pages = self.file.Plugin.pages
        self.pages = [page() for page in self.pages] # type: ignore
        
        # Controls don't need to be instantiated before use.
        # They are instantiated when the plugin is created.
        self.controls = self.file.Plugin.controls
        
        return None
        
    def listener(self) -> None:
        """Send all messages into the stack."""
        while True:
            while self.queue.empty():
                time.sleep(0.01)
            
            try:
                message: PluginMessage = self.queue.get(timeout=1)
            except: time.sleep(0.01); continue
            
            # Handle the message based on the channel
            match message.channel:
                case Channel.GET_DESCRIPTION:
                    Description(self)(message)
                case Channel.ENABLE_PLUGIN | Channel.STOP_PLUGIN | Channel.RESTART_PLUGIN:
                    PluginManagement(self)(message)
                case Channel.GET_TAGS | Channel.UPDATE_TAGS:
                    Tags(self)(message)
                case Channel.CALL_FUNCTION:
                    Function(self)(message)
                case Channel.GET_CONTROLS | Channel.CONTROL_STATE_UPDATE:
                    Controls(self)(message)
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
            
            try: self.plugin.before()
            except: pass
            
            try: self.plugin.run() # type: ignore
            except: logging.exception("Error in plugin process.")
            
            try: self.plugin.after()
            except: pass
        
    def page_updater(self) -> None:
        """Update the pages."""
        while True:
            time.sleep(0.1)
            for page in self.pages:
                try: 
                    dictionary = page.build()
                    url = page.url
                    if url in self.last_dictionaries:
                        if self.last_dictionaries[url] == dictionary:
                            continue
                    
                    self.last_dictionaries[url] = dictionary
                    message = PluginMessage(
                        Channel.UPDATE_PAGE, {
                            "url": url,
                            "data": dictionary
                        }
                    )
                    message.state = State.DONE
                    self.return_queue.put(message, block=True)
                except: 
                    logging.exception("Page build failed.")
        
    def __init__(self, path: str, queue: Queue, return_queue: Queue) -> None:
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
        
        message = PluginMessage(
            Channel.SUCCESS, {}
        )
        message.state = State.DONE
        self.return_queue.put(message)
        
        threading.Thread(
            target=self.listener,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.tag_updater,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.page_updater,
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
            message.data = [self.plugin.description, self.plugin.authors]
            message.state = State.DONE
            self.plugin.return_queue.put(message)
        except:
            message.state = State.ERROR
            message.data = "Error getting plugin description"
            logging.exception("Error getting plugin description")
            self.plugin.return_queue.put(message)
            
class Controls(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.state == State.ERROR:
                logging.error("Error getting controls, " + message.data)
                return None
            
            if message.channel == Channel.GET_CONTROLS:
                message.data = self.plugin.controls
                message.state = State.DONE
                self.plugin.return_queue.put(message)
                return None
                
            if message.channel == Channel.CONTROL_STATE_UPDATE:
                controls = message.data
                if self.plugin.plugin is None:
                    return
                
                for event in self.plugin.controls:
                    if event.alias in controls:
                        event.update(controls[event.alias])
            
        except Exception as e:
            logging.exception("Error handling controls")
            
class PluginManagement(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.channel == Channel.ENABLE_PLUGIN:
                if self.plugin.plugin is not None:
                    message.state = State.ERROR
                    message.data = "Plugin is already enabled"
                    self.plugin.return_queue.put(message)
                    return
                
                try:
                    self.plugin.plugin = self.plugin.file.Plugin( # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,  
                        self.plugin.get_tag,
                        self.plugin.set_tag  
                    )
                    
                    for page in self.plugin.pages:
                        page.plugin = self.plugin.plugin
                        page.settings = self.plugin.plugin.settings

                    message.state = State.DONE
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error enabling plugin")
                    
            elif message.channel == Channel.STOP_PLUGIN:
                try:
                    del self.plugin.plugin
                    self.plugin.plugin = None
                    message.state = State.DONE
                    
                    for page in self.plugin.pages:
                        page.plugin = None
                        page.settings = None
                    
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error stopping plugin")
                    
            elif message.channel == Channel.RESTART_PLUGIN:
                try:
                    del self.plugin.plugin
                    self.plugin.plugin = None
                    self.plugin.update_plugin()
                    self.plugin.plugin = self.plugin.file.Plugin( # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,  
                        self.plugin.get_tag,
                        self.plugin.set_tag      
                    )
                    
                    for page in self.plugin.pages:
                        page.plugin = self.plugin
                        page.settings = self.plugin.settings
                    
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
            
class Function(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.state == State.ERROR:
                logging.error("Error getting function, " + message.data)
                return None

            data = message.data
            func = data.get("function")
            args = data.get("args")
            kwargs = data.get("kwargs")
            
            # Fix problem with args and kwargs
            if "args" in kwargs:
                args = kwargs["args"]
                del kwargs["args"]
            
            # Extract the function
            function = func.split(".")[-1]
            object = func.split(".")[-2]
            
            if object == "Plugin":
                function = getattr(self.plugin.plugin, function)
            else:
                # Find the page
                page = None
                for p in self.plugin.pages:
                    # Get the page object name (ie. Settings, Page, etc.)
                    page_object = p.__class__.__name__
                    if page_object == object:
                        page = p
                        break
                    
                if page is None:
                    logging.error(f"Page {object} not found on plugin {self.plugin.path}")
                    return None
                
                function = getattr(page, function)
            
            try:
                if args and kwargs:
                    function(*args, **kwargs)
                elif args:
                    function(*args)
                elif kwargs:
                    function(**kwargs)
                else:
                    function()
            except Exception as e:
                logging.exception("Error calling function")

        except Exception as e:
            logging.exception("Error handling function")