from ETS2LA.Plugin.process import (
    PluginProcess,
    PluginDescription,
    PluginMessage,
    Author,
)
from ETS2LA.Networking.Servers import notifications
from ETS2LA.Networking.cloud import SendCrashReport
from ETS2LA.Plugin.message import Channel, State
from ETS2LA.Utils.translator import _
from ETS2LA.Controls import ControlEvent
from ETS2LA.Handlers import controls
from ETS2LA.Utils import settings
from ETS2LA import variables

from memory import create_shared_memory_pair, SharedMemorySender, SharedMemoryReceiver
import multiprocessing
import threading

import logging
import time
import os

search_folders: list[str] = ["Plugins", "CataloguePlugins"]

loading: bool = False
"""Indicator for other files that the plugin handler is still loading plugins."""

# Discover all plugins in the search folders.
plugin_folders: list[str] = []


def discover_plugins() -> None:
    global plugin_folders
    plugin_folders = []

    for folder in search_folders:
        for root, _dirs, files in os.walk(folder):
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

    sender: SharedMemorySender
    """The sender for shared memory messages."""

    receiver: SharedMemoryReceiver
    """The receiver for shared memory messages."""

    stack: dict[Channel, dict[int, PluginMessage]]
    """All the messages that have arrived from the plugin."""

    controls: list[ControlEvent]
    """All the controls that belong to the plugin."""

    last_controls_state: dict
    """The last state of the controls."""

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

    files: str
    """List of files that the plugin wants the backend to check for changes for."""

    file_times: dict[str, float]
    """The last modification times of the files the plugin wants to check."""

    frametimes: list[float]
    """
    A list of all frametimes recorded by the plugin.
    """

    def start_plugin(self) -> None:
        # First initialize / reset the variables
        self.stack = {}
        self.state = {"status": "", "progress": -1}
        self.frametimes = []
        self.last_controls_state = {}
        self.stop = False
        self.running = False

        self.queue = multiprocessing.Queue()
        self.return_queue = multiprocessing.Queue()
        plugin_sender, self.receiver = create_shared_memory_pair(1)
        self.sender, plugin_receiver = create_shared_memory_pair(1)

        # Then kill and start the new process
        if "process" in self.__dict__ and self.process.is_alive():
            self.process.kill()
            self.process.join()
            self.process.close()
            self.process = None  # type: ignore

        self.files = []
        self.file_times = {}
        self.process = multiprocessing.Process(
            target=PluginProcess,
            args=(
                self.folder,
                self.queue,
                self.return_queue,
                plugin_sender,
                plugin_receiver,
            ),
            daemon=True,
            name=f"Plugin {self.folder.split('/')[-1]} Process",
        )

        # The plugin was stopped / restarted, we clear the tags so they don't linger.
        if "description" in self.__dict__:
            self.discover_files()
            for tag in self.tags:
                if self.description.id in self.tags[tag]:
                    self.tags[tag][self.description.id] = {}

        self.process.start()

    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.start_plugin()

        threading.Thread(target=self.listener, daemon=True).start()

        message = self.wait_for_channel_message(Channel.SUCCESS, 1, timeout=30)
        if message is None:
            logging.error(
                _(
                    "Plugin {0} failed to start: Timeout.\nTry to close other programs to give more memory and CPU to the plugin."
                ).format(folder)
            )
            self.remove()
            return

        if message.data != {}:
            logging.error(
                _("Plugin {0} failed to start: {1}").format(folder, message.data)
            )
            self.remove()
            return

        plugins.append(self)
        self.get_description()

        if (
            self.description.hidden or "Base" not in self.description.tags
        ) and not variables.DEVELOPMENT_MODE:
            self.remove()
            return

        self.get_controls()

        threading.Thread(target=self.tag_handler, daemon=True).start()
        threading.Thread(target=self.memory_handler, daemon=True).start()
        threading.Thread(target=self.state_handler, daemon=True).start()
        threading.Thread(target=self.page_handler, daemon=True).start()
        threading.Thread(target=self.controls_updater, daemon=True).start()
        threading.Thread(target=self.notification_handler, daemon=True).start()
        threading.Thread(target=self.performance_handler, daemon=True).start()
        threading.Thread(target=self.check_edit_thread, daemon=True).start()

        self.keep_alive()

    def keep_alive(self) -> None:
        """Keep the process alive."""
        logging.debug(
            _("Plugin [yellow]{0}[/yellow] loaded successfully.").format(
                self.description.name
            )
        )
        while not self.stop:
            time.sleep(1)
        self.remove()

    def listener(self):
        """Send all messages into the stack."""
        while True:
            if self.stop:
                return

            try:
                message: PluginMessage = self.return_queue.get(timeout=2)
            except Exception:
                if self.running:
                    time.sleep(0.01)
                else:
                    time.sleep(0.1)
                continue

            if message.channel == Channel.CRASHED:
                name = (
                    self.description.name
                    if "description" in self.__dict__
                    else self.folder
                )
                SendCrashReport(
                    "Plugin Crash",
                    f"{name} has indicated a crash.",
                    {
                        "Error": message.data["message"]
                        if message.data
                        else "No details provided",
                    },
                )
                threading.Thread(
                    target=stop_plugin,
                    kwargs={"description": self.description}
                    if "description" in self.__dict__
                    else {"folder": self.folder},
                    daemon=True,
                ).start()
                continue

            if message.channel == Channel.STOP_PLUGIN:
                threading.Thread(
                    target=stop_plugin,
                    kwargs={"description": self.description},
                    daemon=True,
                ).start()
                continue

            if message.channel not in self.stack:
                self.stack[message.channel] = {}
            self.stack[message.channel][message.id] = message

    def controls_updater(self):
        while True:
            if self.stop:
                return

            states = controls.get_states(self.controls)
            if not self.last_controls_state or states != self.last_controls_state:
                self.last_controls_state = states
                message = PluginMessage(Channel.CONTROL_STATE_UPDATE, states)
                self.queue.put(message)

            if self.running:
                time.sleep(0.025)
            else:
                time.sleep(0.25)

    def tag_handler(self):
        while True:
            if self.stop:
                return

            if Channel.GET_TAGS in self.stack:
                while self.stack[Channel.GET_TAGS]:
                    message = self.stack[Channel.GET_TAGS].popitem()[1]

                    tags = message.data["tags"]
                    response = {}
                    for tag in tags:
                        if tag == "running":
                            response[tag] = {
                                plugin.description.id: plugin.running
                                for plugin in plugins
                            }
                        elif tag == "state":
                            response[tag] = {
                                plugin.description.id: plugin.state
                                for plugin in plugins
                            }
                        else:
                            response[tag] = self.tags.get(tag, None)

                    message.state = State.DONE
                    message.data = response
                    self.queue.put(message, block=True)

            if Channel.UPDATE_TAGS in self.stack:
                while self.stack[Channel.UPDATE_TAGS]:
                    message = self.stack[Channel.UPDATE_TAGS].popitem()[1]
                    data = message.data

                    for tag, value in data.items():
                        if tag not in self.tags:
                            self.tags[tag] = {}

                        if self.description.id not in self.tags[tag]:
                            self.tags[tag][self.description.id] = {}

                        self.tags[tag][self.description.id] = value

                    message.state = State.DONE
                    message.data = "success"  # clear data for faster transmit
                    self.queue.put(message, block=True)

            if self.running:
                time.sleep(0.01)
            else:
                time.sleep(0.25)

    def memory_handler(self):
        while True:
            if self.stop:
                return

            if Channel.GET_MEM_TAGS in self.stack:
                while self.stack[Channel.GET_MEM_TAGS]:
                    message = self.stack[Channel.GET_MEM_TAGS].popitem()[1]

                    tags = message.data["tags"]
                    response = {}
                    for tag in tags:
                        response[tag] = self.tags.get(tag, {})

                    self.sender.put(response)

            try:
                data = self.receiver.get_nowait()
                if data:
                    for tag, value in data.items():
                        if tag not in self.tags:
                            self.tags[tag] = {}

                        if self.description.id not in self.tags[tag]:
                            self.tags[tag][self.description.id] = {}

                        self.tags[tag][self.description.id] = value
            except Exception:
                pass

            if self.running:
                time.sleep(0.01)
            else:
                time.sleep(0.25)

    def state_handler(self):
        while True:
            if self.stop:
                return

            if Channel.STATE_UPDATE in self.stack:
                while self.stack[Channel.STATE_UPDATE]:
                    message = self.stack[Channel.STATE_UPDATE].popitem()[1]
                    if "progress" in message.data and "status" in message.data:
                        self.state["progress"] = message.data["progress"]
                        self.state["status"] = message.data["status"]

            if self.running:
                time.sleep(0.1)
            else:
                time.sleep(1)

    def page_handler(self):
        while True:
            if self.stop:
                return

            if Channel.UPDATE_PAGE in self.stack:
                while self.stack[Channel.UPDATE_PAGE]:
                    message = self.stack[Channel.UPDATE_PAGE].popitem()[1]
                    if "url" in message.data:
                        url = message.data["url"]
                        data = message.data["data"]
                        data[0]["plugin"] = self.description.id
                        self.pages[url] = data
                        variables.REFRESH_PAGES = True

            time.sleep(0.01)

    def notification_handler(self):
        while True:
            if self.stop:
                return

            if Channel.NOTIFICATION in self.stack:
                while self.stack[Channel.NOTIFICATION]:
                    message = self.stack[Channel.NOTIFICATION].popitem()[1]
                    if "text" in message.data and "type" in message.data:
                        text = message.data["text"]
                        type_ = message.data["type"]
                        notifications.sonner(text=text, type=type_)

            if Channel.NAVIGATE in self.stack:
                while self.stack[Channel.NAVIGATE]:
                    message = self.stack[Channel.NAVIGATE].popitem()[1]
                    if "url" in message.data:
                        url = message.data["url"]
                        reason = message.data.get("reason", "")
                        plugin = self.description.id
                        notifications.navigate(url, plugin, reason)

            time.sleep(0.1)

    def performance_handler(self):
        """Handle the performance data from the plugin."""
        while True:
            if self.stop:
                return

            if Channel.FRAMETIME_UPDATE in self.stack:
                while self.stack[Channel.FRAMETIME_UPDATE]:
                    message = self.stack[Channel.FRAMETIME_UPDATE].popitem()[1]
                    if "frametime" in message.data:
                        frametime = message.data["frametime"]
                        self.frametimes.append(frametime)
                        if len(self.frametimes) > 60:
                            self.frametimes.pop(0)

            time.sleep(0.5)

    def wait_for_channel_message(
        self, channel: Channel, id: int, timeout: float = -1
    ) -> PluginMessage | None:
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

    def remove(self) -> None:
        """Remove the current plugin"""
        self.stop = True
        try:
            plugins.remove(self)
        except Exception:
            pass

        try:
            self.process.kill()
            self.process.join()
            self.process.close()
            self.process = None
        except Exception:
            pass
        quit(1)
        return

    def was_edited(self) -> bool:
        for file in self.files:
            if not os.path.exists(file):
                continue

            current = os.path.getmtime(file)
            if file not in self.file_times:
                self.file_times[file] = current
                continue

            if current != self.file_times[file]:
                self.file_times[file] = current
                return True

    def discover_files(self):
        rules = self.description.listen  # default = ["*.py"]
        files = []
        for root, _dirs, filenames in os.walk(self.folder):
            for rule in rules:
                if rule == "*":  # All
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
                elif rule.startswith("*"):  # Ending
                    ext = rule[1:]
                    for filename in filenames:
                        if filename.endswith(ext):
                            files.append(os.path.join(root, filename))
                elif rule.endswith("*"):  # Beginning
                    start = rule[:-1]
                    for filename in filenames:
                        if filename.startswith(start):
                            files.append(os.path.join(root, filename))
                else:
                    for filename in filenames:  # Exact
                        if filename == rule:
                            files.append(os.path.join(root, filename))

        self.files = files

    def get_description(self) -> PluginDescription:
        """Get the plugin description from the plugin process."""
        message = PluginMessage(Channel.GET_DESCRIPTION, {})
        self.queue.put(message)
        response = self.wait_for_channel_message(
            message.channel, message.id, timeout=10
        )
        if response is None:
            logging.error(
                _("Plugin {0} failed to get description: Timeout.").format(self.folder)
            )
            self.remove()

        if response.state == State.ERROR:
            logging.error(
                _("Plugin {0} failed to get description: {1}").format(
                    self.folder, response.data
                )
            )
            SendCrashReport(
                "Error Fetching Description",
                f"The runner for {self.folder} failed to get it's description.",
                {
                    "Error": response.data if response.data else "No details provided",
                },
            )
            self.remove()

        self.description, self.authors = response.data
        self.discover_files()

        return response.data

    def check_edit_thread(self) -> None:
        if not variables.DEVELOPMENT_MODE:
            return

        while True:
            if self.stop:
                return

            time.sleep(2)
            if self.was_edited():
                logging.info(
                    f"Plugin {self.description.name} has been edited. Reloading..."
                )
                if self.running:
                    threading.Thread(
                        target=restart_plugin,
                        args=(self.description, self.description.name, self.folder),
                        daemon=True,
                    ).start()
                else:
                    threading.Thread(
                        target=stop_plugin,  # will actually just reset
                        args=(self.description, self.description.name, self.folder),
                        daemon=True,
                    ).start()

    def get_controls(self) -> list[ControlEvent]:
        """Get the controls from the plugin process."""
        message = PluginMessage(Channel.GET_CONTROLS, {})
        self.queue.put(message)
        response = self.wait_for_channel_message(message.channel, message.id, timeout=5)
        if response is None:
            logging.error(
                _("Plugin {0} failed to get controls: Timeout.").format(self.folder)
            )
            self.remove()

        if response.state == State.ERROR:
            SendCrashReport(
                "Error Fetching Controls",
                f"The runner for {self.folder} failed to get it's controls.",
                {
                    "Error": response.data if response.data else "No details provided",
                },
            )
            logging.error(
                _("Plugin {0} failed to get controls: {1}").format(
                    self.folder, response.data
                )
            )
            self.remove()

        self.controls = response.data
        for control in self.controls:
            control.plugin = self.description.id

        controls.validate_events(self.controls)
        return response.data


def reload_plugins() -> None:
    global plugins
    for plugin in plugins:
        plugin.stop = True
        plugin.process.kill()
        plugin.process.join()
        plugin.process.close()

    plugins = []
    discover_plugins()
    threading.Thread(target=create_processes, daemon=True).start()


def create_process(folder: str) -> bool:
    initial_state = len(plugins)
    try:
        threading.Thread(
            target=Plugin,
            name=f"Backend for {folder.split('/')[-1]}",
            args=(folder,),
            daemon=True,
        ).start()
    except Exception:
        return False

    start = time.time()
    while len(plugins) == initial_state:
        time.sleep(0.1)
        if time.time() - start > 10:
            logging.warning(f"Timeout waiting for plugin {folder} to load.")
            return False

    return True


# MARK: Startup
plugins: list[Plugin] = []


def create_processes() -> None:
    global loading
    loading = True

    timeout = 12
    low_performance = settings.Get("global", "slow_loading", False)

    for folder in plugin_folders:
        initial_state = len(plugins)
        logging.debug(f"Creating plugin process for {folder}")
        threading.Thread(
            target=Plugin,
            name=f"Backend for {folder.split('/')[-1]}",
            args=(folder,),
            daemon=True,
        ).start()

        if low_performance:
            waiting_since = time.time()
            while len(plugins) == initial_state:
                time.sleep(0.1)
                if time.time() - waiting_since > timeout:
                    logging.warning(f"Timeout waiting for plugin {folder} to load.")
                    break

    if not low_performance:
        time.sleep(10)

    loading = False
    logging.info(_("Loaded {0} plugins.").format(len(plugins)))


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
        if plugin.folder.replace("\\", "/") == folder.replace("\\", "/"):
            return plugin
    return None


def match_plugin_by_id(id: str) -> Plugin | None:
    """Match a plugin by its ID."""
    for plugin in plugins:
        if plugin.description.id == id:
            return plugin
    return None


def match_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None,
    id: str | None = None,
) -> Plugin | None:
    """Match a plugin by its description, name or folder."""
    if description is not None:
        return match_plugin_by_description(description)
    if name is not None:
        return match_plugin_by_name(name)
    if folder is not None:
        return match_plugin_by_folder(folder)
    if id is not None:
        return match_plugin_by_id(id)

    return None


# MARK: Enable/Disable
def start_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None,
    id: str | None = None,
) -> bool:
    """Start a plugin based on one of the parameters."""
    plugin: Plugin | None = match_plugin(
        description=description, name=name, folder=folder, id=id
    )
    if not plugin:
        logging.error(_("Plugin not found."))
        return False

    if plugin.process.is_alive():
        message = PluginMessage(Channel.ENABLE_PLUGIN, {})
        plugin.queue.put(message)
        response = plugin.wait_for_channel_message(
            message.channel, message.id, timeout=30
        )
        if response and response.state == State.DONE:
            plugin.running = True
            logging.info(
                _("Plugin [yellow]{0}[/yellow] started successfully.").format(
                    plugin.description.name
                )
            )
            return True
        else:
            if response and response.data == "Plugin is already enabled":
                return False
            else:
                plugin.running = False
                logging.error(
                    _("Failed to start plugin: {0}").format(
                        response.data if response else _("Timeout")
                    )
                )
                return False

    return False


def stop_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None,
    id: str | None = None,
    stop_process: bool = False,
) -> bool:
    """Stop a plugin based on one of the parameters."""
    plugin: Plugin | None = match_plugin(
        description=description, name=name, folder=folder, id=id
    )
    if not plugin:
        logging.error(
            _(
                "Plugin not found, this can be a result of a plugin crash or failure to load."
            )
        )
        return False

    plugin.start_plugin()
    response = plugin.wait_for_channel_message(Channel.SUCCESS, 1, timeout=30)
    plugin.running = False

    if stop_process:
        plugin.stop = True
        plugin.process.kill()
        plugin.process.join()
        plugin.process.close()

    if response and response.state == State.DONE:
        logging.info(
            _("Plugin [yellow]{0}[/yellow] stopped successfully.").format(
                plugin.description.name
            )
        )
        return True
    else:
        logging.error(
            _("Failed to stop plugin: {0}").format(
                response.data if response else _("Timeout")
            )
        )
        return False

    return False


def restart_plugin(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None,
    id: str | None = None,
) -> bool:
    """Restart a plugin based on one of the parameters."""
    try:
        stop_plugin(description=description, name=name, folder=folder, id=id)
        start_plugin(description=description, name=name, folder=folder, id=id)
        return True
    except Exception as e:
        logging.error(_("Failed to restart plugin: {0}").format(e))
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
                pages[url] = data[0]  # metadata

    return pages


def page_open_event(url: str):
    page = {}
    for plugin in plugins:
        if url in plugin.pages:
            page = plugin.pages[url]
            break

    if not page:
        return

    plugin_id = page[0]["plugin"]
    plugin = match_plugin(id=plugin_id)
    if not plugin:
        logging.error(_("Plugin {0} not found for page {1}.").format(plugin_id, url))
        return

    plugin.queue.put(PluginMessage(Channel.OPEN_EVENT, {"url": url}))


def page_close_event(url: str):
    page = {}
    for plugin in plugins:
        if url in plugin.pages:
            page = plugin.pages[url]
            break

    if not page:
        return

    plugin_id = page[0]["plugin"]
    plugin = match_plugin(id=plugin_id)
    if not plugin:
        logging.error(_("Plugin {0} not found for page {1}.").format(plugin_id, url))
        return

    plugin.queue.put(PluginMessage(Channel.CLOSE_EVENT, {"url": url}))


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
            states[plugin.description.id] = plugin.state

    return states


def function_call(
    description: PluginDescription | None = None,
    name: str | None = None,
    folder: str | None = None,
    id: str | None = None,
    function: str = "",
    *args,
    **kwargs,
) -> bool:
    """Start a plugin based on one of the parameters."""
    plugin: Plugin | None = match_plugin(
        description=description, name=name, folder=folder, id=id
    )

    if not plugin:
        logging.error(_("Plugin not found."))
        return False

    plugin.queue.put(
        PluginMessage(
            Channel.CALL_FUNCTION,
            {"function": function, "args": args, "kwargs": kwargs},
        )
    )

    return True


def save_running_plugins() -> None:
    running = []
    for plugin in plugins:
        if plugin.running:
            running.append(plugin.description.id)

    settings.Set("global", "running_plugins", running)
