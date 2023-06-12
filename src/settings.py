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

def ChangeProfile(profileName):
    with open(r"profiles\currentProfile.txt", "w") as f:
        f.truncate(0)
        f.write(profileName)

# Change settings in the json file
def UpdateSettings(category, name, data):
    profile = open(r"profiles\currentProfile.txt", "r").readline().replace("\n", "")
    with open(profile, "r") as f:
        settings = json.load(f)

    settings[category][name] = data
    with open(profile, "w") as f:
        f.truncate(0)
        json.dump(settings, f, indent=6)

# Get a specific setting
def GetSettings(category, name):
    profile = open(r"profiles\currentProfile.txt", "r").readline().replace("\n", "")
    with open(profile, "r") as f:
        settings = json.load(f)
    return settings[category][name]


# Create a new setting
def CreateSettings(category, name, data):
    profile = open(r"profiles\currentProfile.txt", "r").readline().replace("\n", "")
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
        