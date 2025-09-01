import datetime
import json
import git
import sys
import os

YEAR = datetime.datetime.now().year
"""This year will be displayed in the window title."""

APPTITLE = f"ETS2LA - Tumppi066 & Contributors © {YEAR}"
"""The title of the frontend window."""

FRONTEND_MIRRORS = [
    "https://app.ets2la.com",  # Global
    "https://app.ets2la.cn",  # China
]
"""The frontend mirrors. The first one is the default mirror."""

PATH = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
"""The path to the ETS2LA folder."""

if PATH.endswith("/ETS2LA"):
    PATH = PATH[:-7]
PATH += "/"

ICONPATH = PATH + "ETS2LA/Assets/favicon.ico"
"""The path to the .ico icon file, needs to be manually changed when the icon gets moved!"""

OS = os.name
"""The users operating system. Windows = 'nt'"""

REFRESH_PAGES = False
"""Tell the UI websocket to send updated page data to all subscribers."""

CLOSE = False
"""Whether the application should close or not. Used to trigger the close from code that is not the main thread."""

RESTART = False
"""Whether the application should restart or not. Used to trigger the restart from code that is not the main thread."""

MINIMIZE = False
"""Whether the application should minimize or not. Used to trigger the minimize from code that is not the main thread."""

UPDATE = False
"""Whether the application should trigger an update or not. Used to trigger the update from code that is not the main thread."""

CONSOLEHWND = None
"""The handle of the console window. The console.py will set the handle when hiding the console is enabled."""

CONSOLENAME = None
"""The name/title of the console window. The console.py will set the name when hiding the console is enabled."""

DEVELOPMENT_MODE = "--dev" in sys.argv
"""Whether the application is running in development mode. Will be set to True when running the main.py with the --dev flag."""

CHINA_MODE = "--china" in sys.argv
"""Whether the application is running in China mode. This will use ets2la.cn websites and other China specific features."""

LOCAL_MODE = "--local" in sys.argv
"""Whether the user interface is run locally or gotten from the server."""

HIGH_PRIORITY = "--high" in sys.argv
"""Whether the application should run in high priority mode."""

FRONTEND_URL = (
    sys.argv[sys.argv.index("--frontend-url") + 1]
    if "--frontend-url" in sys.argv
    else "https://app.ets2la.com"
)
"""Frontend URL from the --frontend-url argument."""

NO_UI = "--no-ui" in sys.argv
"""Whether the app should start without the UI."""

NO_CONSOLE = "--no-console" in sys.argv and not NO_UI
"""Whether the app should close the console as soon as the UI has started."""

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

WINDOW_QUEUE = None
"""
Used by the window window to get commands from the main process.
Use .put(), only the window process should .get().
"""

# Update paths
if os.name == "nt":
    import ctypes.wintypes

    _CSIDL_PERSONAL = 5  # My Documents
    _SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    _buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, _CSIDL_PERSONAL, None, _SHGFP_TYPE_CURRENT, _buf
    )
    DOCUMENTS_PATH = f"{_buf.value}"

    DOCUMENTS_PATH = DOCUMENTS_PATH.replace("\\", "/")
    ETS2_LOG_PATH = f"{DOCUMENTS_PATH}/Euro Truck Simulator 2/game.log.txt"
    ATS_LOG_PATH = f"{DOCUMENTS_PATH}/American Truck Simulator/game.log.txt"
else:
    # TODO: No clue if this works.
    DOCUMENTS_PATH = f"{os.path.expanduser('~')}/Documents"
    ETS2_LOG_PATH = (
        f"{os.path.expanduser('~')}/.local/share/Euro Truck Simulator 2/game.log.txt"
    )
    ATS_LOG_PATH = (
        f"{os.path.expanduser('~')}/.local/share/American Truck Simulator/game.log.txt"
    )

# Update DLCs
try:
    with open(ATS_LOG_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "[hashfs] dlc_" in line:
                dlc = line.split(".scs")[0].split("dlc_")[1]
                dlc = "dlc_" + dlc
                ATS_DLC.append(dlc)
except Exception:
    pass

try:
    with open(ETS2_LOG_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "[hashfs] dlc_" in line:
                dlc = line.split(".scs")[0].split("dlc_")[1]
                dlc = "dlc_" + dlc
                ETS2_DLC.append(dlc)
except Exception:
    pass

# Update metadata
try:
    repo = git.Repo(search_parent_directories=True)
    hash = repo.head.object.hexsha[:9]
    METADATA["version"] = f"{METADATA['version']} - {hash}"
except Exception:
    pass
