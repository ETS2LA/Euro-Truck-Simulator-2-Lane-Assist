# Import everything
import os
import shutil
from urllib.parse import urljoin, urlparse
import urllib.request
import zipfile
import tkinter as tk
import webbrowser

def PrintGreen(text):
    print("\033[92m {}\033[00m" .format(text))

def PrintRed(text):
    print("\033[91m {}\033[00m" .format(text))

# Helper functions for tkinter
def AddLabel(text, frame, font = "Calibri", size = 12, color = "white"):
    labelVal = tk.StringVar()
    labelVal.set(text)
    label = tk.Label(frame, textvariable=labelVal, fg=color, bg="#1c1c1c", font=(font, size))
    label.pack()
    return labelVal

# Helper functions for tkinter
def AddButton(name, callback, frame):
    button = tk.Button(frame, text=name, command=callback, width=100, fg="white", bg="#1c1c1c")
    button.pack()

# Helper functions for tkinter
def AddEntry(name, frame, width = 100):
    entry = tk.Entry(frame, text = name, width=width, fg="white", bg="#1c1c1c")
    entry.pack()
    return entry

# Default paths
hostname = "github.com" # For checking internet
localVersion = 0
newestVersion = 0
changeLog = ""
branch = "main"
dest = "Euro-Truck-Simulator-2-Lane-Assist-{}".format(branch)

# Just so there are no errors
newestLabel = 0
currentLabel = 0
root = 0
installButton = 0
warningLabel = 0
changeLogButton = 0

# Main Install Function
def Install():
    RemoveOldFiles()
    DownloadNewVersion()
    AskForInformation()

def CheckVersion():
    global localVersion
    global newestVersion
    global installButton
    global warningLabel
    global changeLog
    global changeLogButton
    try:
        # Get local version
        localVersion = open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[0] + " from " + open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[1]
        # Check the newest version
        newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/version.txt".format(branch))
        newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
        os.remove(newestVersionFile)
        # Check the change log        
        changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/changelog.txt".format(branch))
        changeLog = open(changeLogFile, "r").read().split("Update")[1]
        os.remove(changeLogFile)
        currentLabel.set(("Current version: " + localVersion).replace("\n", ""))
        newestLabel.set(("Newest version: " + newestVersion).replace("\n", ""))
        if(installButton == 0):
            installButton = AddButton("Install", Install, root)
            warningLabel = AddLabel("Warning: Backup settings.json", root, color="red")
            changeLogButton = AddButton("Change log", ShowChangeLog, root)
        # Check if the newest version is newer than the local version
    except:
        newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/version.txt".format(branch))
        newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
        os.remove(newestVersionFile)
        changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/changelog.txt".format(branch))
        changeLog = open(changeLogFile, "r").read().split("Update")[1]
        os.remove(changeLogFile)
        currentLabel.set("Current version: " + "not installed")
        newestLabel.set("Newest version: " + newestVersion)
        if(installButton == 0):
            installButton = AddButton("Install", Install, root)
            warningLabel = AddLabel("Warning: Backup settings.json", root, color="red")
            changeLogButton = AddButton("Change log", ShowChangeLog, root)
        pass



def RemoveOldFiles():
    # Delete the old files
    shutil.rmtree(dest, ignore_errors=True)
    print("Old version removed")


def ShowChangeLog():
    # Show the change log in a new window
    changeLogWindow = tk.Tk()
    changeLogWindow.title("Change log")
    changeLogWindow.geometry("600x600")
    changeLogWindow.configure(background="#1c1c1c")
    changeLogLabel = tk.Label(changeLogWindow, text=changeLog, fg="white", bg="#1c1c1c", font=("Calibri", 12), anchor="nw", justify="left")
    changeLogLabel.pack()

def DownloadNewVersion():
    # Download the newest version
    try:
        name, headers = urllib.request.urlretrieve("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/{}.zip".format(branch), "tempFile.zip")
        PrintGreen("Downloading new version please wait...")

        # Unzip the new version
        with zipfile.ZipFile(name, 'r') as zip_ref:
            zip_ref.extractall("")

        # Remove the temporary zip
        os.remove(name)
        PrintGreen("Download complete")
    except Exception as e:
        PrintRed("Error while downloading new version from github")
        print(e)
        exit()


isMac = 0
isGPU = 0
model = 0
installWindow = 0
def AskForInformation():
    global isMac
    global isGPU
    global installWindow
    global model

    # Make the options window
    installWindow = tk.Tk()
    installWindow.title("Additional Installation Options...")
    installWindow.geometry("250x120")
    isMac = tk.IntVar(installWindow)
    isGPU = tk.IntVar(installWindow)
    model = tk.IntVar(installWindow)
    mac = tk.Checkbutton(installWindow, variable=isMac, text="Are you using a mac?", font=("Calibri", 12), onvalue=1, offvalue=0)
    mac.pack()
    gpu = tk.Checkbutton(installWindow, variable=isGPU, text="Do you have an NVIDIA GPU?", font=("Calibri", 12), onvalue=1, offvalue=0)
    gpu.pack()
    modelCheckButton = tk.Checkbutton(installWindow, variable=model, text="Open models in Web Browser?", font=("Calibri", 12), onvalue=1, offvalue=0)
    modelCheckButton.pack()
    # Make a button that calls InstallRequirements() once clicked
    installButton = tk.Button(installWindow, text="Install", command=InstallRequirements, font=("Calibri", 12))
    installButton.pack()


def InstallRequirements():
    try:
        if(model.get() == 1):
            webbrowser.open("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist#lane-detection-models")
        installWindow.destroy()
        path = dest + "\\requirements.txt"
        requirements = open(path, "r").readlines()
        PrintGreen("Installing requirements...")
        for line in range(len(requirements)):
            PrintGreen("{} of {}".format(line + 1, len(requirements)))
            line = requirements[line].replace("\n", "")
            os.system("pip install " + line)
        if isMac.get() == 1:
            PrintGreen("Installing torch for mac...")
            os.system("pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu")
        elif isGPU.get() == 1:
            PrintGreen("Installing torch for NVIDIA GPUs...")
            webbrowser.open("https://developer.nvidia.com/cuda-downloads")
            os.system("pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116")
        else:
            PrintGreen("Installing torch for CPUs...")
            os.system("pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu")
        PrintGreen("Everything is installed")
    except Exception as e:
        PrintRed("Error while installing requirements")
        print(e)
        exit()

# Default TKinter window
width = 250
height = 300
root = tk.Tk()
root.title("ETS2 Lane Assist Updater V0.3")
root.geometry("%dx%d" % (width, height))
root.configure(bg='#1c1c1c', padx=10, pady=10)
AddLabel("ETS2 Lane Assist Updater V0.3", root, size=14)
currentLabel = AddLabel("Current version: " + "unknown", root, size=10)
newestLabel = AddLabel("Newest version: " + "unknown", root, size=10)
AddButton("Check versions", CheckVersion, root)

root.mainloop()