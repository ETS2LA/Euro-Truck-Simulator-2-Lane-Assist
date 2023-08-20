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
    global ENABLELOOP
    ENABLELOOP = not ENABLELOOP

def UpdatePlugins():
    global UPDATEPLUGINS
    UPDATEPLUGINS = True