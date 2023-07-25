'''
Stores all main variables for the program.
'''
import os


PATH = os.path.dirname(__file__).replace("src", "")
ENABLELOOP = False
UPDATEPLUGINS = False


def ToggleEnable():
    global ENABLELOOP
    ENABLELOOP = not ENABLELOOP

def UpdatePlugins():
    global UPDATEPLUGINS
    UPDATEPLUGINS = True