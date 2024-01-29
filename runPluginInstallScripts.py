"""This file is mainly used to easily run all plugin install scripts with github actions."""

# Find all folders in plugins/
# Run install.py (install function) in each folder
import os
import sys
import importlib.util

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
        install.install()