import datetime
import json
import os

YEAR = datetime.datetime.now().year
"""This year will be displayed in the window title."""

PATH = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
"""The path to the ETS2LA folder."""

if PATH.endswith("/ETS2LA"):
    PATH = PATH[:-7]
PATH += "/"

ICONPATH = PATH + "ETS2LA/Window/favicon.ico"
"""The path to the .ico icon file, needs to be manually changed when the icon gets moved!"""

OS = os.name
"""The users operating system. Windows = 'nt'"""

CLOSE = False
"""Whether the application should close or not. Used to trigger the close from code that is not the main thread."""

RESTART = False
"""Whether the application should restart or not. Used to trigger the restart from code that is not the main thread."""

MINIMIZE = False
"""Whether the application should minimize or not. Used to trigger the minimize from code that is not the main thread."""

CONSOLEHWND = None
"""The handle of the console window. The console.py will set the handle when hiding the console is enabled."""

CONSOLENAME = None
"""The name/title of the console window. The console.py will set the name when hiding the console is enabled."""

DEVELOPMENT_MODE = False
"""Whether the application is running in development mode. Will be set to True when running the main.py with the --dev flag."""

LOCAL_MODE = False
"""Whether the user interface is run locally or gotten from the server."""

METADATA = json.loads(open(PATH + "metadata.json", "r").read())
"""Current version metadata."""

IS_UI_UPDATING = False
"""Used by all UIs in the current process to wait for each other to complete updating before continuing."""

DOCUMENTS_PATH = ""
"""The path to the documents folder of the user."""

ETS2_LOG_PATH = ""
"""The path to the ETS2 log file."""

ATS_LOG_PATH = ""
"""The path to the ATS log file."""

ATS_DLC = []
"""List of all ATS DLCs currently installed."""

ETS2_DLC = []
"""List of all ETS2 DLCs currently installed."""


if os.name == "nt":
    import ctypes.wintypes
    _CSIDL_PERSONAL = 5     # My Documents
    _SHGFP_TYPE_CURRENT = 0 # Get current, not default value
    _buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, _CSIDL_PERSONAL, None, _SHGFP_TYPE_CURRENT, _buf)
    DOCUMENTS_PATH = f"{_buf.value}"
    
    DOCUMENTS_PATH = DOCUMENTS_PATH.replace('\\', '/')
    ETS2_LOG_PATH = f"{DOCUMENTS_PATH}/Euro Truck Simulator 2/game.log.txt"
    ATS_LOG_PATH = f"{DOCUMENTS_PATH}/American Truck Simulator/game.log.txt"
else:
    # TODO: No clue if this works.
    DOCUMENTS_PATH = f"{os.path.expanduser('~')}/Documents"
    ETS2_LOG_PATH = f"{os.path.expanduser('~')}/.local/share/Euro Truck Simulator 2/game.log.txt"
    ATS_LOG_PATH = f"{os.path.expanduser('~')}/.local/share/American Truck Simulator/game.log.txt"    

try:
    with open(ATS_LOG_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "[hashfs] dlc_" in line:
                dlc = line.split(".scs")[0].split("dlc_")[1]
                dlc = "dlc_" + dlc
                ATS_DLC.append(dlc)
except: pass

try:
    with open(ETS2_LOG_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "[hashfs] dlc_" in line:
                dlc = line.split(".scs")[0].split("dlc_")[1]
                dlc = "dlc_" + dlc
                ETS2_DLC.append(dlc)
except: pass