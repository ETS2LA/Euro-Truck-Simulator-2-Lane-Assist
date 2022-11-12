import json


# Change settings in the json file
def UpdateSettings(category, name, data):
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings[category][name] = data
    with open("settings.json", "w") as f:
        f.truncate(0)
        json.dump(settings, f, indent=6)

# Get a specific setting
def GetSettings(category, name):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    return settings[category][name]