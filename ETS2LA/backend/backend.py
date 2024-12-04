import ETS2LA.frontend.immediate as immediate
from ETS2LA.Plugin import *
from ETS2LA.UI import *
import multiprocessing
import threading
import ETS2LA.variables as variables
import logging
import inspect
import psutil
import time
import os

plugin_path = "plugins"
plugin_target_class = "Plugin"

AVAILABLE_PLUGINS: list[tuple[str, PluginDescription, Author, ETS2LASettingsMenu]] = []

class PluginHandler:
    
    plugin_name: str
    plugin_description: PluginDescription
    data = None
    
    stop = False
    
    tags: dict[str, any]
    
    state: dict = {
        "status": "",
        "progress": -1
    }
    
    last_performance: list[tuple[float, float]] = []
    last_performance_time: float = 0
    
    statistics: dict[str, any] = {}
    last_statistics_time: float = 0
    
    def __init__(self, plugin_name: str, plugin_description: PluginDescription):
        self.tags = {}
        self.plugin_name = plugin_name
        self.plugin_description = plugin_description
        self.data = None
        self.state = {
            "status": "",
            "progress": -1
        }
        
        self.last_performance = []
        self.last_performance_time = 0
        
        self.statistics = {
            "memory": [],
            "cpu": [],
            "performance": []
        }
        self.last_statistics_time = 0
        
        self.return_queue = multiprocessing.JoinableQueue()
        self.plugins_queue = multiprocessing.JoinableQueue()
        self.plugins_return_queue = multiprocessing.JoinableQueue()
        self.tags_queue = multiprocessing.JoinableQueue()
        self.tags_return_queue = multiprocessing.JoinableQueue()
        self.settings_menu_queue = multiprocessing.JoinableQueue()
        self.settings_menu_return_queue = multiprocessing.JoinableQueue()
        self.frontend_queue = multiprocessing.JoinableQueue()
        self.frontend_return_queue = multiprocessing.JoinableQueue()
        self.immediate_queue = multiprocessing.JoinableQueue()
        self.immediate_return_queue = multiprocessing.JoinableQueue()
        self.state_queue = multiprocessing.JoinableQueue()
        self.performance_queue = multiprocessing.JoinableQueue()
        self.performance_return_queue = multiprocessing.JoinableQueue()
        self.event_queue = multiprocessing.JoinableQueue()
        self.event_return_queue = multiprocessing.Queue()
        
        try:
            RUNNING_PLUGINS.append(self)
            threading.Thread(target=self.data_handler, daemon=True).start()
            threading.Thread(target=self.plugins_handler, daemon=True).start()
            threading.Thread(target=self.tags_handler, daemon=True).start()
            threading.Thread(target=self.immediate_handler, daemon=True).start()
            threading.Thread(target=self.state_handler, daemon=True).start()
            threading.Thread(target=self.change_listener, daemon=True).start()
            threading.Thread(target=self.event_listener, daemon=True).start()
            
            self.process = multiprocessing.Process(target=PluginRunner, args=(self.plugin_name, self.plugin_description,
                                                                            self.return_queue,
                                                                            self.plugins_queue, self.plugins_return_queue,
                                                                            self.tags_queue, self.tags_return_queue,
                                                                            self.settings_menu_queue, self.settings_menu_return_queue,
                                                                            self.frontend_queue, self.frontend_return_queue,
                                                                            self.immediate_queue, self.immediate_return_queue,
                                                                            self.state_queue,
                                                                            self.performance_queue, self.performance_return_queue,
                                                                            self.event_queue, self.event_return_queue
                                                                            ), daemon=True)
            self.process.start()
            
            threading.Thread(target=self.statistics_thread, daemon=True).start()
        except:
            logging.exception(f"Failed to start plugin {plugin_name}.")
        
    def change_listener(self):
        plugin_file_path = f"{plugin_path}/{self.plugin_name}/main.py"
        file_hash = hash(open(plugin_file_path, "rb").read())
        while True:
            if self.stop:
                break
            new_hash = hash(open(plugin_file_path, "rb").read())
            if new_hash != file_hash:
                logging.info(f"Plugin {self.plugin_name} has been updated, restarting.")
                file_hash = new_hash
                self.process.terminate()
                self.process.join()
                self.process = multiprocessing.Process(target=PluginRunner, args=(self.plugin_name, self.plugin_description,
                                                                            self.return_queue,
                                                                            self.plugins_queue, self.plugins_return_queue,
                                                                            self.tags_queue, self.tags_return_queue,
                                                                            self.settings_menu_queue, self.settings_menu_return_queue,
                                                                            self.frontend_queue, self.frontend_return_queue,
                                                                            self.immediate_queue, self.immediate_return_queue,
                                                                            self.state_queue,
                                                                            self.performance_queue, self.performance_return_queue,
                                                                            self.event_queue, self.event_return_queue
                                                                            ), daemon=True)
                self.process.start()
            time.sleep(1)
        
    def event_listener(self):
        while True:
            if self.stop:
                break
            try:
                data = self.event_return_queue.get(timeout=1)
            except:
                continue
            
            try:
                call_event(
                    data["name"],
                    data["args"],
                    data["kwargs"],
                    called_from=self.plugin_name
                )
            except:
                logging.exception(f"Failed to call event {data['name']} in plugin {self.plugin_name}.")
        
    def tags_handler(self):
        while True:
            if self.stop:
                break
            try:
                tag_dict = self.tags_queue.get(timeout=1)
            except:
                continue
            if tag_dict["operation"] == "read":
                tag = tag_dict["tag"]
                return_data = {}
                
                for plugin in RUNNING_PLUGINS:
                    if tag in plugin.tags:
                        return_data[plugin.plugin_name] = plugin.tags[tag]
                
                if return_data == {}:
                    return_data = None
                    
                self.tags_return_queue.put(return_data)
            elif tag_dict["operation"] == "write":
                self.tags[tag_dict["tag"]] = tag_dict["value"]
                self.tags_return_queue.put(True)
            else:
                self.tags_return_queue.put(False)

    def plugins_handler(self):
        while True:
            if self.stop:
                break
            try:
                plugin_name = self.plugins_queue.get(timeout=1)
            except:
                continue
            plugins = [plugin.plugin_name for plugin in RUNNING_PLUGINS]
            if plugin_name in plugins:
                index = plugins.index(plugin_name)
                self.plugins_return_queue.put(RUNNING_PLUGINS[index].data)
            else:
                self.plugins_return_queue.put(None)
                
    def immediate_handler(self):
        while True:
            if self.stop:
                break
            try:
                data = self.immediate_queue.get(timeout=1)
            except:
                continue
            if data["operation"] == "terminate":
                self.process.terminate()
                self.stop = True
                disable_plugin(self.plugin_name, from_plugin=True)
                
            if data["operation"] == "notify":
                type = data["options"]["type"]
                text = data["options"]["text"]
                immediate.sonner(text, type)
                self.immediate_return_queue.put(True)
            elif data["operation"] == "ask":
                text = data["options"]["text"]
                options = data["options"]["options"]
                description = data["options"]["description"]
                self.immediate_return_queue.put(immediate.ask(text, options, description=description))
            elif data["operation"] == "dialog":
                return_data = immediate.dialog(data["options"])
                self.immediate_return_queue.put(return_data)
            else:
                self.immediate_return_queue.put(False)

    def state_handler(self):
        while True:
            if self.stop:
                break
            try:
                data = self.state_queue.get(timeout=1)
            except:
                continue
            if "status" in data:
                self.state["status"] = data["status"]
            if "progress" in data:
                self.state["progress"] = data["progress"]

    def data_handler(self):
        while True:
            if self.stop:
                break
            try:
                data = self.return_queue.get(timeout=1)
            except:
                continue
            if type(data) == tuple:
                self.data = data[0]
                for tag in data[1]:
                    print(tag)
                    self.tags[tag] = data[1][tag]
            else:
                self.data = data
                
    def statistics_thread(self):
        while True:
            if self.stop:
                break
            
            if time.time() - self.last_statistics_time > 1:
                process = psutil.Process(self.process.pid)
                self.statistics["memory"].append(process.memory_percent())
                self.statistics["cpu"].append(process.cpu_percent())
                self.statistics["performance"] = self.get_performance()
                
                if len(self.statistics["memory"]) > 60:
                    self.statistics["memory"].pop(0)
                if len(self.statistics["cpu"]) > 60:    
                    self.statistics["cpu"].pop(0)
                
                self.last_statistics_time = time.time()
                
            time.sleep(0.1)
                
    def get_settings(self):
        self.settings_menu_queue.put(True)
        return self.settings_menu_return_queue.get()
    
    def call_function(self, name: str, *args, **kwargs):
        self.frontend_queue.put({
            "operation": "function",
            "target": name,
            "args": args,
            "kwargs": kwargs
        })
        
        try:
            return_data = self.frontend_return_queue.get(timeout=0.25)
        except:
            logging.exception(f"Failed to call function {name} in plugin {self.plugin_name}.")
            return None
            
        self.frontend_return_queue.task_done()
        return return_data
    
    def get_performance(self):
        if time.time() - self.last_performance_time > 1:
            self.performance_queue.put(True)
            data = self.performance_return_queue.get()
            self.performance_return_queue.task_done()
            self.last_performance = data
            self.last_performance_time = time.time()
            return data
        else:
            return self.last_performance
    

RUNNING_PLUGINS: list[PluginHandler] = []

def get_plugin_class(module_name):
    module = __import__(module_name, fromlist=['*'])
    for name, cls in inspect.getmembers(module):
        if inspect.isclass(cls) and issubclass(cls, ETS2LAPlugin) and cls != ETS2LAPlugin:
            return cls
    return None

def find_plugins() -> list[tuple[str, PluginDescription, Author]]:
    folders = os.listdir(plugin_path)
    plugins = []
    for folder in folders:
        if "main.py" in os.listdir(f"{plugin_path}/{folder}"):
            plugin_class = get_plugin_class(f"{plugin_path}.{folder}.main")
            if plugin_class is not None:
                information = getattr(plugin_class, "description", None)
                author = getattr(plugin_class, "author", None)
                settings = getattr(plugin_class, "settings_menu", None)
                plugins.append((folder, information, author, settings))
            del plugin_class
            
    return plugins

def enable_plugin(plugin_name: str):
    runner = threading.Thread(target=PluginHandler, args=(plugin_name, PluginDescription()), daemon=True)
    runner.start()
    
def disable_plugin(plugin_name: str, from_plugin: bool = False):
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == plugin_name:
            try:
                plugin.process.terminate()
            except:
                logging.warning(f"Failed to terminate plugin {plugin_name}, this could be because the plugin has already been terminated.")
            plugin.stop = True
            RUNNING_PLUGINS.remove(plugin)
            
            if not from_plugin:
                return True
    if not from_plugin:
        return False
    
def get_plugin_data(plugin_name: str):
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == plugin_name:
            return plugin.data
    return None

def get_plugin_settings() -> dict[str, None | list]:
    settings_dict = {}
    
    while variables.IS_UI_UPDATING:
        time.sleep(0.01)
    
    variables.IS_UI_UPDATING = True
    
    for name, desc, author, settings in AVAILABLE_PLUGINS:
        if settings is None:
            settings_dict[name] = None
            continue
        
        elif not settings.dynamic:
            settings_dict[name] = settings.build()
            
        elif name in [plugin.plugin_name for plugin in RUNNING_PLUGINS]:
            for plugin in RUNNING_PLUGINS:
                if plugin.plugin_name == name:
                    settings_dict[name] = plugin.get_settings()
                    break
                
        elif name not in [plugin.plugin_name for plugin in RUNNING_PLUGINS]:
            settings_dict[name] = settings.build()
        
        else:
            settings_dict[name] = None
            
    variables.IS_UI_UPDATING = False
    return settings_dict

def get_state(plugin: str):
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == plugin:
            return plugin.state
    return None

def get_states():
    states = {}
    for plugin in RUNNING_PLUGINS:
        states[plugin.plugin_name] = plugin.state
    return states

def get_performance(plugin: str):
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == plugin:
            return plugin.get_performance()
    return None

def get_performances():
    performances = {}
    for plugin in RUNNING_PLUGINS:
        performances[plugin.plugin_name] = plugin.get_performance()
    return performances

def get_latest_frametimes():
    dict = {}
    for plugin in RUNNING_PLUGINS:
        dict[plugin.plugin_name] = plugin.get_performance()[-1]
        
    return dict

def get_latest_frametime(plugin_name: str):
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == plugin_name:
            performances = plugin.get_performance()
            if len(performances) > 0:
                return performances[-1]
            return 0
    return 0

def get_main_process_mem_usages():
    total = 0
    python = 0
    node = 0
    for proc in psutil.process_iter():
        try:
            if "python" in proc.name().lower(): # backend
                total += proc.memory_percent()
                python += proc.memory_percent()
            if "node" in proc.name().lower():   # frontend
                total += proc.memory_percent()
                node += proc.memory_percent()
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return {
        "total": total,
        "python": python,
        "node": node,
        "free": psutil.virtual_memory().available / psutil.virtual_memory().total * 100,
        "other": psutil.virtual_memory().used / psutil.virtual_memory().total * 100 - total,
        "capacity": psutil.virtual_memory().total
    }

def get_statistics():
    main = get_main_process_mem_usages()
    stats = {
        "global": main,
        "plugins": {}
    }
    for plugin in RUNNING_PLUGINS:
        stats["plugins"][plugin.plugin_name] = plugin.statistics
        
    return stats

def get_tag_list():
    tags = []
    for plugin in RUNNING_PLUGINS:
        try:
            tags += plugin.tags.keys()
        except:
            pass
    return tags

def get_all_tag_data():
    tag_dict = {}
    for plugin in RUNNING_PLUGINS:
        tag_dict[plugin.plugin_name] = plugin.tags
    return tag_dict

def get_tag_data(tag: str):
    tag_dict = {}
    for plugin in RUNNING_PLUGINS:
        if tag in plugin.tags:
            tag_dict[plugin.plugin_name] = plugin.tags[tag]
    return tag_dict

def call_event(event: str, args: list, kwargs: dict, called_from: str = ""):
    if type(args) != list:
        args = [args]
    if type(kwargs) != dict:
        kwargs = {}
    for plugin in RUNNING_PLUGINS:
        if plugin.plugin_name == called_from:
            continue
        try:
            plugin.event_queue.put({
                "name": event,
                "args": args,
                "kwargs": kwargs
            })
        except:
            logging.exception("Error in event call.")

def get_all_process_pids():
    pids = {}
    for plugin in RUNNING_PLUGINS:
        pids[plugin.plugin_name] = plugin.process.pid
    return pids

def run():
    global AVAILABLE_PLUGINS
    AVAILABLE_PLUGINS = find_plugins()
    logging.info(f"Discovered {len(AVAILABLE_PLUGINS)} plugins, of which {len([plugin for plugin in AVAILABLE_PLUGINS if plugin[3] is not None])} have settings menus.")