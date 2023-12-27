'''
Stores all main variables for the program.
'''
import os


PATH = os.path.dirname(__file__).replace("src", "")
ENABLELOOP = False
UPDATEPLUGINS = False
RELOAD = False
VERSION = open(PATH + "version.txt", "r").read().replace("\n", "")
CHANGELOG = open(PATH + "changelog.txt", "r").readlines()

def ToggleEnable():
    """Will toggle the mainloop.
    """
    global ENABLELOOP
    ENABLELOOP = not ENABLELOOP

def UpdatePlugins():
    """Will prompt the application to update it's list of plugins."""
    global UPDATEPLUGINS
    UPDATEPLUGINS = True