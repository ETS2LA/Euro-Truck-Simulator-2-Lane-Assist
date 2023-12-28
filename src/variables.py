'''
Stores all main variables for the program.
'''
import os


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

def ToggleEnable():
    """Will toggle the mainloop.
    """
    global ENABLELOOP
    ENABLELOOP = not ENABLELOOP

def UpdatePlugins():
    """Will prompt the application to update it's list of plugins."""
    global UPDATEPLUGINS
    UPDATEPLUGINS = True