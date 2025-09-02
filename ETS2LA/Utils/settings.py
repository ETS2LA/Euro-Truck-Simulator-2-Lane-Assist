"""This file is used by the backend and pages.
Plugins should use self.settings for a more reliable way with less of a chance
for a race condition to occur.

Basically if you would be sending anything other than "global" as the plugin
name, then you should probably use self.settings instead.
"""

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
        with open(filename, "w") as f:
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
    if not os.path.exists(filename):
        CreateLock(plugin)
        return

    while True:
        if not os.path.exists(filename):
            break

        # Check if the lock file is too old (10s)
        if os.path.getmtime(filename) + 10 < time.time():
            logging.warning(f"Lock file for {plugin} is too old. Removing it.")
            RemoveLock(plugin)
            break

        time.sleep(random.uniform(0, 0.1))

    CreateLock(plugin)


def CreateLock(plugin):
    """Will create a lock file in the plugin folder.

    Args:
        plugin (str): Plugin name to create the lock file for.

    """
    # Create the lock file
    filename = GetFilename(plugin).split(".json")[0] + ".lock"
    with open(filename, "w") as f:
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
        if not isinstance(key, list):
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
                except Exception:
                    try:
                        success = Set(plugin, key, default)
                        if success == "success":
                            return default
                        else:
                            return None
                    except Exception:
                        return None
                return None

    except Exception:
        logging.error(
            f"Error while reading [yellow]{filename}[/yellow]. It is possible the file is corrupted. You should delete it and try again."
        )
        return None


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
    WaitUntilLock(plugin)
    filename = GetFilename(plugin)
    CreateIfNotExists(plugin)
    try:
        if not isinstance(key, list):
            with open(filename) as f:
                data = json.load(f)
                data[key] = value
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

                RemoveLock(plugin)
                return data[key]
        else:
            with open(filename) as f:
                data = json.load(f)
                data = set_nested_item(data, key, value)
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

                RemoveLock(plugin)
                return "success"

    except Exception:
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
                except Exception:
                    logging.warning(
                        f"Callback function {callback.__name__} doesn't accept the JSON data as an argument."
                    )
                    try:
                        callback()
                    except Exception:
                        logging.exception("Callback function call unsuccessful.")

    import threading

    t = threading.Thread(
        target=listen, args=(GetFilename(plugin), callback), daemon=True
    )
    t.daemon = True
    t.start()
