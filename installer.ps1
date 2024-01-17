#Check for admin
if ((New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
    } else {
        Write-Error "Please run menu.exe as administrator."
        Exit 1
}

#import the thingy
if (-not (Get-Module -ListAvailable -Name "PSScriptMenuGui")) {
    Install-Module -Name "PSScriptMenuGui" -Scope CurrentUser -Force
}

# Create a temporary directory
$tempDir = New-Item -ItemType Directory -Path "$env:TEMP\ScriptOutput" -Force
$scriptDirectory = $PWD.path

# Specify the file names
$fileName = "output.csv"
$installerbatFileName = "installer.bat"
$uninstallerbatFileName = "uninstaller.bat"
$debugbatFileName = "debug.bat"
$installpyFileName = "installer.py"

# Specify the path to the bat file
$installerFilePath = Join-Path $tempDir $installerbatFileName
$uninstallerFilePath = Join-Path $tempDir $uninstallerbatFileName
$debugfilepath = Join-Path $tempDir $debugbatFileName
$installpyFilePath = Join-Path $tempDir $installpyFileName

# Save the content to a CSV file inside the temporary directory
$csvPath = "$tempDir\$fileName"

$csvdata = @(
    "Install,cmd,$installerFilePath,,Installer,Opens the installer to download and install the app",
    "Utilities,cmd,./update.bat,,Update,Updates the app and installer to the latest version",
    "Utilities,cmd,$debugFilePath,,Debug,Creates a debug.txt file that includes information for devs to diagnose issues",
    "Utilities,cmd,./activate.bat,,Activate,Opens a CMD prompt in the VENV",
    "Uninstall,cmd,$uninstallerFilePath,,Uninstaller,Uninstalls the app"
)

$installerdata = @"
@echo off

winget --version >nul 2>&1 || (
    color 4 & echo WARNING, You do not have winget avialble on your system, This is most lickly because your on a windows version older then 2004. Please update your windows install and try again.
    pause
    exit 0
)

git --version >nul 2>&1 || (
    color 6 & echo Installing git, Please read and accept the windows smart screen prompt
    winget install Git.Git
    echo git is now installed
)

python --version >nul 2>&1 || (
    color 6 & echo Installing python, Please read and accept the windows smart screen prompt
    winget install -e --id Python.Python.3.11
    echo Python is now installed
)

python --version >nul 2>&1 || (
        color 2 & echo Successfully install all requirements please re run installer.bat
        pause
        exit 0
)
if exist version.txt (
    python $installpyFilePath
) else (
    git clone -b installer https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist.git
    xcopy Euro-Truck-Simulator-2-Lane-Assist\* . /E /H /C /Y
    rmdir /S /Q Euro-Truck-Simulator-2-Lane-Assist
    python $installpyFilePath
)

pause
"@

$uninstallerdata = @"
@echo off

set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "NORMAL=[0m"

set "APP_PATH=%~dp0"

echo.
set /p "confirmation=Are you sure you want to uninstall the app 'ETS2 Lane Assist' and all its data from the path '%APP_PATH%'? Type !YELLOW!\"uninstall\"!NORMAL! in the console and press enter to continue or press enter to exit the uninstaller.!YELLOW! "

if /i "!confirmation!"=="uninstall" (
    try (
        set "start_time=!time!"
        echo.
        echo %BLUE%Searching for files...%NORMAL%
        echo.
        echo App installed at "%APP_PATH%"
        echo.
        echo %BLUE%Searching for Start Menu entry...%NORMAL%
        if exist "C:\Users\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ETS2 Lane Assist.lnk" (
            echo %PURPLE%Found Start Menu entry at "C:\Users\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ETS2 Lane Assist.lnk"%NORMAL%
            echo Removing Start Menu entry...
            try (
                del "C:\Users\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ETS2 Lane Assist.lnk"
                echo %GREEN%Successfully removed Start Menu entry!%NORMAL%
            ) catch (
                echo %RED%Failed to remove Start Menu entry!%NORMAL%
            )
        ) else (
            echo %BLUE%Start Menu entry not found!%NORMAL%
        )
        echo.
        echo %BLUE%Searching for Desktop shortcut...%NORMAL%
        if exist "C:\Users\%username%\OneDrive\Desktop\ETS2 Lane Assist.Ink" (
            echo %PURPLE%Found Desktop shortcut at "C:\Users\%username%\OneDrive\Desktop\ETS2 Lane Assist.Ink"%NORMAL%
            echo Removing Desktop shortcut...
            try (
                del "C:\Users\%username%\OneDrive\Desktop\ETS2 Lane Assist.Ink"
                echo %GREEN%Successfully removed Desktop shortcut!%NORMAL%
            ) catch (
                echo %RED%Failed to remove Desktop shortcut!%NORMAL%
            )
        ) else (
            echo %BLUE%Desktop shortcut not found!%NORMAL%
        )
        echo.
        try (
            set "STEAM_PATH=!SteamPath!"
        ) catch (
            set "STEAM_PATH=c:\program files (x86)\steam"
        )
        set "ETS2_PATH=!STEAM_PATH!\steamapps\common\Euro Truck Simulator 2"
        set "ATS_PATH=!STEAM_PATH!\steamapps\common\American Truck Simulator"

        if exist "!ETS2_PATH!" (
            echo %PURPLE%Found Euro Truck Simulator 2 at "!ETS2_PATH!"%NORMAL%
            echo Searching for API and SDK in Euro Truck Simulator 2 path...
            if exist "!ETS2_PATH!\bin\win_x64\plugins\input_semantical.dll" (
                echo Found input_semantical.dll in "!ETS2_PATH!\bin\win_x64\plugins\input_semantical.dll"
                echo Removing input_semantical.dll...
                try (
                    del "!ETS2_PATH!\bin\win_x64\plugins\input_semantical.dll"
                    echo %GREEN%Successfully removed input_semantical.dll!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove input_semantical.dll!%NORMAL%
                )
            ) else (
                echo %BLUE%input_semantical.dll not found!%NORMAL%
            )
            if exist "!ETS2_PATH!\bin\win_x64\plugins\scs-telemetry.dll" (
                echo Found scs-telemetry.dll in "!ETS2_PATH!\bin\win_x64\plugins\scs-telemetry.dll"
                echo Removing scs-telemetry.dll...
                try (
                    del "!ETS2_PATH!\bin\win_x64\plugins\scs-telemetry.dll"
                    echo %GREEN%Successfully removed scs-telemetry.dll!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove scs-telemetry.dll!%NORMAL%
                )
            ) else (
                echo %BLUE%scs-telemetry.dll not found!%NORMAL%
            )
            if exist "!ETS2_PATH!\bin\win_x64\plugins" (
                echo Found plugins folder in "!ETS2_PATH!\bin\win_x64\plugins"
                echo Removing plugins folder...
                try (
                    rmdir /s /q "!ETS2_PATH!\bin\win_x64\plugins"
                    echo %GREEN%Successfully removed plugins folder!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove plugins folder!%NORMAL%
                )
            )
        ) else (
            echo %PURPLE%Euro Truck Simulator 2 not found!%NORMAL%
        )
        echo.
        if exist "!ATS_PATH!" (
            echo %PURPLE%Found American Truck Simulator at "!ATS_PATH!"%NORMAL%
            echo Searching for API and SDK in American Truck Simulator path...
            if exist "!ATS_PATH!\bin\win_x64\plugins\input_semantical.dll" (
                echo Found input_semantical.dll in "!ATS_PATH!\bin\win_x64\plugins\input_semantical.dll"
                echo Removing input_semantical.dll...
                try (
                    del "!ATS_PATH!\bin\win_x64\plugins\input_semantical.dll"
                    echo %GREEN%Successfully removed input_semantical.dll!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove input_semantical.dll!%NORMAL%
                )
            ) else (
                echo %BLUE%input_semantical.dll not found!%NORMAL%
            )
            if exist "!ATS_PATH!\bin\win_x64\plugins\scs-telemetry.dll" (
                echo Found scs-telemetry.dll in "!ATS_PATH!\bin\win_x64\plugins\scs-telemetry.dll"
                echo Removing scs-telemetry.dll...
                try (
                    del "!ATS_PATH!\bin\win_x64\plugins\scs-telemetry.dll"
                    echo %GREEN%Successfully removed scs-telemetry.dll!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove scs-telemetry.dll!%NORMAL%
                )
            ) else (
                echo %BLUE%scs-telemetry.dll not found!%NORMAL%
            )
            if exist "!ATS_PATH!\bin\win_x64\plugins" (
                echo Found plugins folder in "!ATS_PATH!\bin\win_x64\plugins"
                echo Removing plugins folder...
                try (
                    rmdir /s /q "!ATS_PATH!\bin\win_x64\plugins"
                    echo %GREEN%Successfully removed plugins folder!%NORMAL%
                ) catch (
                    echo %RED%Failed to remove plugins folder!%NORMAL%
                )
            )
        ) else (
            echo %PURPLE%American Truck Simulator not found!%NORMAL%
        )
        echo.
        if exist "!APP_PATH!\app" (
            echo %PURPLE%Found app folder at "!APP_PATH!\app"%NORMAL%
            echo Removing app folder...
            try (
                rmdir /s /q "!APP_PATH!\app"
                echo %GREEN%Successfully removed app folder!%NORMAL%
            ) catch (
                echo %RED%Failed to remove app folder!%NORMAL%
            )
        ) else (
            echo %PURPLE%App folder not found!%NORMAL%
        )
        echo.
        if exist "!APP_PATH!\venv" (
            echo %PURPLE%Found venv folder at "!APP_PATH!\venv"%NORMAL%
            echo Removing venv folder...
            try (
                rmdir /s /q "!APP_PATH!\venv"
                echo %GREEN%Successfully removed venv folder!%NORMAL%
            ) catch (
                echo %RED%Failed to remove venv folder!%NORMAL%
            )
        ) else (
            echo %PURPLE%Venv folder not found!%NORMAL%
        )
        echo.
        if exist "!APP_PATH!" (
            echo %PURPLE%Found main folder at "!APP_PATH!"%NORMAL%
            echo Removing main folder...
            try (
                rmdir /s /q "!APP_PATH!"
                echo %GREEN%Successfully removed main folder!%NORMAL%
            ) catch (
                echo %RED%Failed to remove main folder!%NORMAL%
            )
        ) else (
            echo %PURPLE%Main folder not found!%NORMAL%
        )
        echo.
        echo %GREEN%Finished! (!time! - !start_time!s)%NORMAL%
        pause
    ) catch (
        echo %RED%
        echo Stopped uninstall process because of the following error:
        echo %NORMAL%!errorlevel!
    )
) else (
    echo %GREEN%Aborted uninstall process.%NORMAL%
    pause
)
echo %NORMAL%

"@

if ((Get-Item .).Name -eq 'goodgirl') {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(':3', 'Good girl', 'OK', 'Information')
}

$debugdata = @"
@echo off

REM Specify the path to the version.txt file
set "version_file=app\version.txt"
REM Specify the path to the log file
set "log_file=app\log.txt"
REM Specify the path to the settings file
set "settings_file=app\profiles\settings.json"
REM Specify the path to the debug.txt file
set "debug_file=debug.txt"

REM Clear the debug.txt file
echo. > "%debug_file%"

REM Check if version.txt exists
if not exist "%version_file%" (
    echo Error: %version_file% not found! >> "%debug_file%"
    echo Error: %version_file% not found!
    exit /b 1
)

REM Display the content of version.txt
set /p version_content=<"%version_file%"
echo Version content: %version_content% >> "%debug_file%"

REM Check if log.txt exists
if not exist "%log_file%" (
    echo Error: %log_file% not found! >> "%debug_file%"
    echo Error: %log_file% not found!
    exit /b 1
)

REM Check if settings.txt exists
if not exist "%settings_file%" (
    echo Error: %settings% not found! >> "%debug_file%"
    echo Error: %settings% not found!
    exit /b 1
)




REM Check if Python is installed
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! >> "%debug_file%"
    echo Python is not installed!
    exit /b 1
)

REM Get Python version
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "python_version=%%v"

REM Display Python version
echo Python version: %python_version%
echo Python version: %python_version% >> "%debug_file%"

REM Display gpus 
echo Gpu: >> "%debug_file%
echo --------------------------- >> "%debug_file%"
wmic path win32_videocontroller get caption >> "%debug_file%"
REM Display the content of log.txt
echo END FILE >> "%debug_file%"
echo Settings file: >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
type "%settings_file%" >> %debug_file%"

REM Display the content of log.txt
echo END FILE >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
echo Log file: >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
type "%log_file%" >> %debug_file%"
echo END FILE >> "%debug_file%"
exit /b 0

"@

$installpydata = @"
import sys
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import threading
import time
from tkinter import ttk
import json

def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

checkupdate = 1

try:
    import requests
except:
    checkupdate = 0
    printRed("Requests module not found. Installing...")
    os.system("pip install requests")
    printGreen("Successfully installed requests, Auto updating will check for updates the next time the app is run")

APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/"
FOLDER = r"$scriptDirectory"


with open("version.txt", 'r') as file:
    VERSION = file.read()
    

    

os.chdir(FOLDER)

def UpdateChecker():
    currentVer = VERSION.split(".")

    url = "https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/installer/version.txt"
    try:
        remoteVer = requests.get(url).text.strip().split(".")
    except:
        print("Failed to check for updates")
        print("Please check your internet connection and try again later")
        return
    if currentVer[0] < remoteVer[0]:
        update = True
    elif currentVer[1] < remoteVer[1]:
        update = True
    elif currentVer[2] < remoteVer[2]:
        update = True
    else:
        update = False

    if update:
        from tkinter import messagebox
        if messagebox.askokcancel("Updater", (f"We have detected an installer update, do you want to install it?\nCurrent - {'.'.join(currentVer)}\nUpdated - {'.'.join(remoteVer)}")):
            try:
                os.system("git stash")
                os.system("git pull")
            except:
                print("Failed to update")
            if messagebox.askyesno("Updater", ("The update has been installed and the application needs to be restarted. Do you want to quit the installer?")):
                quit()
        else:
            pass

if checkupdate == 1:
    UpdateChecker()

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

def CreateShortcut(path, name, icon=""):
    try:
        import pyshortcuts
    except:
        os.system("pip install pyshortcuts")
        import pyshortcuts
        
    if icon == "":
        pyshortcuts.make_shortcut(path, name=name)
    else:
        pyshortcuts.make_shortcut(path, name=name, icon=icon)

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
    - Shortucts

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
    printRed(f"Your current Python version is {sys.version_info[0]}.{sys.version_info[1]}.")
    printRed("This app requires a Python version above 3.9.x and below 3.12.x to create the correct virtual environment.")
    printRed("Please uninstall python by searching for python in control panel that has been opened for you and rerun the app to have the app to auto install the correct version.")
    os.system("control appwiz.cpl")
    input("If you would like to install python yourself, I don't know why you would. Are you telling me your going to waste 5 minutes of my time on making a auto installer for python for you to just install it yourself? Fine, If you really want to install python yourself hit enter.")
    import webbrowser
    webbrowser.open("https://www.python.org/downloads/release/python-3116")
    quit()

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
ttk.Label(root, text="ETS2 Lane Assist   \u00a9Tumppi066 - 2023", font=("Roboto", 8)).grid(row=2, sticky="s", padx=10, pady=16)
ttk.Label(root, text=f"Installer version {VERSION.strip()}", font=("Roboto", 8)).grid(row=2, sticky="n", padx=10, pady=0)
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
    "Preferences": [
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
        f.write(fr'cmd /k "cd {dir}/venv/Scripts & .\activate & cd {dir}/app & git stash & git pull & exit" & cd {dir} & git stash & git pull & pause')
        AddLineToConsole("Created update.bat, to update the app easier.")
        
    with open("activate.bat", "w") as f:
        if os.name == "nt":
            f.write("@echo off\n")
            string = "cmd /k"
            string += fr'"cd "{dir}/venv/Scripts" & .\activate.bat & cd {dir}"'
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
    
    def themeset():
        if str(theme.get()) == "Dark":
            sv_ttk.set_theme("dark")
        if str(theme.get()) == "Light":
            sv_ttk.set_theme("light")

    preferenceslabel = ttk.Label(preferenceFrame, text="Preferences", font=("Roboto", 16, "bold"))
    preferenceslabel.grid(columnspan=3, row=0, sticky='n', padx=150, pady=0)
    canchange = ttk.Label(preferenceFrame, text="You can change these in the settings later", font=("Roboto", 10))
    canchange.grid(columnspan=3, row=1, sticky='n', padx=150, pady=5)

    #selectthemelabel = ttk.Label(preferenceFrame, text="Select Theme", font=("Roboto", 12))
    #selectthemelabel.grid(columnspan=3, row=2, sticky='w', pady=5, padx=10)
    #theme = tk.StringVar()
    #dark = ttk.Radiobutton(preferenceFrame, text="Dark", variable=theme, value="Dark", command=themeset)
    #dark.grid(columnspan=3, row=3, sticky='w', pady=5, padx=10)
    #light = ttk.Radiobutton(preferenceFrame, text="Light", variable=theme, value="Light", command=themeset)
    #light.grid(columnspan=3, row=4, sticky='w', pady=5, padx=10)

    selectotherslabel = ttk.Label(preferenceFrame, text="Other Settings", font=("Roboto", 12))
    selectotherslabel.grid(columnspan=3, row=5, sticky='w', pady=5, padx=10)

    shortcut = tk.IntVar()
    iconcheckbox = ttk.Checkbutton(preferenceFrame, text="Enable Desktop and Start Menu Shortcuts", variable=shortcut)
    iconcheckbox.grid(columnspan=3, row=6, sticky='w', pady=5, padx=10)
    shortcut.set(1)
    iconcheckbox.var = shortcut

    # Runs when the confirm button is pressed
    def confirmselection():
        #themesave = (str(theme.get()))
        FOLDER = os.path.dirname(__file__)
        #if themesave == "": 
        #    printRed("Please select a theme")
        #    return
        
        UpdateProgress(5, 0, 0.5)
        pleasewait = ttk.Label(preferenceFrame, text="Please wait, saving preferences", font=("Roboto", 15, "bold"))
        pleasewait.grid(columnspan=3, row=8, padx=0, pady=15)
        root.update()

        if shortcut.get() == 1:
            try:
                CreateShortcut(f"{dir}/run.bat", "ETS2 Lane Assist", f"{dir}/app/assets/favicon.ico")
                printGreen("Shortcut created")
            except:
                printRed("Could not create shortcut")
                AddLineToConsole("Could not create shortcut")
        else:
            print("Shortcut not created")
            pass

        #time.sleep(2)
        #if themesave == "Dark": 
        #    CreateSettings("User Interface", "Theme", "dark")
        #elif themesave == "Light": 
        #    CreateSettings("User Interface", "Theme", "light")
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
        AddLineToConsole("You can now close this installer and use the run.bat file to open the app.")
        AddLineToConsole("!! You can also use the shortcut we created in your windows start menu (win + type ETS2) !!")
        printGreen("Preferences Saved")
        printGreen("Installation complete!")
        printGreen("You can now close this installer and use the run.bat file to open the app.")
        if shortcut.get() == 1:
            printGreen("You can also use the shortcut we created in your windows start menu.")
        UpdateProgress(6, 0, 0)
    confirm = ttk.Button(preferenceFrame, text="Confirm", width=64, command=confirmselection)
    confirm.grid(row=7, columnspan=3, padx=15, pady=10)

    # endregion
# endregion

# This button needs to be after the functions
begin = ttk.Button(infoPage, text="Begin", command=InstallSequence, width=64)
begin.grid(pady=5, sticky="w", padx=9)

root.mainloop()

"@



# Save the content to a CSV file inside the temporary directory
$csvContent = "Section,Method,Command,Arguments,Name,Description`n" + ($csvdata -join "`n")
$csvContent | Set-Content -Path $csvPath

# Save the content to the bat file
$installerdata | Set-Content -Path $installerFilePath
$uninstallerdata | Set-Content -Path $uninstallerFilePath
$debugdata | Set-Content -Path $debugfilepath
$installpydata | Set-Content -Path $installpyFilePath

# Display the path to the generated CSV file and bat file
#Write-Host "CSV file created at: $csvPath"
#Write-Host "Installer file created at: $installerFilePath"
#Write-Host "Uninstaller file created at: $uninstallerFilePath"
#Write-host "Debug file created at: $debugfilepath"
#Write-host "Installpy file created at: $installpyFilePath"

# Run display
Show-ScriptMenuGui -windowTitle "ETS2LA Installer" -csvPath $csvPath

# Remove the files
Remove-Item -Path $csvPath -Force
#Write-Host "CSV file removed at: $csvPath"
Remove-Item -Path $installerFilePath -Force
#Write-Host "Bat file removed at: $installerFilePath"
Remove-Item -Path $uninstallerFilePath -Force
#Write-Host "Bat file removed at: $uninstallerFilePath"
Remove-Item -Path $debugfilepath -Force
#Write-Host "Bat file removed at: $debugfilepath"
Remove-Item -Path $installpyFilePath -Force
#Write-Host "Installpy file removed at: $installpyFilePath"