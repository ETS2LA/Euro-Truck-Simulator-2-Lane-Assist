"""This module is used to listen to the log file from ETS2 / ATS, it will then return the data to the main program."""
import hashlib
import src.variables as variables
from src.logger import print

ets2FilePath = "C:/Users/" + variables.USERNAME + "/Documents/Euro Truck Simulator 2/game.log.txt"
currentFileHash = None
currentLines = []

def plugin(data):
    global currentFileHash
    global currentLines
    
    # Check if the file hash is the same as the last time we checked
    fileHash = hashlib.md5(open(ets2FilePath, 'rb').read()).hexdigest()
    if currentFileHash == fileHash:
        data["log"] = currentLines
        return data
    
    currentFileHash = fileHash
    currentLines = open(ets2FilePath, "r").readlines()

    data["log"] = currentLines
    print("Log updated")
    return data