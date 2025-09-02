from ETS2LA.Plugin.message import PluginMessage, Channel
from ETS2LA.Utils.Values.dictionaries import merge

from multiprocessing import Queue
from typing import Literal, Callable
import threading
import logging
import json
import time


class Tags:
    def __init__(self, get_tag: Callable, set_tag: Callable) -> None:
        self.get_tag = get_tag
        self.set_tag = set_tag

    def __getattr__(self, name):
        if name in ["get_tag", "set_tag"]:
            return super().__getattr__(name)  # type: ignore

        return self.get_tag(name)  # type: ignore

    def __setattr__(self, name, value):
        if name in ["get_tag", "set_tag"]:
            return super().__setattr__(name, value)

        self.set_tag(name, value)  # type: ignore
        return None

    def merge(self, tag_dict: dict):
        if tag_dict is None:
            return None

        plugins = tag_dict.keys()
        count = len(plugins)

        data = {}
        for plugin in tag_dict:
            if isinstance(tag_dict[plugin], dict):
                if count > 1:
                    data = merge(data, tag_dict[plugin])
                else:
                    data = tag_dict[plugin]
                    break
            else:
                data = tag_dict[plugin]
        return data


class GlobalSettings:  # read only instead of the plugin settings
    def __init__(self) -> None:
        self._path = "ETS2LA/global.json"
        self._settings = {}
        self._load()

    def _load(self):
        with open(self._path, "r") as file:
            self._settings = json.load(file)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        if name in self._settings:
            return self._settings[name]

        logging.warning(f"Setting '{name}' not found in settings file")
        return None

    def __setattr__(self, name: str, value) -> None:
        if name in ["_path", "_settings"]:
            self.__dict__[name] = value
        else:
            raise TypeError("Global settings are read-only")


class State:
    text: str = ""
    progress: float = -1

    timeout: int = -1
    timeout_thread: threading.Thread | None = None
    last_update: float = 0

    state_queue: Queue

    def timeout_thread_func(self):
        while time.perf_counter() - self.last_update < self.timeout:
            time.sleep(0.1)
        self.reset()

    def __init__(self, state_queue: Queue):
        self.state_queue = state_queue
        self.text = ""
        self.progress = -1

    def __setattr__(self, name, value):
        if name in ["text", "status", "state"]:
            self.last_update = time.perf_counter()

            message = PluginMessage(
                Channel.STATE_UPDATE, {"status": value, "progress": self.progress}
            )

            self.state_queue.put(message, block=True)
            super().__setattr__("text", value)
            return

        if name in ["value", "progress"]:
            self.last_update = time.perf_counter()

            message = PluginMessage(
                Channel.STATE_UPDATE, {"progress": value, "status": self.text}
            )

            self.state_queue.put(message, block=True)
            super().__setattr__("progress", value)
            return

        if name in ["timeout"]:
            self.last_update = time.perf_counter()
            super().__setattr__("timeout", value)
            if self.timeout_thread is None:
                print("Starting timeout thread")
                self.timeout_thread = threading.Thread(
                    target=self.timeout_thread_func, daemon=True
                )
                self.timeout_thread.start()
            return

        super().__setattr__(name, value)

    def reset(self):
        self.text = ""
        self.progress = -1


class Global:
    settings: GlobalSettings
    """
    You can use this to access the global settings with dot notation.
    
    Example:
    ```python
    # Get Data
    setting_data = self.globals.settings.setting_name
    # Set Data
    self.globals.settings.setting_name = 5
    -> TypeError: Global settings are read only
    ```
    """
    tags: Tags
    """
    You can access the tags by using dot notation.
    
    Example:
    ```python
    # Get Data
    tag_data = self.globals.tags.tag_name
    
    # Set Data
    self.globals.tags.tag_name = 5
    ```
    """

    def __init__(self, get_tag: Callable, set_tag: Callable) -> None:
        self.settings = GlobalSettings()
        self.tags = Tags(get_tag, set_tag)


class PluginDescription:
    """ETS2LA Plugin Description

    :param str name: The name of the plugin.
    :param str version: The version of the plugin.
    :param str description: The description of the plugin.
    :param str id: The ID of the plugin. If not set, it will be generated from the filepath. This ID is used to identify the plugin in the backend.
    :param list[str] tags: The list of tags to show on the frontend.
    :param list[str] dependencies: List of plugin names that this plugin depends on. FOLDER NAMES NOT THE name ATTRIBUTE!
    :param list[str] modules: List of modules that the plugin uses. FOLDER NAMES NOT THE name ATTRIBUTE!
    :param list[Literal["Windows", "Linux"]] compatible_os: List of OS that the plugin is compatible with.
    :param list[Literal["ETS2", "ATS"]] compatible_game: List of games that the plugin is compatible with.
    :param dict[str, str] update_log: The update log of the plugin.
    :param bool hidden: If the plugin is hidden from the frontend when development mode is not enabled.
    :param list[str] listen: List of files that will trigger a restart when changed. Default is ["*.py"] (all python files in the root folder). Listening only works in dev mode.
    :param float fps_cap: The maximum frames per second the plugin will run at. Default is 30.
    """

    name: str
    version: str
    description: str
    id: str = ""
    tags: list[str]
    dependencies: list[str]
    modules: list[str]
    compatible_os: list[Literal["Windows", "Linux"]] = ["Windows", "Linux"]
    compatible_game: list[Literal["ETS2", "ATS"]] = ["ETS2", "ATS"]
    update_log: dict[str, str] = {}
    hidden: bool = False
    listen: list[str] = ["*.py"]
    ui_filename: str = ""
    fps_cap: float = 30.0

    def __init__(
        self,
        name: str = "",
        version: str = "",
        description: str = "",
        tags: list[str] = None,
        dependencies: list[str] = None,
        compatible_os: list[Literal["Windows", "Linux"]] = None,
        compatible_game: list[Literal["ETS2", "ATS"]] = None,
        update_log: dict[str, str] = None,
        modules: list[str] = None,
        hidden: bool = False,
        listen: list[str] = None,
        ui_filename: str = "",
        fps_cap: float = 30.0,
    ) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies if dependencies else []
        self.compatible_os = compatible_os if compatible_os else ["Windows", "Linux"]
        self.compatible_game = compatible_game if compatible_game else ["ETS2", "ATS"]
        self.update_log = update_log if update_log else {}
        self.modules = modules if modules else []
        self.tags = tags if tags else []
        self.hidden = hidden
        self.listen = listen if listen else ["*.py"]
        self.ui_filename = ui_filename
        self.fps_cap = fps_cap
