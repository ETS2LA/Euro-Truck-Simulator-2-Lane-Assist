"""This file is mainly used to easily run all plugin install scripts with github actions."""

# Install requirements from requirements.txt one by one
import os
import sys
import importlib.util
file = open("requirements.txt", "r")
for line in file:
    try:
        os.system(f"pip install {line}")
    except:
        print(f"Failed to install {line}")

# Find all folders in plugins/
# Run install.py (install function) in each folder

# Get the path to the plugins folder
pluginsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

# Get all folders in the plugins folder
plugins = [f.path for f in os.scandir(pluginsPath) if f.is_dir()]
for plugin in plugins:
    # Get the install.py file in each folder
    installPath = os.path.join(plugin, "install.py")
    if os.path.exists(installPath):
        # Import the install.py file
        spec = importlib.util.spec_from_file_location("install", installPath)
        install = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(install)
        # Run the install function
        print(f"Running install script for {plugin}")
        try:
            install.install()
        except:
            print(f"Failed to run install script for {plugin}")
            print(sys.exc_info()[0])