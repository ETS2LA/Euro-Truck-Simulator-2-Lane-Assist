# Import everything
import os
import shutil
from urllib.parse import urljoin, urlparse
import urllib.request
import zipfile
import tkinter as tk
from tkinter import ttk
import webbrowser
import sys

def PrintGreen(text):
    print("\033[92m {}\033[00m" .format(text))

def PrintRed(text):
    print("\033[91m {}\033[00m" .format(text))

def PrintBlue(text):
    print("\033[94m {}\033[00m" .format(text))

# Helper functions for tkinter
def AddLabel(text, frame, font = "Calibri", size = 12, color = "white", bg = "#1c1c1c"):
    labelVal = tk.StringVar()
    labelVal.set(text)
    label = tk.Label(frame, textvariable=labelVal, fg=color, bg=bg, font=(font, size))
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
availableBranches = ["main", "experimental", "updater"]
selectedBranch = "main"
dest = "Euro-Truck-Simulator-2-Lane-Assist-{}".format(selectedBranch)
w = 250
h = 300
# Just so there are no errors
newestLabel = 0
currentLabel = 0
root = 0
installButton = 0
warningLabel = 0
changeLogButton = 0
progressBar = 0
progressText = 0

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
    if selectedBranch != "updater":
        try:
            # Get local version
            localVersion = open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[0] + " from " + open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[1]
            # Check the newest version
            newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/version.txt".format(selectedBranch))
            newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
            os.remove(newestVersionFile)
            # Check the change log        
            changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/changelog.txt".format(selectedBranch))
            changeLog = open(changeLogFile, "r").read().split("Update")[1]
            os.remove(changeLogFile)
            currentLabel.set(("Current version: " + localVersion).replace("\n", ""))
            newestLabel.set(("Newest version: " + newestVersion).replace("\n", ""))
            if(installButton == 0):
                installButton = AddButton("Install", Install, root)
                if selectedBranch == "experimental":
                    warningLabel = AddLabel("Warning: branch may not work\nsince it's used for development", root, color="red")
                else:
                    warningLabel = AddLabel("Warning: Backup settings.json", root, color="red")
                changeLogButton = AddButton("Change log", ShowChangeLog, root)
            elif selectedBranch == "experimental":
                warningLabel.set("Warning: branch may not work\nsince it's used for development")
            else:
                warningLabel.set("Warning: Backup settings.json")
            
        except:
            newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/version.txt".format(selectedBranch))
            newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
            os.remove(newestVersionFile)
            changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/{}/changelog.txt".format(selectedBranch))
            changeLog = open(changeLogFile, "r").read().split("Update")[1]
            os.remove(changeLogFile)
            currentLabel.set("Current version: " + "not installed")
            newestLabel.set("Newest version: " + newestVersion.replace("\n", ""))
            if(installButton == 0):
                installButton = AddButton("Install", Install, root)
                if selectedBranch == "experimental":
                    warningLabel = AddLabel("Warning: branch may not work\nsince it's used for development", root, color="red")
                else:
                    warningLabel = AddLabel("Warning: Backup settings.json", root, color="red")
                changeLogButton = AddButton("Change log", ShowChangeLog, root)
            elif selectedBranch == "experimental":
                warningLabel.set("Warning: branch may not work\nsince it's used for development")
            else:
                warningLabel.set("Warning: Backup settings.json")
            
    else:
        currentLabel.set("Current version: " + "can't check")
        newestLabel.set("Newest version: " + "can't check")
        if(installButton == 0):
                installButton = AddButton("Install", Install, root)
                warningLabel = AddLabel("Warning: updater branch only\n contains the updater", root, color="red")
                changeLogButton = AddButton("Change log", ShowChangeLog, root)
        pass



def RemoveOldFiles():
    # Delete the old files
    try:
        shutil.move("Euro-Truck-Simulator-2-Lane-Assist-{}\\settings.json".format(selectedBranch), "settings.json")
        PrintBlue("Successfully backed up settings.json")
    except:
        pass
    shutil.rmtree(dest, ignore_errors=True)
    PrintGreen("Old version removed")


def ShowChangeLog():
    # Show the change log in a new window
    changeLogWindow = tk.Tk()
    changeLogWindow.title("Change log")
    changeLogWindow.geometry("600x600")
    changeLogWindow.configure(background="#1c1c1c")
    changeLogLabel = tk.Label(changeLogWindow, text=changeLog, fg="white", bg="#1c1c1c", font=("Calibri", 12), anchor="nw", justify="left")
    changeLogLabel.pack()

lastPercentReported = 1
def DownloadProgressBar(count, blockSize, totalSize):
    global progressBar
    global lastPercentReported

    percent = count * blockSize * 100 / totalSize
    percent = round(percent, 2)
    if percent > 100:
        percent = 100.00
    kb = int(count * blockSize / 1024)

    if percent < 0:
        percent = "unknown"

    if lastPercentReported != percent:
        sys.stdout.write("\r {}% {}kb".format(percent, kb))
        sys.stdout.flush()
        
        try:
            progressBar["value"] = int(percent)
            progressText["text"] = ("{}% {}kb".format(percent, kb))
            root.update()
        except Exception as e:
            pass
        
        lastPercentReported = percent

def DownloadNewVersion():
    global lastPercentReported
    global progressBar
    global progressText
    # Download the newest version
    try:
        lastPercentReported = 1
        PrintGreen("\n Downloading new version please wait...")
        print("\r\033[94m")
        
        if progressBar == 0:
            progressBar = ttk.Progressbar(root, orient="horizontal", length=w, mode="determinate")
            progressBar.config()
            progressBar.pack()
            progressText = tk.Label(root, text="Downloading... (0%)", fg="white", bg="#1c1c1c")
            progressText.pack()
        
        name, headers = urllib.request.urlretrieve("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/{}.zip".format(selectedBranch), "tempFile.zip", reporthook=DownloadProgressBar)
        print("\033[0m")
        # Unzip the new version
        with zipfile.ZipFile(name, 'r') as zip_ref:
            zip_ref.extractall("")

        # Remove the temporary zip
        os.remove(name)
        PrintGreen("Download complete")
        PrintBlue("You can copy your settings.json back into the app folder")
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
    installWindow.geometry("250x160")
    text = tk.Label(installWindow, text="You can close this window if\nthis is not your first time installing")
    text.pack()
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

def ChangeBranch(branch):
    global selectedBranch
    global branchSelectorValue
    selectedBranch = branch
    PrintBlue("Selected branch: " + selectedBranch)

# Default TKinter window
root = tk.Tk()
root.title("ETS2 Lane Assist Updater V0.4")
root.geometry("%dx%d" % (w, h))
root.configure(bg='#1c1c1c', padx=10, pady=10)
AddLabel("ETS2 Lane Assist Updater V0.4", root, size=14)
currentLabel = AddLabel("Current version: " + "unknown", root, size=10)
newestLabel = AddLabel("Newest version: " + "unknown", root, size=10)
branchSelectorValue = tk.StringVar(root)
branchSelector = tk.OptionMenu(root, branchSelectorValue, *availableBranches, command=ChangeBranch)
branchSelectorValue.set("main")
branchSelector.config(bg="#1c1c1c", fg="white", highlightcolor="#1c1c1c", activebackground="#1c1c1c", activeforeground="white", width=100)
branchSelector.pack()
AddButton("Check versions", CheckVersion, root)

root.mainloop()