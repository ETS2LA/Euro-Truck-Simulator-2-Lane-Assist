# This file has been copied from the installer
# it will need to be rebuilt before release as the
# code is very bad.

# TODO: Use the ETS2 and ATS registry keys directly!

import logging
import vdf
import os
try:
    import winreg
    STEAM_INSTALL_FOLDER = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam"), "SteamPath")[0]
    #logging.info("Found registery key for Steam install folder: " + STEAM_INSTALL_FOLDER)
except:
    STEAM_INSTALL_FOLDER = r"C:\Program Files (x86)\Steam"
    logging.info("Could not find registery key for Steam install folder, using default: [code]" + STEAM_INSTALL_FOLDER + "[/code]")

LIBRARY_FOLDER_LOCATION = r"steamapps\libraryfolders.vdf"
SECONDARY_LIBRARY_FOLDER_LOCATION = r"D:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
ETS2_PATH_IN_LIBRARY = r"steamapps\common\Euro Truck Simulator 2"
ATS_PATH_IN_LIBRARY = r"steamapps\common\American Truck Simulator"
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
    
    #for library in libraries:
    #    logging.info("Found Steam library: " + library)
    
    return libraries

def FindSCSGames():
    try:
        libraries = ReadSteamLibraryFolders()
    except:
        libraries = [r"C:\Games"]
    foundGames = []
    
    for library in libraries:
        if os.path.isfile(library + "\\" + ETS2_PATH_IN_LIBRARY + "\\" + VERIFY_FILE):
            foundGames.append(library + "\\" + ETS2_PATH_IN_LIBRARY)
        if os.path.isfile(library + "\\" + ATS_PATH_IN_LIBRARY + "\\" + VERIFY_FILE):
            foundGames.append(library + "\\" + ATS_PATH_IN_LIBRARY)
    
    return foundGames

if os.name == "nt":
    from win32api import GetFileVersionInfo, LOWORD, HIWORD
    def get_version_number(filename):
        try:
            info = GetFileVersionInfo(filename, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
        except:
            return 0,0,0,0

def GetVersionForGame(gamePath):
    if os.name != "nt":
        return "Unknown"
    
    if "Euro Truck Simulator" in gamePath:
        return ".".join([str(i) for i in get_version_number(gamePath + "\\bin\\win_x64\\eurotrucks2.exe")[:2]])
    elif "American Truck Simulator" in gamePath:
        return ".".join([str(i) for i in get_version_number(gamePath + "\\bin\\win_x64\\amtrucks.exe")[:2]])
    else:
        return "Unknown"