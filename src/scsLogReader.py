"""This module is used to listen to the log file from ETS2 / ATS, it will then return the data to the main program."""
import src.variables as variables
import src.helpers as helpers
from src.logger import print
import hashlib

ets2FilePath = "C:/Users/" + variables.USERNAME + "/Documents/Euro Truck Simulator 2/game.log.txt"
currentFileHash = None
currentLines = []
hasShownCrackError = False

def CheckForCrackedGame(data):
    global hasShownCrackError
    crackIdentifier = "0000007E"
    for line in data["log"]:
        if crackIdentifier in line:
            if not hasShownCrackError:
                helpers.ShowFailure("\nThis is almost certainly due to a cracked game or DLC. It might just be a broken DLL though.\nIf the app and game works then fine, but if you see this error we will not help with diagnosing the issue.", "DLL load error detected!")
                print("Possible cracked game detected.")
                hasShownCrackError = True
        

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