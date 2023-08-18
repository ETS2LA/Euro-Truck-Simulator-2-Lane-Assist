import sys
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import threading

import time
from tkinter import ttk

APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/"

def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

"""

Steps to installation : 
(under each step are the individual steps for displaying on the side bar)

1. Create a virtual environment
    - Check for virtual environment
    - Create a virtual environment
2. Download the app with git
    - Check for git
    - Check for app
    - Check for connection to github
    - Download the app
    - Check for successful download
3. Install the requirements from requirements.txt
    - Check for requirements.txt
    - Install the requirements
?. Ask the user for a theme (coming later)

"""

# region Check Necessary Requirements on Startup

# Check for path spaces
if " " in os.getcwd():
    printRed("The path of this app includes spaces.")
    printRed("Please move the app to a folder path without spaces.")
    printGreen("For example 'C:/LaneAssist/'")
    input()
    quit()

# Check for special characters
if not os.getcwd().isascii():
    printRed("The path of this app includes special characters.")
    printRed("Please move the app to a folder path without special characters.")
    printGreen("For example 'C:/LaneAssist/'")
    input()
    quit()

if "OneDrive" in os.getcwd().lower():
    printRed("The path of this app includes 'OneDrive'.")
    printRed("OneDrive prevents the app from creating a virtual environment.")
    printRed("Please move the app to a folder path without 'OneDrive'.")
    printGreen("For example 'C:/LaneAssist/'")
    input()
    quit()

# Check python version (must be > 3.9.x)
if sys.version_info[0] != 3 or sys.version_info[1] < 9:
    printRed("This app requires atleast python version 3.9.x to create the correct virtual environment.")
    printRed("Please install another version and run the installer again.")
    input()
    quit()

# Check for a .bat file
if not os.path.exists("installer.bat"):
    # Create it
    with open("installer.bat", "w") as file:
        file.write("python installer.py")
        file.write("\npause")
        printGreen("Created installer.bat to run the application easier.")

def CheckGit():
    try:
        subprocess.check_call(["git", "--version"])
        found = True
    except:
        found = False
    
    return found

def Install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check for customtkinter
try:
    import sv_ttk

except ImportError:
    print("Please wait installing necessary UI library...")
    Install("sv_ttk")
    printGreen("> Done")
    import sv_ttk

# Check for urrlib
try:
    import urllib.request as urrlib

except:
    print("Please wait installing urlrlib...")
    Install("urllib")
    printGreen("> Done")
    import urllib.request as urrlib

# Check for zipfile
try:
    import zipfile

except:
    print("Please wait installing zipfile...")
    Install("zipfile")
    printGreen("> Done")
    import zipfile

# Check for venv
try:
    import venv
except:
    print("Please wait installing venv...")
    Install("virtualenv")
    printGreen("> Done")
    import venv

# endregion

# region Helper Functions

progress = 0
def DownloadProgressBar(count, blockSize, totalSize):
    global progress

    if totalSize == -1:
        totalSize = 33656
    percent = count * blockSize * 100 / totalSize
    percent = round(percent, 2)
    if percent > 100:
        percent = 100.00
    kb = int(count * blockSize / 1024)

    sys.stdout.write("\r {}kb".format(kb))
    sys.stdout.flush()
    
    try:
        ChangeStatus("Downloading... " + "\r {}kb".format(kb))
        root.update()
    except Exception as e:
        pass
        

def ChangeStatus(text):
    global status
    status.configure(text=text)
    root.update()

# endregion

# region Create the initial installer window

# Make the installer window
root = tk.Tk()
root.title("ETS2 Lane Assist Installer")
width = 800
height = 600
root.geometry(f"{width}x{height}")
root.resizable(False, False)
sv_ttk.set_theme("dark")

# Bottom text
ttk.Label(root, text="ETS2 Lane Assist   ©Tumppi066 - 2023", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
ttk.Label(root, text="Installer version 0.2.0", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
progressBar = ttk.Progressbar(root, mode="determinate", length=width)
progressBar.pack(side="top", padx=0, pady=0, anchor="w")

# Left button bar
progressFrame = ttk.LabelFrame(root, text="Progress", width=width-630, height=height-20)
progressFrame.pack_propagate(0)
progressFrame.grid_propagate(0)

progressFrame.pack(side="left", anchor="n", padx=10, pady=10)

# Plugin frame
statusFrame = ttk.LabelFrame(root, text="Status", width=width, height=height-20)
statusFrame.pack_propagate(0)
statusFrame.grid_propagate(0)

statusFrame.pack(side="left", anchor="w", padx=10, pady=10)

# Info page
infoPage = tk.Canvas(statusFrame, width=600, height=520, border=0, highlightthickness=0)
infoPage.grid_propagate(0)
infoPage.pack_propagate(0)

# Add a label describing what the installer will do
ttk.Label(infoPage, text="Welcome!", font=("Roboto", 20, "bold")).pack(pady=10, anchor="w", padx=10)
ttk.Label(infoPage, text="The installer will create a virtual environment for the app's python version.", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text="The app will be installed in the same folder as the installer.", font=("Roboto", 10, "bold")).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text="", font=("Roboto", 10)).pack(pady=2)
ttk.Label(infoPage, text="Following are the steps the app will take to install itself:", font=("Roboto", 10, "bold")).pack(pady=5, anchor="w", padx=10)
ttk.Label(infoPage, text="1. Create a virtual python environment from your current python version", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text="2. Download the app from github", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text="3. Install the requirements from requirements.txt (to the virtual env)", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text="4. Create .bat files for easy access to the app's functions", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)
ttk.Label(infoPage, text=" ", font=("Roboto", 10)).pack(pady=2, anchor="w", padx=10)

infoPage.pack(anchor="center", expand=False)
infoPage.update()
root.update()

# endregion

# region Progress function

states = {
    "Venv": [
        "Check venv",
        "Create venv",
    ],
    "Download": [
        "Check git",
        "Check connection",
        "Check app",
        "Download app",
        "Check download",
    ],
    "Install": [
        "Update pip",
        "Install requirements",
    ],
    "Cleanup": [
        "Empty pip cache",
        "Create .bat files",
    ],
    "Done!": [
        "",
    ]
}

# State = The current state index
# Progress = The current progress index
def UpdateProgress(state, value, progress, problem=False):
    progressBar.configure(value=progress)
    
    for child in progressFrame.winfo_children():
        child.destroy()
    
    # ttk.Label(progressFrame, text=" ", font=("Roboto", 0, "bold")).pack(pady=1, anchor="n")
    
    for i in range(len(states)):
        keys = list(states.keys())
        ttk.Label(progressFrame, text=keys[i], font=("Calibri", 14, "bold")).pack(pady=5, anchor="n", padx=10)
        
        for j in range(len(states[keys[i]])):
            if j == value and i == state:
                ttk.Label(progressFrame, text="> " + states[keys[i]][j] + " <", font=("Roboto", 10, "bold"), foreground="#cccc00" if not problem else "#b30000").pack(pady=5, anchor="n", padx=10)
            elif j < value and i == state or i < state:
                ttk.Label(progressFrame, text=states[keys[i]][j], font=("Roboto", 8, "bold"), foreground="green").pack(pady=5, anchor="n", padx=10)
            else:
                ttk.Label(progressFrame, text=states[keys[i]][j], font=("Roboto", 8)).pack(pady=5, anchor="n", padx=10)
    
        ttk.Label(progressFrame, text="", font=("Roboto", 10)).pack(pady=5, anchor="n", padx=10)
    
    progressFrame.update()
    root.update()
    
    pass

UpdateProgress(0, 0, 0)

# endregion

# region Install sequence

def InstallSequence():
    
    # region Branch selection
    
    for child in infoPage.winfo_children():
        child.destroy()
        
    ttk.Label(infoPage, text="Please select the branch you want to install:", font=("Roboto", 16, "bold")).pack(pady=5, anchor="w", padx=10)
    branch = tk.StringVar()
    ttk.Radiobutton(infoPage, text="Stable", variable=branch, value="main").pack(pady=5, anchor="w", padx=10)
    ttk.Radiobutton(infoPage, text="Experimental (development)", variable=branch, value="experimental").pack(pady=5, anchor="w", padx=10)
    
    while branch.get() == "":
        root.update()
    
    for child in infoPage.winfo_children():
        child.destroy()
    
    # endregion
    
    # region Console
    
    ttk.Label(infoPage, text="The app is now being installed...", font=("Roboto", 16, "bold")).pack(pady=5, anchor="center", padx=10)
    console = tk.Text(infoPage, width=600, height=520, border=0, highlightthickness=0, background="#0d0d0d", foreground="#ffffff", font=("Roboto", 10))
    console.pack(pady=5, anchor="center", padx=10)
    
    def AddLineToConsole(line):
        console.insert("end", line + "\n")
        console.see("end")
        root.update()
        infoPage.update()
    
    # endregion
    
    # region Virtual environment
    
    # Check for a virtual environment
    AddLineToConsole("Checking for a virtual environment...")
    if os.path.exists("venv/Scripts/activate"):
        # Virtual environment exists
        UpdateProgress(1, 0, 0)
        AddLineToConsole("> Virtual environment exists")
        
    else:
        # Virtual environment does not exist
        UpdateProgress(0, 1, 0)   
        AddLineToConsole("> Virtual environment does not exist")

    # endregion

    # region Git

    AddLineToConsole("\nChecking git...")
    foundGit = CheckGit()
    if not foundGit:
        AddLineToConsole("> Git not found")
        AddLineToConsole("   > Please install git and run the installer again.")
        UpdateProgress(1, 0, 1, True)
        
        import time
        waitTime = 5
        startTime = time.time()
        AddLineToConsole(f"   > Opening download page in {round(5 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(1, 0, round((time.time() - startTime) / waitTime * 100), True)
            pass
             
        try:
            import webbrowser
        except:
            os.system("pip install webbrowser")
            import webbrowser

        webbrowser.open("https://gitforwindows.org/")
        
        waitTime = 10
        startTime = time.time()
        AddLineToConsole(f"   > Closing in {round(8 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(1, 0, round((time.time() - startTime) / waitTime * 100), True)
            pass
        
        quit()
    else:
        AddLineToConsole("> Git found")
        UpdateProgress(1, 1, 0)

    # endregion

    # region Connection
    
    # Check connection to the github servers
    AddLineToConsole("\nChecking connection to github...")
    try:
        urrlib.urlopen(APP_URL)
        AddLineToConsole("> Connection to github successful")
        UpdateProgress(1, 2, 0)
    except:
        AddLineToConsole("> Connection to github failed")
        AddLineToConsole("   > Please check your internet connection and try again.")
        UpdateProgress(1, 2, 1, True)
        
        import time
        
        waitTime = 10
        startTime = time.time()
        AddLineToConsole(f"   > Closing in {round(8 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(1, 2, round((time.time() - startTime) / waitTime * 100), True)
            pass
        
        quit()
    
    # endregion

    # region Check App
    
    def DownloadApp():
        UpdateProgress(1, 3, 0)
        AddLineToConsole("\nPlease wait, downloading the app...")
        AddLineToConsole("THE INSTALLER WILL BE UNRESPONSIVE, CHECK THE ACTUAL CONSOLE FOR PROGRESS")
        
        os.system("git clone -b " + branch.get() + " " + APP_URL + " app")
        
        pass
    
    AddLineToConsole("\nChecking app...")
    
    if os.path.exists("app/requirements.txt"):
        found = True
    else:
        found = False
        
    AddLineToConsole("> App found" if found else "> App not found")
    
    if found:
        from tkinter import messagebox
        if messagebox.askokcancel("App", "The app was already found, do you want to re-download it?"):
            import shutil
            shutil.rmtree("app")
            DownloadApp()
    
    else:
        DownloadApp()
    
    UpdateProgress(1, 4, 0)
    
    # endregion

    # region Check Download
    
    AddLineToConsole("\nChecking app...")
    if os.path.exists("app/requirements.txt"):
        AddLineToConsole("> App valid")
    else:
        AddLineToConsole("> App not valid")
        AddLineToConsole("   > Please check the console for any errors!")
    
        waitTime = 12
        startTime = time.time()
        AddLineToConsole(f"   > Closing in {round(8 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(1, 4, round((time.time() - startTime) / waitTime * 100), True)
            pass
        
        quit()
    
    UpdateProgress(2, 0, 0)
    
    # endregion

    # region Update pip
    
    dir = os.path.dirname(os.path.realpath(__file__))
    
    AddLineToConsole("\nPlease wait, updating pip...")
    
    if os.system(f"{dir}/venv/Scripts/python -m pip install --upgrade pip") != 0:
        AddLineToConsole("   > Error while updating pip!")
        AddLineToConsole("   > Please check the console for any errors!")
        
        waitTime = 12
        startTime = time.time()
        AddLineToConsole(f"   > Closing in {round(8 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(2, 1, round((time.time() - startTime) / waitTime * 100), True)
            pass
        
        quit()
    
    else:
        AddLineToConsole("> Done")
        
    UpdateProgress(2, 1, 0)
    
    # endregion

    # region Download Requirements
    
    requirements = open("app/requirements.txt", "r").read().split("\n")
    amount = len(requirements)
    
    AddLineToConsole("\nPlease wait, installing requirements...")
    
    
    try:
        for i in range(amount):
            UpdateProgress(2, 1, round(i / amount * 100))
            AddLineToConsole(f"Installing {requirements[i]}...")
            os.system(f"{dir}/venv/Scripts/pip install {requirements[i]}")
    except:
        AddLineToConsole("   > Error while installing!")
        AddLineToConsole("   > Please check the console for any errors!")
        
        waitTime = 12
        startTime = time.time()
        AddLineToConsole(f"   > Closing in {round(8 - (time.time() - startTime), 1)} seconds...")
        while time.time() - startTime < waitTime:
            UpdateProgress(2, 1, round((time.time() - startTime) / waitTime * 100), True)
            pass
        
        quit()
        
    UpdateProgress(3, 0, 0)
    
    # endregion

    # region Cleanup
    
    AddLineToConsole("\nPlease wait, clearing pip cache...")
    os.system(f"{dir}/venv/Scripts/pip cache purge")
    
    AddLineToConsole("\nPlease wait, creating .bat files...")
    with open("run.bat", "w") as f:
        f.write(fr'cmd /k "cd {dir}/venv/Scripts & .\activate & cd {dir}/app & {dir}/venv/Scripts/python main.py & pause & exit" & exit')
        AddLineToConsole("Created run.bat, to run the app easier.")
    
    with open("update.bat", "w") as f:
        f.write(fr'cmd /k "cd {dir}/venv/Scripts & .\activate & cd {dir}/app & git stash & git pull & pause & exit" & exit')
        AddLineToConsole("Created update.bat, to update the app easier.")
        
    with open("activate.bat", "w") as f:
        if os.name == "nt":
            f.write("@echo off\n")
            string = "cmd /k"
            string += fr'"cd "{dir}/venv/Scripts" & .\activate.bat"'
            f.write(string)
        else:
            f.write(f"cd {dir}/venv/Scripts & ./activate")
            
        AddLineToConsole("Created activate.bat, to activate the virtual environment easier.")
        
    UpdateProgress(4, 0, 0)
    
    AddLineToConsole("\nInstallation complete!")
    AddLineToConsole("You can now close this installer and run the run.bat file to open the app.")
    
    # endregion

# endregion

# This button needs to be after the functions
ttk.Button(infoPage, text="Begin", command=InstallSequence, width=200).pack(pady=5, anchor="w", padx=10)

root.mainloop()
