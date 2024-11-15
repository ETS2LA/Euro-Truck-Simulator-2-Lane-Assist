import json
import os

YEAR = 2024
"""This year will be displayed in the window title. The year in the LICENSE file must be set manually!"""

PATH = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
if PATH.endswith("/ETS2LA"):
    PATH = PATH[:-7]
PATH += "/"
"""The path to the ETS2LA folder."""

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

METADATA = json.loads(open(PATH + "metadata.json", "r").read())