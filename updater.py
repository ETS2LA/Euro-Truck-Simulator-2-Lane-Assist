# Import everything
import os

print("Checking that all requirements are installed...")
os.system("pip install shutil")
os.system("pip install zipfile")
os.system("pip install urllib")
os.system("pip install tkinter")
os.system("pip install webbrowser")
print("It is normal for there to be errors here this is just to make sure...")

import shutil
from urllib.parse import urljoin, urlparse
import urllib.request
import zipfile
import tkinter as tk
import webbrowser

def AddLabel(text, frame, font = "Calibri", size = 12, color = "white"):
    labelVal = tk.StringVar()
    labelVal.set(text)
    label = tk.Label(frame, textvariable=labelVal, fg=color, bg="#1c1c1c", font=(font, size))
    label.pack()
    return labelVal

def AddButton(name, callback, frame):
    button = tk.Button(frame, text=name, command=callback, width=100, fg="white", bg="#1c1c1c")
    button.pack()

def AddEntry(name, frame, width = 100):
    entry = tk.Entry(frame, text = name, width=width, fg="white", bg="#1c1c1c")
    entry.pack()
    return entry

# Default paths
hostname = "github.com" # For checking internet
dest = "Euro-Truck-Simulator-2-Lane-Assist-main"
localVersion = 0
newestVersion = 0
changeLog = ""

# Just so there are no errors
newestLabel = 0
currentLabel = 0
root = 0
installButton = 0
warningLabel = 0
changeLogButton = 0
# Check the current version and the newest version

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
    try:
        # Get local version
        localVersion = open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[0] + " from " + open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[1]
        # Check the newest version
        newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt")
        newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
        os.remove(newestVersionFile)
        # Check the change log        
        changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/experimental/changelog.txt")
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
        newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt")
        newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
        os.remove(newestVersionFile)
        changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/experimental/changelog.txt")
        changeLog = open(changeLogFile, "r").read().split("Update")[1]
        os.remove(changeLogFile)
        currentLabel.set("Current version: " + "not installed")
        newestLabel.set("Newest version: " + newestVersion)
        if(installButton == 0):
            installButton = AddButton("Install", Install, root)
            warningLabel = AddLabel("Warning: Backup settings.json", root, color="red")
            changeLogButton = AddButton("Change log", ShowChangeLog, root)
        pass


# Make sure the user understands that the program will delete the old files
def RemoveOldFiles():
    # Delete the old files
    shutil.rmtree(dest, ignore_errors=True)
    print("Files removed")

# Download percentage display
# Credits to https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html


def ShowChangeLog():
    changeLogWindow = tk.Tk()
    changeLogWindow.title("Change log")
    changeLogWindow.geometry("600x600")
    changeLogWindow.configure(background="#1c1c1c")
    changeLogLabel = tk.Label(changeLogWindow, text=changeLog, fg="white", bg="#1c1c1c", font=("Calibri", 12), anchor="nw", justify="left")
    changeLogLabel.pack()

def DownloadNewVersion():
    # Download the newest version
    name, headers = urllib.request.urlretrieve("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/main.zip", "tempFile.zip")
    print("Downloading please wait...")

    # Unzip the new version
    with zipfile.ZipFile(name, 'r') as zip_ref:
        zip_ref.extractall("")

    # Remove the temporary zip
    os.remove(name)

isMac = 0
isGPU = 0
model = 0
installWindow = 0
def AskForInformation():
    global isMac
    global isGPU
    global installWindow
    global model
    # Install the requirements from the requirements.txt file
    # This piece of code get's the current path and appends the newly downloaded file path to it.
    # os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt"
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
    installButton = tk.Button(installWindow, text="Install", command=InstallRequirements, font=("Calibri", 12))
    installButton.pack()


def InstallRequirements():
    if(model.get() == 1):
        webbrowser.open("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist#lane-detection-models")
    installWindow.destroy()
    os.system("pip install -r " + os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt")
    if isMac.get() == 1:
        os.system("pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu")
    elif isGPU.get() == 1:
        webbrowser.open("https://developer.nvidia.com/cuda-downloads")
        os.system("pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116")
    else:
        os.system("pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu")

# Default TKinter window
width = 250
height = 300
root = tk.Tk()
root.title("Updater")
root.geometry("%dx%d" % (width, height))
root.configure(bg='#1c1c1c', padx=10, pady=10)
AddLabel("ETS2 Lane Assist Updater", root, size=14)
currentLabel = AddLabel("Current version: " + "unknown", root, size=10)
newestLabel = AddLabel("Newest version: " + "unknown", root, size=10)
AddButton("Check versions", CheckVersion, root)

root.mainloop()