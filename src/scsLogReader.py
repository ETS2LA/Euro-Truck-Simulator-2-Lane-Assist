"""This module is used to listen to the log file from ETS2 / ATS, it will then return the data to the main program."""
import src.variables as variables
import src.helpers as helpers
from src.logger import print
import hashlib

ets2FilePath = "C:/Users/" + variables.USERNAME + "/Documents/Euro Truck Simulator 2/game.log.txt"
currentFileHash = None
currentLines = []

def CheckForCrackedGame(data):
    crackIdentifier = "0000007E"
    for line in data["log"]:
        if crackIdentifier in line:
            helpers.ShowFailure("\nThis is most likely because of a cracked game or DLCs.\nYou will have to buy the game / DLCs to continue!", "Error loading required DLLs")
        

def plugin(data):
    global currentFileHash
    global currentLines
    
    try:
        # Check if the file hash is the same as the last time we checked
        fileHash = hashlib.md5(open(ets2FilePath, 'rb').read()).hexdigest()
        if currentFileHash == fileHash:
            data["log"] = currentLines
            CheckForCrackedGame(data)
            return data
        
        currentFileHash = fileHash
        currentLines = open(ets2FilePath, "r").readlines()
        CheckForCrackedGame(data)

        data["log"] = currentLines
    except:
        pass
    return data