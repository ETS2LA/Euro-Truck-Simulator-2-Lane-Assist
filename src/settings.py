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
from src.variables import PATH
import os

currentProfile = ""
"""The currently selected profile (filename)."""

if os.name == "nt":
    currentProfile = r"profiles\currentProfile.txt"
else:
    currentProfile = "profiles/currentProfile.txt"

if open(currentProfile, "r").readline().replace("\n", "") == "":
    with open(currentProfile, "w") as f:
        f.write("profiles/settings.json")
    print("Profile variable was empty, set it to settings.json")

def EnsureFile(file:str):
    """Will check if a file exists and create it if it doesn't.

    Args:
        file (str): Filename.
    """
    try:
        with open(file, "r") as f:
            pass
    except:
        with open(file, "w") as f:
            f.write("{}")

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
        # Copy the current profile
        profile = open(currentProfile, "r").readline().replace("\n", "")
            
        with open(profile, "r") as f:
            data = json.load(f)
        
        newFile.truncate(0)
        json.dump(data, newFile, indent=6)
            
        filePath = newFile.name
        
        newFile.close()
            
        # Change the current profile
        # ChangeProfile(filePath)
    
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
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

        settings[category][name] = data
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except Exception as ex:
        print(ex.args)

# Get a specific setting
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
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)
        
        if settings[category][name] == None:
            return value    
        
        return settings[category][name]
    except Exception as ex:
        if value != None:
            CreateSettings(category, name, value)
            return value
        else:
            print(ex.args)


# Create a new setting
def CreateSettings(category:str, name:str, data:any):
    """Will create a new setting in the settings file.

    Args:
        category (str): Json category.
        name (str): Json setting name.
        data (_type_): Data to write.
    """
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

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
    except Exception as ex:
        print(ex.args)
        
def AddToList(category:str, name:str, data:any, exclusive:bool=False):
    """Will add a new item to a list in the settings file.

    Args:
        category (str): Json category.
        name (str): Json list name.
        data (str): Data to add to the list.
        exclusive (bool, optional): Whether to allow adding multiple instances of the same data. Defaults to False.
    """
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

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
    except Exception as ex:
        print(ex.args)
        

def RemoveFromList(category:str, name:str, data:any):
    """Remove an item from a list in the settings file.

    Args:
        category (str): Json category.
        name (str): Json list name.
        data (_type_): Data to remove from the list.
    """
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

        # If the setting doesn't exist then don't do anything 
        if not category in settings:
            return
        
        # If the setting exists then overwrite it
        if category in settings:
            settings[category][name].remove(data)
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
        
    except Exception as ex:
        print(ex.args)
        