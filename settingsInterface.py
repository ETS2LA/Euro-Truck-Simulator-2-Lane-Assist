import json

def ChangeProfile(profileName):
    with open("currentProfile.txt", "w") as f:
        f.truncate(0)
        f.write(profileName)

# Change settings in the json file
def UpdateSettings(category, name, data):
    profile = open("currentProfile.txt", "r").readline()
    with open(profile, "r") as f:
        settings = json.load(f)

    settings[category][name] = data
    with open(profile, "w") as f:
        f.truncate(0)
        json.dump(settings, f, indent=6)

# Get a specific setting
def GetSettings(category, name):
    profile = open("currentProfile.txt", "r").readline()
    with open(profile, "r") as f:
        settings = json.load(f)
    return settings[category][name]