"""
Provides an interface to read and write settings from the main JSON file.
Ideally all settings should be stored using this interface.

Main functions:
```python
# Will create (or update) a new setting in the settings file.
CreateSettings(category, name, data) 

# Will get a specific setting from the settings file.
GetSettings(category, name, value=None) 
```
"""
import json
from src.logger import print
from src.variables import PATH, FRAMECOUNTER
import os

currentProfile = ""
"""The currently selected profile (filename)."""

if os.name == "nt":
    currentProfile = r"profiles\currentProfile.txt"
else:
    currentProfile = "profiles/currentProfile.txt"

# Check that the current profile file exists
if not os.path.exists(currentProfile):
    with open(currentProfile, "w") as f:
        f.write("profiles/settings.json")
    print("Profile file didn't exist, created a new one")

if open(currentProfile, "r").readline().replace("\n", "") == "":
    with open(currentProfile, "w") as f:
        f.write("profiles/settings.json")
    print("Profile variable was empty, set it to settings.json")

profile = open(currentProfile, "r").readline().replace("\n", "")
if not os.path.exists(profile) or open(profile, "r").readline() == "":
    with open(profile, "w") as f:
        f.truncate(0)
        f.write("{}")
        f.close()
        print("Settings file didn't exist, created a new one")

settings = json.load(open(profile, "r"))
settings_file = open(profile, "w")

# Check for settings file in root folder
SETPATH = str(os.path.abspath(os.path.join(PATH, os.pardir)))
# Check that settings.json exists
if os.path.exists(os.path.join(SETPATH, "settings.json")):
    # Remove import.json from profiles if it exist
    if os.path.exists(os.path.join("profiles", "import.json")):
        os.remove(os.path.join("profiles", "import.json"))
    # Move SETPATH settings.json to profiles with the name inport.json
    os.rename(os.path.join(SETPATH, "settings.json"), os.path.join("profiles", "import.json"))
    with open(currentProfile, "w") as f:
        f.write("profiles/import.json")

def EnsureFile(file:str):
    """Will check if a file exists and create it if it doesn't.

    Args:
        file (str): Filename.
    """
    if os.path.exists(file):
        return
    with open(file, "w") as f:
        f.truncate(0)

def ChangeProfile():
    """Will change the currently selected profile and reload the app.
    """
    global currentProfile
    
    from tkinter import filedialog
    file = filedialog.askopenfilename(initialdir=PATH+"\\profiles", title="Select a profile", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
    with open(currentProfile, "w") as f:
        f.truncate(0)
        f.write(file)
    
    import src.variables
    src.variables.RELOAD = True

def CreateProfile():
    """Will create a new profile based on the current one. Will not change the current profile.
    """
    from tkinter import filedialog
    newFile = filedialog.asksaveasfile(initialdir=PATH+"\\profiles", initialfile="newProfile.json", title="Create a new profile", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
    try: 
        with open(profile, "r") as f:
            data = json.load(f)
        
        newFile.truncate(0)
        json.dump(data, newFile, indent=6)
            
        filePath = newFile.name
        
        newFile.close()

    except Exception as ex:
        print(ex.args)
        print("Failed to create profile")

# Change settings in the json file
def UpdateSettings(category:str, name:str, data:any):
    """Update a setting in the settings file.
    In case the setting doesn't exist, it will be created.

    Args:
        category (str): Json category.
        name (str): Json setting name.
        data (_type_): Data to write.
    """
    global currentFrameSettings, frameCounter
    try:
        settings[category][name] = data
        json.dump(settings, settings_file, indent=6)
            
        currentFrameSettings = settings
        frameCounter = FRAMECOUNTER
        
    except Exception as ex:
        pass

# Get a specific setting
currentFrameSettings = {}
frameCounter = -1
def GetSettings(category:str, name:str, value:any=None):
    """Will get a specific setting from the settings file.

    Args:
        category (str): Json category.
        name (str): Json setting name.
        value (_type_, optional): Default value in case the data is not found. Defaults to None.

    Returns:
        _type_: The data from the json file. (or the default value)
    """
        
    try:
        if settings[category][name] == None:
            return value    
        else:
            return settings[category][name]
    except Exception as ex:
        if value != None:
            CreateSettings(category, name, value)
            return value
        else:
            pass


# Create a new setting
def CreateSettings(category:str, name:str, data:any):
    """Will create a new setting in the settings file.

    Args:
        category (str): Json category.
        name (str): Json setting name.
        data (_type_): Data to write.
    """
    global currentFrameSettings, frameCounter
    try:
        # If the setting doesn't exist then create it 
        if not category in settings:
            settings[category] = {}
            settings[category][name] = data
        
        # If the setting exists then overwrite it
        if category in settings:
            settings[category][name] = data
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
            
        currentFrameSettings = settings
        frameCounter = FRAMECOUNTER
    except Exception as ex:
        pass
        
def AddToList(category:str, name:str, data:any, exclusive:bool=False):
    """Will add a new item to a list in the settings file.

    Args:
        category (str): Json category.
        name (str): Json list name.
        data (str): Data to add to the list.
        exclusive (bool, optional): Whether to allow adding multiple instances of the same data. Defaults to False.
    """
    global currentFrameSettings, frameCounter
    try:
        # If the setting doesn't exist then create it 
        if not category in settings:
            settings[category] = {}
            settings[category][name] = []

            # Check if the data is a list
            if isinstance(data, list):
                for item in data:
                    settings[category][name].append(item)
            else:
                settings[category][name].append(data)
        
        if not name in settings[category]:
            settings[category][name] = []
            # Check if the data is a list
            if isinstance(data, list):
                for item in data:
                    settings[category][name].append(item)
            else:
                settings[category][name].append(data)
        
        # If the setting exists then overwrite it
        if category in settings:
            # Check if the data is a list
            if isinstance(data, list):
                for item in data:
                    if exclusive:
                        if not item in settings[category][name]:
                            settings[category][name].append(item)
                    else:
                        settings[category][name].append(item)
            else:
                if exclusive:
                    if not data in settings[category][name]:
                        settings[category][name].append(data)
                else:
                    settings[category][name].append(data)
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
            
        currentFrameSettings = settings
        frameCounter = FRAMECOUNTER
    except Exception as ex:
        pass
        

def RemoveFromList(category:str, name:str, data:any):
    """Remove an item from a list in the settings file.

    Args:
        category (str): Json category.
        name (str): Json list name.
        data (_type_): Data to remove from the list.
    """
    global currentFrameSettings, frameCounter
    try:
        # If the setting doesn't exist then don't do anything 
        if not category in settings:
            return
        
        # If the setting exists then overwrite it
        if category in settings:
            settings[category][name].remove(data)
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
            
        currentFrameSettings = settings
        frameCounter = FRAMECOUNTER
        
    except Exception as ex:
        pass