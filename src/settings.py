'''
Settings interface


ChangeProfile(profileName)
- Profilename is a string with the current .json file name
    
    >>> ChangeProfile("default.json")


UpdateSettings(category, name, data)
- Category is a string with the category name
- Name is a string with the setting name
- Data is the data to be written to the setting
    
    >>> UpdateSettings("General", "ShowFPS", True)


GetSettings(category, name)
- Category is a string with the category name
- Name is a string with the setting name
    
    >>> GetSettings("General", "ShowFPS")
    
CreateSettings(category, name, data)
- Category is a string with the category name
- Name is a string with the setting name
- Data is the data to be written to the setting
! In case the setting already exists, it will be overwritten with UpdateSettings()

    >>> CreateSettings("Controller", "IndicateRight", 3)
'''

import json
from src.logger import print
from src.variables import PATH
import os

if os.name == "nt":
    currentProfile = r"profiles\currentProfile.txt"
else:
    currentProfile = "profiles/currentProfile.txt"

if open(currentProfile, "r").readline().replace("\n", "") == "":
    with open(currentProfile, "w") as f:
        f.write("profiles/settings.json")
    print("Profile variable was empty, set it to settings.json")

def EnsureFile(file):
    try:
        with open(file, "r") as f:
            pass
    except:
        with open(file, "w") as f:
            f.write("{}")

def ChangeProfile():
    global currentProfile
    
    from tkinter import filedialog
    file = filedialog.askopenfilename(initialdir=PATH+"\\profiles", title="Select a profile", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
    with open(currentProfile, "w") as f:
        f.truncate(0)
        f.write(file)
    
    import src.variables
    src.variables.RELOAD = True

def CreateProfile():
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
        ChangeProfile(filePath)
    
    except Exception as ex:
        print(ex.args)
        print("Failed to create profile")

# Change settings in the json file
def UpdateSettings(category, name, data):
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
def GetSettings(category, name, value=None):
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)
        return settings[category][name]
    except Exception as ex:
        if value != None:
            CreateSettings(category, name, value)
            return value
        else:
            print(ex.args)


# Create a new setting
def CreateSettings(category, name, data):
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
        
def AddToList(category, name, data):
    try:
        profile = open(currentProfile, "r").readline().replace("\n", "")
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

        # If the setting doesn't exist then create it 
        if not category in settings:
            settings[category] = {}
            settings[category][name] = []
            settings[category][name].append(data)
        
        # If the setting exists then overwrite it
        if category in settings:
            settings[category][name].append(data)
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except Exception as ex:
        print(ex.args)
        

def RemoveFromList(category, name, data):
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
        