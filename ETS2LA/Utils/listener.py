"""
ETS2LA's change listener. This file will listen for file changes accross all
main ETS2LA backend files when in development mode.
"""

from ETS2LA import variables
import importlib
import logging
import os

ignore = ["webserver.py", "listener.py", "core.py"]

def discover_files(path):
    """Recursively discover all .py files in the given path."""
    py_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                if file not in ignore:
                    py_files.append(os.path.join(root, file))
                    
    logging.info(f"Discovered {len(py_files)} files, listening for changes.")
    return py_files

if variables.DEVELOPMENT_MODE:       
    files = discover_files("ETS2LA")
    state = {file: os.path.getmtime(file) for file in files}

def check_for_changes():
    """Check for changes in the files and reload the modules if any changes are detected."""
    global state
    for file in files:
        current_mtime = os.path.getmtime(file)
        if file not in state or state[file] != current_mtime:
            logging.warning(f"Reloading [dim]{file}[/dim] due to changes.")
            module_name = "ETS2LA." + os.path.relpath(file, "ETS2LA").replace(os.sep, ".")[:-3]
            module = importlib.reload(importlib.import_module(module_name))
            state[file] = current_mtime
            try:
                module.on_reload()
            except: pass