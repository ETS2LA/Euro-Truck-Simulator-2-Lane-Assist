import json
import os
import logging
import time
import random

def WaitUntilLock(plugin):
    """Will wait until the lock file is removed from the plugin folder.

    Args:
        plugin (str): Plugin name to wait for.
    """
    
    # Wait until the lock file is removed
    while True:
        time.sleep(random.uniform(0, 0.2))
        if not os.path.exists("ETS2LA/plugins/" + plugin + "/lock"):
            break
    
def CreateLock(plugin):
    """Will create a lock file in the plugin folder.

    Args:
        plugin (str): Plugin name to create the lock file for.
    """
    
    # Create the lock file
    with open("ETS2LA/plugins/" + plugin + "/lock", 'w') as f:
        f.write("lock")
        pass
    
def RemoveLock(plugin):
    """Will remove the lock file from the plugin folder.

    Args:
        plugin (str): Plugin name to remove the lock file from.
    """
    
    # Remove the lock file
    if os.path.exists("ETS2LA/plugins/" + plugin + "/lock"):
        os.remove("ETS2LA/plugins/" + plugin + "/lock")

def GetJSON(plugin):
    """Will get the settings for the plugin provided as a JSON object.

    Args:
        plugin (str): Plugin name to get the settings from.

    Returns:
        dict: JSON object of the settings.
    """
    
    # Check that the file exists
    filename = "ETS2LA/plugins/" + plugin + "/settings.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f, indent=4)
            return {}
    
    try:
        with open(filename) as f:
            return json.load(f)
            
    except Exception as e:
        print(e)
        return {}

def Get(plugin, key, default=None):
    """Will get the settings for the plugin and key provided. If the key is not found, it will return the default value provided.

    Args:
        plugin (str): Plugin name to get the settings from.
        key (str): The key to get the value from.
        default (any, optional): Default value if data has not yet been set. Defaults to None.

    Returns:
        any: Value of the key.
    """
    
    # Check that the file exists
    filename = "ETS2LA/plugins/" + plugin + "/settings.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f, indent=4)
            return default
    
    try:
        with open(filename) as f:
            data = json.load(f)
            if key in data:
                return data[key]
            else:
                return Set(plugin, key, default)
            
    except Exception as e:
        print(e)
        return None

def Set(plugin, key, value):
    """Will set the settings for the plugin and key provided.

    Args:
        plugin (str): Plugin name to set the settings for.
        key (str): Key of the value to set.
        value (any): Value to set the key to.

    Returns:
        any: The value of the key after setting it, None if failed.
    """
    # Check that the file exists
    WaitUntilLock(plugin)
    CreateLock(plugin)
    filename = "ETS2LA/plugins/" + plugin + "/settings.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f, indent=4)
    try:
        with open("ETS2LA/plugins/" + plugin + "/settings.json") as f:
            data = json.load(f)
            data[key] = value
            with open("ETS2LA/plugins/" + plugin + "/settings.json", 'w') as f:
                json.dump(data, f, indent=4)
                
            RemoveLock(plugin)
            return data[key]
                
    except Exception as e:
        print(e)
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
    t = threading.Thread(target=listen, args=("ETS2LA/plugins/" + plugin + "/settings.json", callback))
    t.daemon = True
    t.start()