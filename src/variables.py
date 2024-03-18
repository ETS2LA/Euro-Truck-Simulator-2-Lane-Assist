'''
Stores all global variables for the program.
'''
import os
import subprocess
import ctypes
import sys

#region Variables
PATH = os.path.dirname(__file__).replace("src", "")
"""The current absolute path to the root of the program."""
ENABLELOOP = False
"""Whether or not the mainloop is enabled."""
UPDATEPLUGINS = False
"""Whether to update the list of plugins at the start of the next frame."""
RELOAD = False
"""Whether to reload the program at the start of the next frame."""
VERSION = open(PATH + "version.txt", "r").read().replace("\n", "")
"""Current version of the program."""
CHANGELOG = open(PATH + "changelog.txt", "r").readlines()
"""The current shortened changelog. Used to show the user what's new in the small autoupdater dialog."""
CONSOLENAME = None
"""The name of the console, it is needed to hide or show the console."""
CONSOLEHWND = None
"""The hwnd of the console, it is needed to hide or show the console."""
APPENDDATANEXTFRAME = None
"""Add custom data for the next frame. This is usually useful for panels that can't add their data the normal way.
Should be used sparingly, since it only supports one piece of data at a time (for the one open panel / UI)."""
RELOADPLUGINS = False
"""Will fully reload the plugin code for all plugins. This is useful for debugging and development."""
USERNAME = os.getlogin()
"""The username of the current windows user."""
ETS2DOCUMENTSPATH = "C:/Users/" + USERNAME + "/Documents/Euro Truck Simulator 2/"
"""Path to the ETS2 documents folder. Contains stuff like the mod folder and log files."""
OS = os.name
"""The current operating system."""
LASTUPDATE = None
"""The date of the last update to the local git repo."""
UPDATEAVAILABLE = False
"""Will be set to the updated version by the mainloop if an update is available and it's ignored."""
WINDOWSCALING = ctypes.windll.shcore.GetScaleFactorForDevice(0)
"""The current scaling of windows."""
FRAMECOUNTER = 0
"""The amount of frames that have passed since the program started."""
WIKI_URL = "https://wiki.tumppi066.fi"
"""The url that will show when the wiki panel is opened"""
IN_VENV = sys.prefix != sys.base_prefix
"""Whether the program is running in a virtual environment or not."""
#endregion

#region Var Set Functions

try:
    try:
        LASTUPDATE = subprocess.check_output("git log -1 --date=local --format=%cd", shell=True).decode("utf-8").replace("\n", "")
    except:
        # Git is probably notifying us of the root folder being owned by admin
        unixPath = PATH.replace("\\", "/")
        if unixPath[-1] == "/":
            unixPath = unixPath[:-1]
            
        os.system(f'cmd /k "cd {PATH} & git config --global --add safe.directory {unixPath} & exit"')

        LASTUPDATE = subprocess.check_output("git log -1 --date=local --format=%cd", shell=True).decode("utf-8").replace("\n", "")
        
except:
    LASTUPDATE = "Unknown"
#endregion

#region Functions

def ToggleEnable():
    """Will toggle the mainloop.
    """
    global ENABLELOOP
    ENABLELOOP = not ENABLELOOP

def UpdatePlugins():
    """Will prompt the application to update it's list of plugins."""
    global UPDATEPLUGINS
    UPDATEPLUGINS = True
    
def ReloadAllPlugins():
    """Will prompt the application to reload all plugins."""
    global RELOADPLUGINS
    RELOADPLUGINS = True
    
#endregion
