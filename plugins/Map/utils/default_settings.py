"""Default settings management for the Map plugin."""
import os
import json
from pathlib import Path

DEFAULT_SETTINGS = {
    "enabled_dlcs": [],  # Base game only by default
    "dlc_guards": {
        "going_east": 1,
        "scandinavia": 2,
        "france": 3,
        "italia": 4,
        "baltic": 5,
        "black_sea": 6,
        "iberia": 7,
        "russia": 8
    }
}

def ensure_settings_file(settings_path):
    """Create default settings file if it doesn't exist."""
    if not os.path.exists(settings_path):
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    return settings_path

def get_settings_path():
    """Get the path to the global settings file."""
    # Check common locations
    possible_paths = [
        os.path.expanduser("~/Documents/ETS2LA/global_settings.json"),
        os.path.expanduser("~/ETS2LA/global_settings.json"),
        "./global_settings.json"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If no existing file found, create in default location
    default_path = os.path.expanduser("~/Documents/ETS2LA/global_settings.json")
    return ensure_settings_file(default_path)

def load_settings():
    """Load settings, creating default if necessary."""
    try:
        settings_path = get_settings_path()
        with open(settings_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load settings, using defaults. Error: {e}")
        return DEFAULT_SETTINGS.copy()
