import json
import vdf
import os

LIBRARY_FOLDER_LOCATION = r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
SECONDARY_LIBRARY_FOLDER_LOCATION = r"D:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
ETS2_PATH_IN_LIBRARY = r"steamapps\common\Euro Truck Simulator 2"
ATS_PATH_IN_LIBRARY = r"steamapps\common\American Truck Simulator"
VERIFY_FILE = "base.scs"

def ReadSteamLibraryFolders():
    libraries = []
    
    if os.path.isfile(LIBRARY_FOLDER_LOCATION):
        file = open(LIBRARY_FOLDER_LOCATION, "r")
    else:
        file = open(SECONDARY_LIBRARY_FOLDER_LOCATION, "r")
        
    file = vdf.load(file)   
    for key in file["libraryfolders"]:
        if key.isnumeric():
            libraries.append(file["libraryfolders"][key]["path"])    
    
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
