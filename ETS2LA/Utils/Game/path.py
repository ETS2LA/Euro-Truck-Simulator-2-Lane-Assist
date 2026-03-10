"""This file is used to discover ETS2 and ATS game files.
The functions here work fine, but the code is very old so it's not
all that pretty.
"""

import os
import vdf
import json
import logging
import subprocess
import ETS2LA.variables as variables

if os.name == "nt":
    try:
        import winreg

        STEAM_INSTALL_FOLDER = winreg.QueryValueEx(
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam"), "SteamPath"
        )[0]
        if variables.DEVELOPMENT_MODE:
            logging.info(f"Found registery key for Steam install folder: {STEAM_INSTALL_FOLDER}")
    except Exception:
        STEAM_INSTALL_FOLDER = r"C:\Program Files (x86)\Steam"
        if variables.DEVELOPMENT_MODE:
            logging.warning(
                f"Could not find registery key for Steam install folder, using default: {STEAM_INSTALL_FOLDER}"
            )
else:
    STEAM_INSTALL_FOLDER = os.path.expanduser("~/.steam/steam")

if os.name == "nt":
    LIBRARY_FOLDER_LOCATION = r"steamapps\libraryfolders.vdf"
    SECONDARY_LIBRARY_FOLDER_LOCATION = r"D:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
    ETS2_PATH_IN_LIBRARY = r"steamapps\common\Euro Truck Simulator 2"
    ATS_PATH_IN_LIBRARY = r"steamapps\common\American Truck Simulator"
    VERIFY_FILE = "base.scs"
else:
    LIBRARY_FOLDER_LOCATION = "steamapps/libraryfolders.vdf"
    SECONDARY_LIBRARY_FOLDER_LOCATION = f"{STEAM_INSTALL_FOLDER}/steamapps/libraryfolders.vdf"
    ETS2_PATH_IN_LIBRARY = "steamapps/common/Euro Truck Simulator 2"
    ATS_PATH_IN_LIBRARY = "steamapps/common/American Truck Simulator"
    VERIFY_FILE = "base.scs"


def ReadSteamLibraryFolders():
    libraries = []

    if os.path.isfile(os.path.join(STEAM_INSTALL_FOLDER, LIBRARY_FOLDER_LOCATION)):
        file = open(os.path.join(STEAM_INSTALL_FOLDER, LIBRARY_FOLDER_LOCATION), "r")
    else:
        file = open(SECONDARY_LIBRARY_FOLDER_LOCATION, "r")

    file = vdf.load(file)
    for key in file["libraryfolders"]:
        if key.isnumeric():
            libraries.append(file["libraryfolders"][key]["path"])

    # for library in libraries:
    #    logging.info("Found Steam library: " + library)

    return libraries


def FindSCSGames():
    try:
        libraries = ReadSteamLibraryFolders()
    except Exception:
        libraries = [r"C:\Games"]
    foundGames = []

    for library in libraries:
        if os.path.isfile(library + os.sep + ETS2_PATH_IN_LIBRARY + os.sep + VERIFY_FILE):
            foundGames.append(library + os.sep + ETS2_PATH_IN_LIBRARY)
        if os.path.isfile(library + os.sep + ATS_PATH_IN_LIBRARY + os.sep + VERIFY_FILE):
            foundGames.append(library + os.sep + ATS_PATH_IN_LIBRARY)

    return foundGames


if os.name == "nt":
    from win32api import GetFileVersionInfo, LOWORD, HIWORD

    def get_version_number(filename):
        try:
            info = GetFileVersionInfo(filename, os.sep)
            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]
            return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
        except Exception:
            return 0, 0, 0, 0
else:

    def get_version_number(filename):
        # DO NOT use `[program, argv1, argv2, ...]`, it causes problem if space(s) in `filename`
        proc = subprocess.run(
            f"peres -v '{filename}' --format json",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        assert proc.returncode != 0, (
            "please check if installed `peres` or `pev-git` (see https://github.com/mentebinaria/readpe)"
        )

        version_info = json.loads(proc.stdout)
        # version info like
        """
        {
            "File Version": "65263.1213.1.0",
            "Product Version": "1.58.1.4"
        }
        """
        return tuple(map(int, version_info["Product Version"].split(".")))


def GetVersionForGame(gamePath):
    if "Euro Truck Simulator" in gamePath:
        return ".".join(
            [
                str(i)
                for i in get_version_number(
                    gamePath + f"{os.sep}bin{os.sep}win_x64{os.sep}eurotrucks2.exe"
                )[:2]
            ]
        )
    elif "American Truck Simulator" in gamePath:
        return ".".join(
            [
                str(i)
                for i in get_version_number(
                    gamePath + f"{os.sep}bin{os.sep}win_x64{os.sep}amtrucks.exe"
                )[:2]
            ]
        )
    else:
        return "Unknown"
