import sys
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import threading
import time
from tkinter import ttk
import json

APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/"
FOLDER = os.path.dirname(__file__)
os.chdir(FOLDER)

def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

def EnsureFile(file):
    try:
        with open(file, "r") as f:
            pass
    except:
        with open(file, "w") as f:
            f.write("{}")

# Change settings in the json file
def UpdateSettings(category, name, data):
    try:
        profile = FOLDER + r"\app\profiles\settings.json"
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

        settings[category][name] = data
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except Exception as ex:
        print(ex.args)

def CreateSettings(category, name, data):
    try:
        profile = FOLDER + r"\app\profiles\settings.json"
        EnsureFile(profile)
        with open(profile, "r") as f:
            settings = json.load(f)

        # If the setting doesn't exist then create it 
        if not category in settings:
            settings[category] = {}
            settings[category][name] = data
        
        # If the setting exists then overwrite it
        if category in settings:
            settings[category][name] = data
            
        with open(profile, "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except Exception as ex:
        print(ex.args)

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
4. Ask user for settings/preferences
    - Theme
    - Color Theme

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

# Check python version (must be > 3.9.x and < 3.12.x)
if sys.version_info[0] != 3 or sys.version_info[1] < 9 or sys.version_info[1] > 11:
    printRed("This app requires a Python version above 3.9.x and below 3.12.x to create the correct virtual environment.")
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

# Check for Pillow
try:
    from PIL import ImageTk, Image
except:
    print("Please wait installing pillow...")
    Install("pillow")
    printGreen("> Done")
    from PIL import ImageTk, Image

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
root.resizable(False, False)
width = 775
height = 640
root.geometry(f"{width}x{height}")
sv_ttk.set_theme("dark")

# Bottom text
ttk.Label(root, text="ETS2 Lane Assist   ©Tumppi066 - 2023", font=("Roboto", 8)).grid(row=2, sticky="s", padx=10, pady=16)
ttk.Label(root, text="Installer version 0.2.0", font=("Roboto", 8)).grid(row=2, sticky="n", padx=10, pady=0)
progressBar = ttk.Progressbar(root, mode="determinate", length=width)
progressBar.grid(row=0, sticky="n", padx=0, pady=0)

# Left button bar
progressFrame = ttk.LabelFrame(root, text="Progress", width=170, height=580)
progressFrame.pack_propagate(False)
progressFrame.grid_propagate(False)

progressFrame.grid(row=1, sticky="w", padx=10, pady=10)

# Plugin frame
statusFrame = ttk.LabelFrame(root, text="Status", width=570, height=580)
statusFrame.pack_propagate(False)
statusFrame.grid_propagate(False)

statusFrame.grid(row=1, sticky="e", padx=10, pady=10)

# Info page
infoPage = tk.Canvas(statusFrame, width=550, height=540, border=0, highlightthickness=0)
infoPage.pack_propagate(False)
infoPage.grid_propagate(False)

infoPage.grid(padx=10)

# Add a label describing what the installer will do
ttk.Label(infoPage, text="Welcome!", font=("Roboto", 20, "bold")).grid(pady=10, sticky="w", padx=10)
ttk.Label(infoPage, text="The installer will create a virtual environment for the app's python version.", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text="The app will be installed in the same folder as the installer.", font=("Roboto", 10, "bold")).grid(pady=2, sticky="w",  padx=10)
ttk.Label(infoPage, text="", font=("Roboto", 10)).grid(pady=2)
ttk.Label(infoPage, text="Following are the steps the app will take to install itself:", font=("Roboto", 10, "bold")).grid(pady=5, sticky="w", padx=10)
ttk.Label(infoPage, text="1. Create a virtual python environment from your current python version", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text="2. Download the app from github", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text="3. Install the requirements from requirements.txt (to the virtual env)", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text="4. Create .bat files for easy access to the app's functions", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text="5. Ask the user for a theme and color for the app", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)
ttk.Label(infoPage, text=" ", font=("Roboto", 10)).grid(pady=2, sticky="w", padx=10)

infoPage.grid()
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
    "Prefereences": [
        "Theme",
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
    
    for i in range(len(states)):
        keys = list(states.keys())
        ttk.Label(progressFrame, text=keys[i], font=("Calibri", 14, "bold")).pack(pady=5, anchor="n", padx=10)
        
        for j in range(len(states[keys[i]])):
            if j == value and i == state:
                ttk.Label(progressFrame, text="> " + states[keys[i]][j] + " <", font=("Roboto", 10, "bold"), foreground="#cccc00" if not problem else "#b30000").pack(pady=5, anchor="n", padx=5)
            elif j < value and i == state or i < state:
                ttk.Label(progressFrame, text="✓ " + states[keys[i]][j], font=("Roboto", 8, "bold"), foreground="green").pack(pady=5, anchor="n", padx=5)
            else:
                ttk.Label(progressFrame, text=states[keys[i]][j], font=("Roboto", 8)).pack(pady=5, anchor="n", padx=5)
        ttk.Label(progressFrame, text="", font=("Roboto", 6)).pack(pady=0, anchor="n", padx=5)
    
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
        
    ttk.Label(infoPage, text="Please select the branch you want to install:", font=("Roboto", 16, "bold")).grid(pady=5, sticky="w", padx=10)
    branch = tk.StringVar()
    ttk.Radiobutton(infoPage, text="Stable", variable=branch, value="main").grid(pady=5, sticky="w", padx=10)
    ttk.Radiobutton(infoPage, text="Experimental (development)", variable=branch, value="experimental").grid(pady=5, sticky="w", padx=10)
    
    while branch.get() == "":
        root.update()
    
    for child in infoPage.winfo_children():
        child.destroy()
    
    # endregion
    
    # region Console
    
    installlabel = ttk.Label(infoPage, text="The app is now being installed...", font=("Roboto", 16, "bold"))
    installlabel.grid(sticky='n', pady=5)
    console = tk.Text(infoPage, width=82, height=31, border=0, highlightthickness=0, background="#0d0d0d", foreground="#ffffff", font=("Roboto", 10))
    console.grid(sticky='n', padx=1, pady=20)
    
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
        AddLineToConsole("   > Creating a virtual environment...")
        venv.create("venv", with_pip=True)

    # endregion
    # region Git

    AddLineToConsole("\nChecking git...")
    foundGit = CheckGit()
    if not foundGit:
        AddLineToConsole("> Git not found")
        AddLineToConsole("   > Please install git and run the installer again.")
        UpdateProgress(1, 0, 1, True)
        
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
            os.system("rmdir /s /q app\.git")
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
    
    requirements = open(f"{dir}/app/requirements.txt", "r").read().split("\n")
    amount = len(requirements)
    
    AddLineToConsole("\nPlease wait, installing requirements...")
    
    
    try:
        for i in range(amount):
            UpdateProgress(2, 1, round(i / amount * 100))
            if "--upgrade --no-cache-dir gdown" in requirements[i]:
                AddLineToConsole(f"Installing gdown...")
            else:
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
    # endregion

    # region Preferences
    installlabel.place_forget()
    console.place_forget()
    infoPage.place_forget()
    statusFrame.place_forget()

    preferenceFrame= ttk.LabelFrame(root, text="Preferences", width=570, height=580)
    preferenceFrame.pack_propagate(False)
    preferenceFrame.grid_propagate(False)
    preferenceFrame.grid(row=1, sticky="e", padx=10, pady=10)

    global sunvalleyimg
    global forestimg
    global azureimg

    os.chdir(FOLDER)
    image1 = Image.open(r"app\assets\installer\SunValley.jpg")
    image2 = Image.open(r"app\assets\installer\Forest.jpg")
    image3 = Image.open(r"app\assets\installer\Azure.jpg")
    resizeimage1 = image1.resize((135, 135))
    resizeimage2 = image2.resize((135, 135))
    resizeimage3 = image3.resize((135, 135))
    sunvalleyimg = ImageTk.PhotoImage(resizeimage1)
    forestimg = ImageTk.PhotoImage(resizeimage2)
    azureimg = ImageTk.PhotoImage(resizeimage3)
    
    def themeset():
        if str(theme.get()) == "Dark":
            sv_ttk.set_theme("dark")
        if str(theme.get()) == "Light":
            sv_ttk.set_theme("light")

    preferenceslabel = ttk.Label(preferenceFrame, text="Preferences", font=("Roboto", 16, "bold"))
    preferenceslabel.grid(columnspan=3, row=0, sticky='n', padx=150, pady=0)
    canchange = ttk.Label(preferenceFrame, text="You can change these in the settings later", font=("Roboto", 10))
    canchange.grid(columnspan=3, row=1, sticky='n', padx=150, pady=5)

    selectthemelabel = ttk.Label(preferenceFrame, text="Select Theme", font=("Roboto", 12))
    selectthemelabel.grid(columnspan=3, row=2, sticky='w', pady=5, padx=10)
    theme = tk.StringVar()
    dark = ttk.Radiobutton(preferenceFrame, text="Dark", variable=theme, value="Dark", command=themeset)
    dark.grid(columnspan=3, row=3, sticky='w', pady=5, padx=10)
    light = ttk.Radiobutton(preferenceFrame, text="Light", variable=theme, value="Light", command=themeset)
    light.grid(columnspan=3, row=4, sticky='w', pady=5, padx=10)

    selectcolorthemelabel = ttk.Label(preferenceFrame, text="Select Color Theme", font=("Roboto", 12))
    selectcolorthemelabel.grid(columnspan=3, row=5, sticky='w', pady=10, padx=10)
    colortheme = tk.StringVar()
    sunvalley = ttk.Radiobutton(preferenceFrame, text="Sun Valley", image=sunvalleyimg, compound="bottom", variable=colortheme, value="sunvalley")
    sunvalley.grid(row=6, column=0, pady=10)
    forest = ttk.Radiobutton(preferenceFrame, text="Forest", image=forestimg,  compound="bottom", variable=colortheme, value="forest")
    forest.grid(row=6, column=1, pady=10)
    azure = ttk.Radiobutton(preferenceFrame, text="Azure", image=azureimg,  compound="bottom", variable=colortheme, value="azure")
    azure.grid(row=6, column=2, pady=10)

    # Runs when the confirm button is pressed
    def confirmselection():
        themesave = (str(theme.get()))
        colorthemesave = (str(colortheme.get()))
        FOLDER = os.path.dirname(__file__)
        if themesave == "": 
            printRed("Please select a theme")
            return
        if colorthemesave == "": 
            printRed("Please select a color theme")
            return
        UpdateProgress(5, 0, 0.5)
        pleasewait = ttk.Label(preferenceFrame, text="Please wait, saving preferences", font=("Roboto", 15, "bold"))
        pleasewait.grid(columnspan=3, row=8, padx=0, pady=15)
        root.update()
        if colorthemesave == "sunvalley": 
            CreateSettings("User Interface", "ColorTheme", "SunValley")
        elif colorthemesave == "azure": 
            CreateSettings("User Interface", "ColorTheme", "Azure")
        elif colorthemesave == "forest": 
            CreateSettings("User Interface", "ColorTheme", "Forest")
        time.sleep(2)
        if themesave == "Dark": 
            CreateSettings("User Interface", "Theme", "dark")
        elif themesave == "Light": 
            CreateSettings("User Interface", "Theme", "light")
        restoreconsole()

    # Restore the console after preferences are saved
    def restoreconsole():
        sv_ttk.set_theme("dark")
        preferenceFrame.destroy()
        infoPage.grid(padx=10)
        statusFrame.grid(row=1, sticky="e", padx=10, pady=10)
        installlabel.grid(sticky='n', pady=5)
        console.grid(sticky='n', padx=1, pady=20)
        AddLineToConsole("\nPreferences Saved")
        AddLineToConsole("\nInstallation complete!")
        AddLineToConsole("You can now close this installer and run the run.bat file to open the app.")
        printGreen("Preferences Saved")
        printGreen("Installation complete!")
        printGreen("You can now close this installer and run the run.bat file to open the app.")
        UpdateProgress(6, 0, 0)
    confirm = ttk.Button(preferenceFrame, text="Confirm", width=64, command=confirmselection)
    confirm.grid(row=7, columnspan=3, padx=15, pady=10)

    # endregion
# endregion

# This button needs to be after the functions
begin = ttk.Button(infoPage, text="Begin", command=InstallSequence, width=64)
begin.grid(pady=5, sticky="w", padx=9)

root.mainloop()
