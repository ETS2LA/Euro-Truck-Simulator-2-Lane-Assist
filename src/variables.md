---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: code-square
---

!!!warning Warning
This page is meant for `developers`
!!!

## Directly usable functions and values
```python
from src.variables import *

"""The current absolute path to the root of the program."""
PATH:str
"""Whether or not the mainloop is enabled."""
ENABLELOOP:bool
"""Whether to update the list of plugins at the start of the next frame."""
UPDATEPLUGINS:bool
"""Whether to reload the program at the start of the next frame."""
RELOAD:bool
"""Current version of the program."""
VERSION:str
"""The current shortened changelog. Used to show the user what's new in the small autoupdater dialog."""
CHANGELOG:str
"""The name of the console, it is needed to hide or show the console."""
CONSOLENAME = None
"""The hwnd of the console, it is needed to hide or show the console."""
CONSOLEHWND = None
"""Add custom data for the next frame. This is usually useful for panels that can't add their data the normal way.
Should be used sparingly, since it only supports one piece of data at a time (for the one open panel / UI)."""
APPENDDATANEXTFRAME:bool
"""Will fully reload the plugin code for all plugins. This is useful for debugging and development."""
RELOADPLUGINS:bool
"""The username of the current windows user."""
USERNAME:str
"""Path to the ETS2 documents folder. Contains stuff like the mod folder and log files."""
ETS2DOCUMENTSPATH:str
"""The current operating system."""
OS:str
"""The date of the last update to the local git repo."""
LASTUPDATE:bool
"""Will be set to the updated version by the mainloop if an update is available and it's ignored."""
UPDATEAVAILABLE:bool/str
"""The current scaling of windows. (100, 125, 150, etc...)"""
WINDOWSCALING:int
```

## Description
Stores all important global variables for the app in one place.