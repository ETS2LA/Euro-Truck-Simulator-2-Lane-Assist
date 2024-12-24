import logging
import random
import time
import json
import os

def GetFilename(plugin):
    if "/" in plugin or "\\" in plugin:
        filename = plugin
    elif plugin == "global" or plugin == "Global":
        filename = "ETS2LA/global.json"
    elif plugin == "global_settings":
        filename = "ETS2LA/global_settings.json"
    else: 
        filename = "Plugins/" + plugin + "/settings.json"
    
    return filename

def CreateIfNotExists(plugin):
    """Will check if the settings file exists for the plugin provided.

    Args:
        plugin (str): Plugin name to check for.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    
    # Check if the file exists
    filename = GetFilename(plugin)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f, indent=4)
            return False
    if open(filename, "r").read().replace("\n", "").strip() == "":
        with open(filename, 'w') as f:
            json.dump({}, f, indent=4)
            return False
    return True

def WaitUntilLock(plugin):
    """Will wait until the lock file is removed from the plugin folder.

    Args:
        plugin (str): Plugin name to wait for.
    """
    
    # Wait until the lock file is removed
    filename = GetFilename(plugin).split(".json")[0] + ".lock"
    while True:
        time.sleep(random.uniform(0, 0.2))
        if not os.path.exists(filename):
            break
    
def CreateLock(plugin):
    """Will create a lock file in the plugin folder.

    Args:
        plugin (str): Plugin name to create the lock file for.
    """
    
    # Create the lock file
    filename = GetFilename(plugin).split(".json")[0] + ".lock"
        
    with open(filename, 'w') as f:
        f.write("lock")
        pass
    
def RemoveLock(plugin):
    """Will remove the lock file from the plugin folder.

    Args:
        plugin (str): Plugin name to remove the lock file from.
    """
    
    # Remove the lock file
    filename = GetFilename(plugin).split(".json")[0] + ".lock"
        
    if os.path.exists(filename):
        os.remove(filename)

def GetJSON(plugin, filename=None):
    """Will get the settings for the plugin provided as a JSON object.

    Args:
        plugin (str): Plugin name to get the settings from.

    Returns:
        dict: JSON object of the settings.
    """
    
    # Check that the file exists
    filename = GetFilename(plugin)
    CreateIfNotExists(plugin)
    try:
        with open(filename) as f:
            return json.load(f)
            
    except Exception as e:
        print(e)
        return {}

def Get(plugin, key, default=None):
    """Will get the settings for the plugin and key provided. If the key is not found, it will return the default value provided.

    Args:
        plugin (str): Plugin name to get the settings from. Alternatively, the full path to the settings file.
        key (str): The key to get the value from.
        default (any, optional): Default value if data has not yet been set. Defaults to None.

    Returns:
        any: Value of the key.
    """
    
    # Check that the file exists
    filename = GetFilename(plugin)
    CreateIfNotExists(plugin)
    try:
        if type(key) != list:
            with open(filename) as f:
                data = json.load(f)
                if key in data:
                    return data[key]
                else:
                    return Set(plugin, key, default)
        else:
            with open(filename) as f:
                data = json.load(f)
                try:
                    for k in key:
                        data = data[k]
                    return data
                except Exception as e:
                    try:
                        success = Set(plugin, key, default)
                        if success == "success":
                            return default
                        else:
                            return None
                    except:
                        return None
                return None
        
    except Exception as e:
        logging.error(e)
        return None

from functools import reduce
from operator import getitem
# https://stackoverflow.com/a/70377616
def set_nested_item(dataDict, mapList, val):
    """Set item in nested dictionary"""
    current_dict = dataDict
    for key in mapList[:-1]:
        current_dict = current_dict.setdefault(key, {})
    current_dict[mapList[-1]] = val
    return dataDict
            

def Set(plugin, key, value):
    """Will set the settings for the plugin and key provided.

    Args:
        plugin (str): Plugin name to set the settings for. Alternatively, the full path to the settings file.
        key (str): Key of the value to set.
        value (any): Value to set the key to.

    Returns:
        any: The value of the key after setting it, None if failed.
    """
    # Check that the file exists
    WaitUntilLock(plugin)
    CreateLock(plugin)
    
    filename = GetFilename(plugin)
    CreateIfNotExists(plugin)
    try:
        if type(key) != list:
            with open(filename) as f:
                data = json.load(f)
                data[key] = value
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                    
                RemoveLock(plugin)
                return data[key]
        else:
            with open(filename) as f:
                data = json.load(f)
                data = set_nested_item(data, key, value)
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                    
                RemoveLock(plugin)
                return "success"
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        RemoveLock(plugin)
        return None
    
def Listen(plugin, callback):
    """Will listen the settings file for changes and call the callback function when any of the settings change.

    Args:
        plugin (str): Plugin name to listen for changes.
        callback (function): The function to call with the changed file.
    """
    
    # Run a new thread to listen for changes
    def listen(filepath, callback):
        import time
        last_change = os.path.getmtime(filepath)
        while True:
            time.sleep(1)
            if os.path.getmtime(filepath) != last_change:
                last_change = os.path.getmtime(filepath)
                settings = GetJSON(plugin)
                try:
                    callback(settings)
                except:
                    logging.warning("Callback function doesn't accept the JSON data as an argument.")
                    try:
                        callback()
                    except:
                        logging.error("Callback function call unsuccessful.")
                
    import threading
    t = threading.Thread(target=listen, args=(GetFilename(plugin), callback))
    t.daemon = True
    t.start()