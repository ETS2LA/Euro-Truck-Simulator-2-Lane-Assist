from multiprocessing import Queue
from types import ModuleType

from ETS2LA.Utils.Console.logging import setup_process_logging
from ETS2LA.Controls import ControlEvent
from ETS2LA.Settings import GlobalSettings
from ETS2LA.Events import Event, events
from ETS2LA.UI import ETS2LAPage
from ETS2LA.Plugin import (
    PluginMessage,
    Channel,
    State,
    ETS2LAPlugin,
    PluginDescription,
    Author,
)

from memory import SharedMemorySender, SharedMemoryReceiver
import threading
import importlib
import logging
import psutil
import time
import os

settings = GlobalSettings()


class PerformanceEntry:
    timestamp: float
    frametime: float

    def __init__(self, timestamp: float, frametime: float):
        self.timestamp = timestamp
        self.frametime = frametime


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

    sender: SharedMemorySender
    """
    Shared memory sender for large data.
    Only used for tags.
    """

    receiver: SharedMemoryReceiver
    """
    Shared memory receiver for large data.
    Only used for tags.
    """

    stack: dict[int, PluginMessage] = {}
    """
    The current stack of messages to process.
    """

    main_thread_stack: list[PluginMessage] = []
    """
    The main thread stack of messages to process.
    This is used for operations that should be completed on the main thread,
    such as starting or stopping the plugin.
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

    performance: list[PerformanceEntry] = []
    """
    Performance entries for this plugin. This is used to
    track the performance of the plugin.
    """

    mem_needs_update: bool = False
    pending_mem_out_update: bool = False
    last_mem_output_time: int = 0
    mem_output: dict = {}
    """
    Memory tag output.
    """

    output_needs_update: bool = False
    pending_output_update: bool = False
    last_output_time: int = 0
    output_tags: dict = {}
    """
    Output tags are tags that this plugin wants to send to others.
    """

    mem_tags_that_need_update: list[str] = []
    pending_mem_update: bool = False
    """
    Memory tags that need to be updated.
    """

    input_tags_that_need_update: list[str] = []
    pending_input_update: bool = False
    input_tags: dict = {}
    """
    Input tags are tags that this plugin wants to get from others.
    """

    def get_tag(self, name: str) -> dict:
        """Get the tags from the plugin. This is used to get the
        tags from the plugin and send them to the backend.
        """
        if name not in self.input_tags_that_need_update:
            self.input_tags_that_need_update.append(name)

        if name not in self.input_tags:
            self.input_tags[name] = None

        return self.input_tags[name]

    def get_mem_tag(self, name: str) -> dict:
        """Get the tags from the plugin without updating them.
        This is used to get the tags from the plugin without
        sending them to the backend.
        """
        if name not in self.mem_tags_that_need_update:
            self.mem_tags_that_need_update.append(name)

        if name not in self.input_tags:
            self.input_tags[name] = None

        return self.input_tags[name]

    def set_tag(self, name: str, value) -> None:
        """Set a tag in the plugin. This is used to set a tag
        in the plugin and send it to the backend.
        """
        self.output_tags[name] = value
        self.output_needs_update = True
        return None

    def set_mem_tag(self, name: str, value) -> None:
        """Set a memory tag."""
        self.mem_output[name] = value
        self.mem_needs_update = True
        return None

    def emit_event(self, alias: str, event: Event, *args, **kwargs) -> None:
        """Emit an event to the backend."""
        message = PluginMessage(
            Channel.EMIT_EVENT,
            {"alias": alias, "event": event, "args": args, "kwargs": kwargs},
        )
        self.return_queue.put(message, block=True)
        return None

    def update_plugin(self) -> None:
        logging.info(f"Importing plugin file from {self.path}")
        import_path = self.path.replace("\\", ".").replace("/", ".") + ".main"

        try:
            self.file = importlib.import_module(import_path)
        except Exception as e:
            logging.error(f"Error importing plugin file: {e}")
            self.return_queue.put(
                PluginMessage(
                    Channel.CRASHED, {"message": f"Error importing plugin file: {e}"}
                )
            )
            raise ImportError(f"Error importing plugin file: {e}") from e

        logging.info(f"Plugin file imported successfully: {self.file}")

        self.description = self.file.Plugin.description
        self.authors = self.file.Plugin.author
        if type(self.authors) is not list:
            self.authors = [self.authors]

        if self.description.id == "":
            # Plugins/AdaptiveCruiseControl/main.py
            # -> plugins.adaptivecruisecontrol
            self.description.id = import_path.replace(".main", "").lower()

        logging.info(
            f"Read plugin description. {self.description.name} by {', '.join(author.name for author in self.authors)}"
        )

        # Pages need to be instantiated before use.
        self.pages = self.file.Plugin.pages
        self.pages = list(filter(lambda p: p is not None, self.pages))
        self.pages = [page() for page in self.pages]  # type: ignore
        logging.info(f"Loaded {len(self.pages)} pages")

        # Controls don't need to be instantiated before use.
        # They are instantiated when the plugin is created.
        self.controls = self.file.Plugin.controls
        logging.info(f"Loaded {len(self.controls)} controls")

        return None

    def listener(self) -> None:
        """Send all messages into the stack."""
        while True:
            try:
                message: PluginMessage = self.queue.get(timeout=1)
            except Exception:
                if self.plugin:
                    time.sleep(0.01)
                else:
                    time.sleep(0.1)
                continue

            match message.channel:
                case Channel.GET_DESCRIPTION:
                    Description(self)(message)
                case (
                    Channel.ENABLE_PLUGIN | Channel.STOP_PLUGIN | Channel.RESTART_PLUGIN
                ):
                    self.main_thread_stack.append(message)
                case Channel.GET_TAGS | Channel.UPDATE_TAGS:
                    Tags(self)(message)
                case Channel.CALL_FUNCTION:
                    Function(self)(message)
                case Channel.GET_CONTROLS | Channel.CONTROL_STATE_UPDATE:
                    Controls(self)(message)
                case Channel.OPEN_EVENT | Channel.CLOSE_EVENT:
                    Page(self)(message)
                case Channel.RECEIVE_EVENT:
                    EventsHandler(self)(message)
                case Channel.MEM_TAGS_RECEIVED:
                    self.pending_mem_out_update = False
                case _:
                    self.stack[message.id] = message

    def memory_listener(self) -> None:
        """Listen to data tags from the shared memory"""
        while True:
            try:
                data = self.receiver.get(timeout=1)
            except Exception:
                if self.plugin:
                    time.sleep(0.01)
                else:
                    time.sleep(1)
                continue

            if type(data) is not dict:
                logging.error(f"Received invalid data type: {type(data)}")
                continue

            for tag in data:
                if tag not in self.input_tags:
                    self.input_tags[tag] = None

                self.input_tags[tag] = data[tag]
                self.pending_mem_update = False

    def wait_for_id(self, id: int) -> PluginMessage:
        """Wait for a message with the given ID."""
        while id not in self.stack:
            time.sleep(0.025)

        message = self.stack.pop(id)
        return message

    def memory_updater(self) -> None:
        while True:
            if self.mem_tags_that_need_update and not self.pending_mem_update:
                self.pending_mem_update = True
                message = PluginMessage(
                    Channel.GET_MEM_TAGS, {"tags": self.mem_tags_that_need_update}
                )

                self.mem_tags_that_need_update = []
                self.return_queue.put(message, block=False)

            if self.mem_needs_update:
                try:
                    self.sender.put(self.mem_output, block=True)
                    self.last_mem_output_time = time.time()
                    self.mem_needs_update = False
                    self.mem_output = {}
                except Exception:
                    pass

            if self.plugin:
                time.sleep(0.01)
            else:
                time.sleep(1)

    def tag_updater(self) -> None:
        while True:
            if self.input_tags_that_need_update and not self.pending_input_update:
                self.pending_input_update = True
                message = PluginMessage(
                    Channel.GET_TAGS, {"tags": self.input_tags_that_need_update}
                )

                self.input_tags_that_need_update = []
                self.return_queue.put(message, block=False)

            if self.output_needs_update and (
                not self.pending_output_update
                or time.time() > self.last_output_time + 1
            ):
                self.pending_output_update = True
                message = PluginMessage(Channel.UPDATE_TAGS, self.output_tags)

                self.return_queue.put(message, block=False)

                self.last_output_time = time.time()
                self.output_needs_update = False
                self.output_tags = {}

            if self.plugin:
                time.sleep(0.01)
            else:
                time.sleep(0.1)

    def process(self) -> None:
        """Keep the process alive."""
        while True:
            # Execute all main thread messages
            if self.main_thread_stack:
                message = self.main_thread_stack.pop(0)
                match message.channel:
                    case (
                        Channel.ENABLE_PLUGIN
                        | Channel.STOP_PLUGIN
                        | Channel.RESTART_PLUGIN
                    ):
                        PluginManagement(self)(message)

            try:
                if not self.plugin:
                    time.sleep(1)
                    continue
            except KeyboardInterrupt:
                break

            start = time.time()
            try:
                self.plugin.before()
            except Exception as e:
                logging.info(f"Error in plugin before(): {e}")

            try:
                self.plugin.run()
            except Exception:
                logging.exception("Error in plugin process.")

            try:
                self.plugin.after()
            except Exception as e:
                logging.info(f"Error in plugin after(): {e}")

            end = time.time()
            frametime = (end - start) * 1000  # Convert to milliseconds
            self.performance.append(PerformanceEntry(start, frametime))

    def performance_updater(self) -> None:
        """Update the performance data."""
        while True:
            time.sleep(1)
            if not self.performance:
                continue

            count = len(self.performance)
            total = sum(entry.frametime for entry in self.performance)
            average = total / count if count > 0 else 0
            self.performance = []

            message = PluginMessage(
                Channel.FRAMETIME_UPDATE,
                {
                    "frametime": average,
                },
            )
            self.return_queue.put(message, block=False)

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
                        Channel.UPDATE_PAGE, {"url": url, "data": dictionary}
                    )
                    message.state = State.DONE
                    self.return_queue.put(message, block=True)
                except Exception:
                    logging.exception("Page build failed.")

    def set_high_priority(self) -> None:
        p = psutil.Process(os.getpid())
        try:
            if os.name == "nt":
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(0)  # negative values need root / sudo
        except Exception as e:
            logging.exception(f"Error setting high priority: {e}")

    def __init__(
        self,
        path: str,
        queue: Queue,
        return_queue: Queue,
        sender: SharedMemorySender,
        receiver: SharedMemoryReceiver,
    ) -> None:
        start_time = time.time()
        events.emit_event = self.emit_event

        self.queue = queue
        self.return_queue = return_queue

        self.sender = sender
        self.receiver = receiver

        name = os.path.basename(path)
        setup_process_logging(
            name,
            console_level=logging.WARNING,
            filepath=os.path.join(os.getcwd(), "logs", f"{name}.log"),
        )
        logging.info("Started logging")

        if settings.high_priority:
            self.set_high_priority()
            logging.info("Set high priority for plugin process")

        files = os.listdir(path)
        if "main.py" not in files:
            self.return_queue.put(
                PluginMessage(
                    Channel.CRASHED,
                    {"message": "No main.py found in the plugin directory."},
                )
            )
            raise Exception("PluginProcess: No main.py found in the plugin directory.")

        self.path = path
        self.update_plugin()

        message = PluginMessage(Channel.SUCCESS, {"pid": os.getpid()})
        message.state = State.DONE
        self.return_queue.put(message)
        logging.info(f"Indicated success in {time.time() - start_time:.2f} seconds")

        threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.memory_listener, daemon=True).start()
        threading.Thread(target=self.tag_updater, daemon=True).start()
        threading.Thread(target=self.memory_updater, daemon=True).start()
        threading.Thread(target=self.page_updater, daemon=True).start()
        threading.Thread(target=self.performance_updater, daemon=True).start()
        logging.info("Threads started, moving to process loop")

        self.process()


# MARK: Handlers
class ChannelHandler:
    """A handler for a specific channel. These are
    used by the plugin process to respond to backend
    messages.
    """

    plugin: PluginProcess

    def __init__(self, plugin: PluginProcess):
        self.plugin = plugin

    def __call__(self, message: PluginMessage):
        """Handle a message from the plugin process.
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
        except Exception as e:
            message.state = State.ERROR
            message.data = "Error getting plugin description: " + str(e)
            logging.exception(f"Error getting plugin description: {e}")
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
                        updated = event.update(controls[event.alias])
                        if updated:
                            if event.type == "button":
                                events.emit(
                                    event.alias, event, event.pressed(), queue=False
                                )
                            elif event.type == "axis":
                                events.emit(
                                    event.alias, event, event.value(), queue=False
                                )

        except Exception:
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
                    self.plugin.plugin = self.plugin.file.Plugin(  # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,
                        self.plugin.get_tag,
                        self.plugin.set_tag,
                        self.plugin.get_mem_tag,
                        self.plugin.set_mem_tag,
                    )
                    events.plugin_object = self.plugin.plugin

                    for page in self.plugin.pages:
                        page.plugin = self.plugin.plugin

                    message.state = State.DONE
                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error enabling plugin")

            elif message.channel == Channel.STOP_PLUGIN:
                try:
                    del self.plugin.plugin
                    self.plugin.plugin = None
                    events.plugin_object = None
                    message.state = State.DONE

                    for page in self.plugin.pages:
                        page.plugin = None

                except Exception as e:
                    message.state = State.ERROR
                    message.data = e.args
                    logging.exception("Error stopping plugin")

            elif message.channel == Channel.RESTART_PLUGIN:
                try:
                    del self.plugin.plugin
                    self.plugin.plugin = None
                    self.plugin.update_plugin()
                    self.plugin.plugin = self.plugin.file.Plugin(  # type: ignore
                        self.plugin.path,
                        self.plugin.queue,
                        self.plugin.return_queue,
                        self.plugin.get_tag,
                        self.plugin.set_tag,
                        self.plugin.get_mem_tag,
                        self.plugin.set_mem_tag,
                    )
                    events.plugin_object = self.plugin.plugin

                    for page in self.plugin.pages:
                        page.plugin = self.plugin

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

        except Exception:
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
                    page_object = p.__class__.__name__
                    if page_object == object:
                        page = p
                        break

                if page is None:
                    logging.error(
                        f"Page {object} not found on plugin {self.plugin.path}"
                    )
                    return None

                function = getattr(page, function)
                page.reset_timer()  # trigger a refresh of the page data

            try:
                if args and kwargs:
                    function(*args, **kwargs)
                elif args:
                    function(*args)
                elif kwargs:
                    function(**kwargs)
                else:
                    function()
            except Exception:
                logging.exception("Error calling function")

        except Exception:
            logging.exception("Error handling function")


class Page(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.state == State.ERROR:
                logging.error("Error getting page, " + message.data)
                return None

            if message.channel == Channel.OPEN_EVENT:
                url = message.data.get("url")
                for page in self.plugin.pages:
                    if page.url == url:
                        page.open_event()
                        return None

            elif message.channel == Channel.CLOSE_EVENT:
                url = message.data.get("url")
                for page in self.plugin.pages:
                    if page.url == url:
                        page.close_event()
                        return None

        except Exception:
            logging.exception("Error handling page event")


class EventsHandler(ChannelHandler):
    def __call__(self, message: PluginMessage):
        try:
            if message.state == State.ERROR:
                logging.error("Error handling event, " + message.data)
                return None

            alias = message.data.get("alias")
            event = message.data.get("event")
            args = message.data.get("args", [])
            kwargs = message.data.get("kwargs", {})
            kwargs["queue"] = False

            events.emit(alias, event, *args, **kwargs)
        except Exception:
            logging.exception("Error handling event")
