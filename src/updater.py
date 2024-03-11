import requests
import src.variables as variables
import src.settings as settings
import src.helpers as helpers
import os
from src.logger import print

def UpdateChecker():
    disable = settings.GetSettings("Dev", "disable_update_checker", False)
    if disable:
        print("Dev mode is enabled, skipping update check")
        return
    
    currentVer = variables.VERSION.split(".")
    githubUrl = "https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/"
    sourceForgeUrl = "https://sourceforge.net/p/eurotrucksimulator2-laneassist/code/ci/main/tree/"
    try:
        remoteVer = requests.get(githubUrl + "version.txt").text.strip().split(".")
        remote = "github"
    except:
        try:
            remoteVer = requests.get(sourceForgeUrl + "version.txt?format=raw").text.strip().split(".")
            remote = "sourceforge"
        except:
            print("Failed to check for updates")
            print("Please check your internet connection and try again later")
            return
    if int(currentVer[0]) < int(remoteVer[0]):
        update = True
    elif int(currentVer[1]) < int(remoteVer[1]):
        update = True
    elif int(currentVer[2]) < int(remoteVer[2]):
        update = True
    else:
        update = False
    
    if remote == "github":
        url = githubUrl
    else:
        url = sourceForgeUrl
    
    if update:
        if remote == "github":
            changelog = requests.get(url + "changelog.txt").text
        elif remote == "sourceforge":
            changelog = requests.get(url + "changelog.txt?format=raw").text
            
        print(f"An update is available: {'.'.join(remoteVer)}")

        print(f"Changelog:\n{changelog}")
        from tkinter import messagebox
        if helpers.AskOkCancel("Updater", f"We have detected an update, do you want to install it?\nCurrent - {'.'.join(currentVer)}\nUpdated - {'.'.join(remoteVer)}\n\nChangelog:\n{changelog}"):
            os.system("git stash")
            os.system("git pull")
            if helpers.AskOkCancel("Updater", "The update has been installed and the application needs to be restarted. Do you want to quit the app?", yesno=True):
                quit()
            else:
                variables.UPDATEAVAILABLE = remoteVer
                variables.RELOAD = True
        else:
            variables.UPDATEAVAILABLE = remoteVer
            variables.RELOAD = True
            pass
    else:
        print(f"No update available, current version: {'.'.join(currentVer)}")
