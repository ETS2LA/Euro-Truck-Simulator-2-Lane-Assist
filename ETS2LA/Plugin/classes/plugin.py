from ETS2LA.Plugin.classes.attributes import Tags, PluginDescription, State
from ETS2LA.Plugin.classes.author import Author

from ETS2LA.Plugin.message import Channel, PluginMessage
from ETS2LA.Controls import ControlEvent
from ETS2LA.UI import ETS2LAPage

from multiprocessing import Queue
import importlib

from types import SimpleNamespace
from typing import Literal, List, Callable
import logging
import time
import os


class ETS2LAPlugin(object):
    """This is the main plugin object, you will see a list of attributes below.

    :param Description description: The description of the plugin.
    :param Author author: The author of the plugin.
    :param list[ControlEvent] controls: The list of control events to listen to.
    :param Tags tags: Get/Set tags to the backend.
    :param State state: Send a persistent state to the backend.
    :param Plugins plugins: Interactions with other plugins.

    Functions:
        **notify(text: str, type: str)** - Show a notification in the frontend.
    """

    path: str

    description: PluginDescription = PluginDescription()
    author: List[Author]
    controls: List[ControlEvent] = []
    pages: List[ETS2LAPage] = []

    queue: Queue
    return_queue: Queue

    state: State
    """
    The state of the plugin shown in the frontend.
    
    Example:
    ```python
    while HeavyOperation():
        percentage = 0.66
        self.state.text = f"Loading... ({round(percentage * 100)}%)"
        self.state.progress = percentage
    
    self.state.reset()
    # or
    self.state.text = ""
    self.state.progress = -1
    ```
    """

    tags: Tags
    """
    Get/Set tags to the backend. 
    
    Example:
    ```python
    self.tags.some_tag = "Hello, World!"
    print(self.tags.some_tag) # "Hello, World!"
    ```
    """

    modules: SimpleNamespace
    """
    Access to all running modules that were defined in the description object.
    
    Example:
    ```python
    
    ```
    """

    def ensure_functions(self) -> None:
        if type(self).before != ETS2LAPlugin.before:
            raise TypeError("'before' is a reserved function name")
        if type(self).after != ETS2LAPlugin.after:
            raise TypeError("'after' is a reserved function name")
        if "run" not in dir(type(self)):
            raise TypeError("Your plugin has to have a 'run' function.")
        if type(self).__name__ != "Plugin":
            raise TypeError("Please make sure the class is named 'Plugin'")

    get_mem_tag: Callable
    set_mem_tag: Callable

    def __new__(
        cls,
        path: str,
        queue: Queue,
        return_queue: Queue,
        get_tag: Callable,
        set_tag: Callable,
        get_mem_tag: Callable,
        set_mem_tag: Callable,
    ) -> object:
        instance = super().__new__(cls)
        instance.path = path

        instance.queue = queue
        instance.return_queue = return_queue

        instance.get_mem_tag = get_mem_tag
        instance.set_mem_tag = set_mem_tag

        instance.tags = Tags(get_tag, set_tag)
        instance.state = State(return_queue)

        if type(instance.author) is not list:
            instance.author = [instance.author]

        return instance

    def load_modules(self) -> None:
        self.modules = SimpleNamespace()
        module_names = self.description.modules
        for module_name in module_names:
            module_path = f"Modules/{module_name}/main.py"
            if os.path.exists(module_path):
                python_object = importlib.import_module(
                    module_path.replace("/", ".").replace(".py", "")
                )
                module = python_object.Module(self)
                setattr(self.modules, module_name, module)
            else:
                logging.warning(f"Module '{module_name}' not found in '{module_path}'")

    def __init__(self, *args) -> None:
        self.ensure_functions()
        self.load_modules()

        self.controls = filter(lambda c: isinstance(c, ControlEvent), self.controls)
        self.pages = list(filter(lambda p: p is not None, self.pages))

        if "pages" in dir(type(self)) and self.pages is not None:
            for page in self.pages:
                page.plugin = self

        try:
            self.imports()
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'imports' function")

        try:
            self.init()
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'init' function")

        try:
            self.initialize()
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'initialize' function")

        try:
            self.Initialize()
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'Initialize' function")

    # def event_listener(self):
    #     while True:
    #         data = self.event_queue.get()
    #         args = data["args"]
    #         kwargs = data["kwargs"]
    #         kwargs.update({"queue": False})
    #
    #         Events.events.emit(data["name"], *args, **kwargs)
    #         self.event_queue.task_done()

    def try_call(self, function_name: str, *args, **kwargs):
        if args == ([], {}):
            args = []

        if hasattr(self, function_name):
            return getattr(self, function_name)(*args, **kwargs)

        return None

    def terminate(self):
        self.return_queue.put(PluginMessage(Channel.STOP_PLUGIN, {}), block=False)

        # Wait for the plugin to be terminated
        while True:
            time.sleep(1)

    def notify(
        self, text: str, type: Literal["info", "warning", "error", "success"] = "info"
    ):
        self.return_queue.put(
            PluginMessage(Channel.NOTIFICATION, {"text": text, "type": type}),
            block=False,
        )

    def navigate(self, url: str, reason: str = ""):
        self.return_queue.put(
            PluginMessage(Channel.NAVIGATE, {"url": url, "reason": reason}), block=False
        )

    def before(self) -> None:
        self.plugin_run_start_time = time.perf_counter()

    def after(self) -> None:
        self.plugin_run_end_time = time.perf_counter()
        time_to_sleep = max(
            1 / self.description.fps_cap
            - (self.plugin_run_end_time - self.plugin_run_start_time),
            0,
        )
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

    def send_large(self) -> None: ...
