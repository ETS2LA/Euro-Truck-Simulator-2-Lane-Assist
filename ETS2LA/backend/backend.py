import multiprocessing
import ETS2LA.frontend.immediate as immediate
from ETS2LA.plugins.runner import PluginRunner
import threading
import time
import json
import requests
import sys
import logging
import psutil
import os

global commits_save
commits_save = []

class PluginRunnerController():
    def __init__(self, pluginName, temporary=False):
        # Initialize the plugin runner
        global runners
        runners[pluginName] = self # So that we can access this runner later from the main thread or other runners.
        self.pluginName = pluginName
        # Make the queue (comms) and start the process.
        self.queue = multiprocessing.JoinableQueue()
        self.functionQueue = multiprocessing.JoinableQueue()
        self.eventQueue = multiprocessing.JoinableQueue()
        self.immediateQueue = multiprocessing.JoinableQueue()
        self.runner = multiprocessing.Process(target=PluginRunner, args=(pluginName, temporary, self.queue, self.functionQueue, self.eventQueue, self.immediateQueue, ), daemon=True)
        self.runner.start()
        self.process = self.runner.pid
        self.process_info = {
            "cpu": 0,
            "mem": 0,
            "disk": 0
        }
        self.run()
    
    def immediateQueueThread(self):
        while True:
            try: data = self.immediateQueue.get(timeout=0.5) # Get the data returned from the plugin runner.
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None): # If the data is None, then we just skip this iteration.
                time.sleep(0.00001)
                continue
        
            if "sonner" in data:
                sonnerType = data["sonner"]["type"]
                sonnerText = data["sonner"]["text"]
                sonnerPromise = data["sonner"]["promise"]
                immediate.sonner(sonnerText, sonnerType, sonnerPromise)
        
    def monitor(self):
        process = psutil.Process(self.process)
        # Get the plugin folder size
        try:
            size = 0
            for root, dirs, files in os.walk(f"ETS2LA/plugins/{self.pluginName}"):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
                size += sum([os.path.getsize(os.path.join(root, name)) for name in dirs])
            
            self.process_info["disk"] = size
            logging.info(f"Plugin {self.pluginName} has a disk usage of {size} bytes.")
        except:
            import traceback
            traceback.print_exc()
            self.process_info["disk"] = 0
            
        while True:
            try:
                self.process_info["cpu"] = process.cpu_percent(interval=0.1) / psutil.cpu_count()
                self.process_info["mem"] = process.memory_percent()
                time.sleep(0.1)
                logging.debug(f"Plugin {self.pluginName} CPU: {self.process_info['cpu']} MEM: {self.process_info['mem']}")
            except:
                time.sleep(0.1)
                continue
        
    def run(self):
        global frameTimes
        threading.Thread(target=self.immediateQueueThread, daemon=True).start()
        threading.Thread(target=self.monitor, daemon=True).start()
        while True:
            try: data = self.queue.get(timeout=0.5) # Get the data returned from the plugin runner.
            except Exception as e: 
                time.sleep(0.00001)
                continue
            
            if type(data) == type(None): # If the data is None, then we just skip this iteration.
                time.sleep(0.00001)
                continue
            
            if "function" in data:
                # Send the data back to wait for the answer.
                self.queue.put(self.lastData)
                time.sleep(0.01)
                continue
            
            if type(data) != dict: # If the data is not a dictionary, we can assume it's return data, instead of a command.
                self.lastData = data
                continue
            
            if "frametimes" in data: # Save the frame times
                frametime = data["frametimes"]
                if self.pluginName not in frameTimes:
                    frameTimes[self.pluginName] = []
                frameTimes[self.pluginName].append(frametime[self.pluginName])
                if len(frameTimes[self.pluginName]) > 120: # 60 seconds of 0.5 intervals
                    frameTimes[self.pluginName].pop(0)
                    
            elif "get" in data: # If the data is a get command, then we need to get the data from another plugin.
                plugins = data["get"]
                for plugin in plugins:
                    if plugin in runners:
                        self.queue.put(runners[plugin].lastData)
                    else:
                        self.queue.put(None)
            else:
                    self.lastData = data
        
        
runners = {}
frameTimes = {}

AVAILABLE_PLUGINS = {}
def GetAvailablePlugins():
    global AVAILABLE_PLUGINS
    import os
    # Get list of everything in the plugins folder
    plugins = os.listdir("ETS2LA/plugins")
    # Check if it's a folder or a file.
    for plugin in plugins:
        if os.path.isdir(f"ETS2LA/plugins/{plugin}"):
            AVAILABLE_PLUGINS[plugin] = {}
    # Remove the pycache folder.
    AVAILABLE_PLUGINS.pop("__pycache__")
    # Add the plugins.json file contents to AVAILABLE_PLUGINS[plugin][file]
    for plugin in AVAILABLE_PLUGINS:
        try:
            with open(f"ETS2LA/plugins/{plugin}/plugin.json", "r") as f:
                AVAILABLE_PLUGINS[plugin]["file"] = json.loads(f.read())
        except:
            AVAILABLE_PLUGINS[plugin]["file"] = {
                "name": plugin,
                "authors": "Unknown",
                "version": "Unknown",
                "description": "No description provided.",
                "image": "None",
                "dependencies": "None"
            }
        
    # Return
    return AVAILABLE_PLUGINS

ENABLED_PLUGINS = []
def GetEnabledPlugins():
    global ENABLED_PLUGINS
    ENABLED_PLUGINS = []
    for runner in runners:
        ENABLED_PLUGINS.append(runner)
        
    return ENABLED_PLUGINS
    
def CallPluginFunction(plugin, function, args, kwargs):
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
        kwargs.pop("timeout")
    else:
        timeout = 5
    try:
        if plugin in runners:
            runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
            # Wait for the answer
            startTime = time.time()
            while time.time() - startTime < timeout:
                try: data = runners[plugin].functionQueue.get()
                except: 
                    logging.error(f"Plugin {plugin} crashed while running function {function}, please check it's logs.")
                    return False
                if data == {"function": function, "args": args, "kwargs": kwargs}:
                    runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
                    time.sleep(0.01)
                else:
                    return data
            return True
        else:
            logging.info(f"Plugin {plugin} is not enabled. Enabling temporarily to run the function.")
            AddPluginRunner(plugin, temporary=True) # Add a temp runner to load the code
            time.sleep(0.5)
            runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
            # Wait for the answer
            startTime = time.time()
            while time.time() - startTime < timeout:
                if plugin in runners:
                    try: data = runners[plugin].functionQueue.get()
                    except:
                        RemovePluginRunner(plugin)
                        logging.error(f"Plugin {plugin} crashed while running function {function}, please check it's logs.")
                        return False
                    if data == {"function": function, "args": args, "kwargs": kwargs}:
                        runners[plugin].functionQueue.put({"function": function, "args": args, "kwargs": kwargs})
                        time.sleep(0.01)
                    else:            
                        RemovePluginRunner(plugin)
                        logging.info(f"Plugin {plugin} removed after running function and returning data.")
                        return data
                else:
                    time.sleep(0.01)
            
            RemovePluginRunner(plugin)
            logging.info(f"Plugin {plugin} removed after running function and hitting timeout.")
            return True
    except:
        import traceback
        traceback.print_exc()
        return False
    
def CallEvent(event, args, kwargs):
    for runner in runners:
        try:
            runners[runner].eventQueue.put({"event": event, "args": args, "kwargs": kwargs})
        except:
            import traceback
            traceback.print_exc()
            pass

def AddPluginRunner(pluginName, temporary=False):
    if pluginName in runners:
        return
    # Run the plugin runner in a separate thread. This is done to avoid blocking the main thread.
    runner = threading.Thread(target=PluginRunnerController, args=(pluginName, temporary, ), daemon=True)
    runner.start()

def RemovePluginRunner(pluginName):
    if not pluginName in runners:
        return
    # Stop the plugin runner
    runners[pluginName].runner.terminate()
    runners.pop(pluginName)

def GetGitHistory():
    global commits_save
    try:
        # If the git history has already been retrieved, then return that instead of searching again
        if commits_save == []:
            # Vars
            api_requests = 0
            commits = []
            authors = {}

            # Get the git history as json
            import git
            repo = git.Repo(search_parent_directories=True)
            
            for commit in repo.iter_commits():
                # Add the commit to the list
                commits.append({
                    "author": commit.author.name,
                    "message": commit.message,
                    "time": commit.committed_date
                })
            
            count = len(commits)
            index = 0
            for commit in commits:
                if index <= 100: # Only get images for the first 100 commits
                    if not commit["author"] in authors:
                        if commit["author"] == "DylDev": # Hardcded because of usernames
                            url = f"https://api.github.com/users/DylDevs"
                        else:
                            url = f"https://api.github.com/users/{commit['author']}"
                        # Get the avatar url from the GitHub API
                        try:
                            response = requests.get(url, timeout=6)
                            success = True
                        except:
                            success = False
                            print(f"Github API request was unsuccessful for author: {commit['author']}. (Timed out)")
                            continue

                        if success:
                            api_requests += 1
                            if response.status_code == 200:
                                data = response.json()
                                avatar_url = data["avatar_url"]
                                authors[commit["author"]] = avatar_url
                            else:
                                authors[commit["author"]] = "https://github.com/favicon.ico"
                        else:
                            authors[commit["author"]] = "https://github.com/favicon.ico"
                    else:
                        pass
                    
                    commit["picture"] = authors[commit["author"]]
                
                index += 1

            commits_save = commits
            return commits
        else:
            return commits_save
    except:
        import traceback
        traceback.print_exc()
        return []

# These are run on startup.
GetAvailablePlugins()