# Create a temporary directory
$tempDir = New-Item -ItemType Directory -Path "$env:TEMP\ScriptOutput" -Force
$tempDir -replace ' ', '` '
$scriptDirectory = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$scriptDirectory = $scriptDirectory.Replace("\InstallerSources", "")
# Specify the file names
$installerbatFileName = "installer.bat"
$installpyFileName = "installer.py"
$uninstallerpsFileName = "uninstaller.ps1"
$debugbatFileName = "debug.py"
$updatebatFileName = "update.bat"
$activatebatFileName = "activate.bat"
$SteamParserpyFileName = "SteamParser.py"

# Specify the path to the bat file
$installerFilePath = Join-Path $tempDir $installerbatFileName
$uninstallerFilePath = Join-Path $tempDir $uninstallerpsFileName
$debugfilepath = Join-Path $tempDir $debugbatFileName
$installpyFilePath = Join-Path $tempDir $installpyFileName
$updatebatFilePath = Join-Path $tempDir $updatebatFileName
$activatebatFilePath = Join-Path $tempDir $activatebatFileName
$SteamParserpyFilePath = Join-Path $tempDir $SteamParserpyFileName

$installerdata = @"
winget --version >nul 2>&1 || (
    color 4 & echo WARNING, You do not have winget avialble on your system, This is most likely because your on a windows version older then 2004. Please update your windows install and try again.
    pause
    exit 0
)

git --version >nul 2>&1 || (
    color 6 & echo Installing git, Please read and accept the windows smart screen prompt
    winget install Git.Git
    echo git is now installed
)

set python_version=cmd /k "python --version"

if not python_version (python --version >nul 2>&1 || (
        color 6 & echo Installing python, Please read and accept the windows smart screen prompt
        winget install -e --id Python.Python.3.11
        echo Python is now installed
    ))

python --version >nul 2>&1 || (
    color 2 & echo Successfully install all requirements please re run installer.bat
    pause
    exit 0
)
python $installpyFilePath

pause
"@
$uninstallerdataarray = '$tempDir =', "'$($tempDir)'", 
'$scriptDirectory = ', "'$($scriptDirectory)'",
@'
$SteamParser = "$tempDir\steamParser.py"
$PluginsFolderPath = "bin/win_x64/plugins"
$global:ETS2Path = $null
$global:ATSPath = $null
function FindGames() {
    $ScriptOutput = cmd.exe /c "python $SteamParser"
    $FoundGames = $ScriptOutput.Replace("[", "").Replace("]", "").Replace("'", "")
    Write-Host $FoundGames
    $FoundGames = $FoundGames -split ","
    
    $TempETS2Path = $FoundGames[0]
    if ($FoundGames[0] -eq "None") {
        Write-Host "ETS2 not found." -ForegroundColor Red
        $global:ETS2Path = "None"
    } else {
        Write-Host "ETS2 Path: $TempETS2Path" -ForegroundColor Green
        $global:ETS2Path = $TempETS2Path
    }
    $TempATSPath = $FoundGames[1].TrimStart(" ")
    if ($TempATSPath -eq "None") {
        Write-Host "ATS not found." -ForegroundColor Red
        $global:ATSPath = "None"
    } else {
        Write-Host "ATS Path: $TempATSPath" -ForegroundColor Green
        $global:ATSPath = $TempATSPath
    }
}

$username = [Environment]::UserName
$files_removed = 0
$confirmation = Read-Host "Are you sure you want to uninstall ETS2LA? This will remove all files, programs, shorcuts, and data associated with ETS2LA. Type yes to continue."
if ($confirmation -eq 'yes') { 
    Write-Host "Finding files..." -ForegroundColor Blue
    Write-Host ""

    # REMOVE START MENU ENTRY
    Write-Host "Searching for start menu entry..." -ForegroundColor Blue
    if (Test-Path -Path "C:\Users\$username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ETS2 Lane Assist.lnk") {
        Remove-Item -Path "C:\Users\$username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ETS2 Lane Assist.lnk"
        Write-Host "Start menu entry found and removed." -ForegroundColor Green
        $files_removed += 1
    } else {
        Write-Host "Start menu entry not found." -ForegroundColor Red
    }
    Write-Host ""

    # REMOVE DESKTOP SHORTCUT
    Write-Host "Searching for desktop shortcut..." -ForegroundColor Blue
    if (Test-Path -Path "C:\Users\$username\Desktop\ETS2 Lane Assist.lnk") {
        Remove-Item -Path "C:\Users\$username\Desktop\ETS2 Lane Assist.lnk"
        Write-Host "Desktop shortcut found and removed." -ForegroundColor Green
        $files_removed += 1
    } else {
        Write-Host "Desktop shortcut not found." -ForegroundColor Red
    }
    Write-Host ""

    # SEARCH FOR ETS2 AND ATS
    Write-Host "Searching for ETS2 and ATS..." -ForegroundColor Blue
    FindGames
    Write-Host ""

    # REMOVE ETS2LA FILES FROM ETS2
    if ($ETS2Path -ne "None") {
        Write-Host "Finding and removing all ETS2LA files from $($ETS2Path)" -ForegroundColor Blue
        if (Test-Path -Path "$ETS2Path\$PluginsFolderPath\input_semantical.dll") {
            try {
                Remove-Item -Path "$ETS2Path\$PluginsFolderPath\input_semantical.dll"
                Write-Host "Found and removed input SDK (input_semantical.dll)" -ForegroundColor Green
                $files_removed += 1
            } catch {
                Write-Host "Failed to find and remove input SDK (input_semantical.dll)" -ForegroundColor Red
            }
        } else {
            Write-Host "Input SDK not found (input_semantical.dll)" -ForegroundColor Red
        }

        if (Test-Path -Path "$ETS2Path\$PluginsFolderPath\scs-telemetry.dll") {
            try {
                Remove-Item -Path "$ETS2Path\$PluginsFolderPath\scs-telemetry.dll"
                Write-Host "Found and removed telemtry SDK (scs-telemetry.dll)" -ForegroundColor Green
                $files_removed += 1
            } catch {
                Write-Host "Failed to find and remove telemtry SDK (scs-telemetry.dll)" -ForegroundColor Red
            }
        } else {
            Write-Host "Telemetry SDK not found (scs-telemetry.dll)" -ForegroundColor Red
        }
        Write-Host "Removed all ETS2LA files from $ETS2Path" -ForegroundColor Green
    }

    Write-Host ""
    if ($ATSPath -ne "None") {
        Write-Host "Finding and removing all ETS2LA files from $($ATSPath)" -ForegroundColor Blue
        if (Test-Path -Path "$ATSPath\$PluginsFolderPath\input_semantical.dll") {
            try {
                Remove-Item -Path "$ATSPath\$PluginsFolderPath\input_semantical.dll"
                Write-Host "Found and removed input SDK (input_semantical.dll)" -ForegroundColor Green
                $files_removed += 1
            } catch {
                Write-Host "Failed to find and remove input SDK (input_semantical.dll)" -ForegroundColor Red
            }
        } else {
            Write-Host "Input SDK not found (input_semantical.dll)" -ForegroundColor Red
        }

        if (Test-Path -Path "$ATSPath\$PluginsFolderPath\scs-telemetry.dll") {
            try {
                Remove-Item -Path "$ATSPath\$PluginsFolderPath\scs-telemetry.dll"
                Write-Host "Found and removed telemtry SDK (scs-telemetry.dll)" -ForegroundColor Green
                $files_removed += 1
            } catch {
                Write-Host "Failed to find and remove telemtry SDK (scs-telemetry.dll)" -ForegroundColor Red
            }
        } else {
            Write-Host "Telemetry SDK not found (scs-telemetry.dll)" -ForegroundColor Red
        }
        Write-Host "Removed all ETS2LA files from $ATSPath" -ForegroundColor Green
    }

    # REMOVE ALL ETS2LA FILES FROM THE ETS2LA DIRECTORY
    Write-Host ""
    Set-Location $scriptDirectory
    Write-Host "Finding and removing all ETS2LA files from install folder..." -ForegroundColor Blue
    Write-Host "This may take a while, please be patient."
    Get-ChildItem -Path $path | ForEach-Object {
        if ($_.Name -eq "menu.exe" -or $_.Name -eq "installer.ps1") {
        } else {
            try {
                Remove-Item -Path $_.FullName -Recurse -Force -Confirm:$false
                Write-Host "$($_.Name) Removed!" -ForegroundColor Green
            } catch {
                Write-Host "Failed to remove $($_.Name)" -ForegroundColor Red
            }
        }   
    }

    # FINISH
    Write-Host ""
    Write-Host "Uninstallation complete." -ForegroundColor Green
    Write-Host "Found and removed $files_removed files." -ForegroundColor Green
    Write-Host "The installer will now self destruct after you click enter." -ForegroundColor Green
    Pause
    Remove-Item -Path "$path/menu.exe" -Force
    exit
} else {
    Write-Host "Aborting uninstallation."
    Pause
    exit
} 
'@

$debugdata = @"
import requests
import json
import platform
import subprocess 
import sys
import os
import tkinter as tk
from tkinter import ttk

def get_os_info():
    global oss
    global osversion
    global appversion
    global pythonversion
    global gitversion
    global cpu
    global gpu
    global logs
    global settings

    try:
        oss = platform.system()
    except:
        oss = "OS name not found."

    try:
        osversion = platform.version()
    except:
        osversion = "OS version not found"

    try:
        with open("app/version.txt", 'r') as file:
            appversion = file.read()
    except:
        appversion = "App version not found."

    try:
        pythonversion = platform.python_version()
    except:
        pythonversion = "Python Not Found"

    try:
        gitversion = os.popen('git --version').read()
    except:
        gitversion = "Git was not found."

    try:
        cpu = os.popen('wmic cpu get name').read()
    except:
        cpu = "No CPU Found."

    try:
        gpu = os.popen('wmic path win32_videocontroller get caption').read()
    except:
        gpu = "No GPU Found."

    try:
        with open("app/log.txt", 'r') as file:
            logsuncence = file.read()
        username = os.getlogin()
        logs = logsuncence.replace(username, "censored") 
    except:
        logs = "No log file found"

    try:
        with open("app/profiles/settings.json", 'r') as file:
            settingsuncence = file.read()
        username = os.getlogin()
        settings = settingsuncence.replace(username, "censored") 
    except:
        settings = "No settings file found."

    try:
        username = os.getlogin()
        with open(f"C:/Users/{username}/Documents/Euro Truck Simulator 2/game.log.txt", 'r') as file:
            gamesuncence = file.read()
        games = gamesuncence.replace(username, "censored") 
    except:
        games = "No ETS2 Game Log File Found"

    try:
        if (games == "No ETS2 Game Log File Found"):
            scs_telemetry_found = False
            input_semantical_found = False
        else:
            # Check if the line contains 'input_semantical' or 'scs-telemetry'
            if 'input_semantical' in games:
                input_semantical_found = True
            else:
                input_semantical_found = False
            if 'scs-telemetry' in games:
                scs_telemetry_found = True
            else:
                scs_telemetry_found = False
    except:
        input_semantical_found = False
        scs_telemetry_found = False
        
    try:
        config_data = json.loads(settings)
        app_enabled = config_data.get("Plugins", {}).get("Enabled", [])
    except:
        if(settings == "No settings file found."):
            app_enabled = ""
        else:
            app_enabled = "No plugins enabled"

    if app_enabled == "":
        jsonData = {
            "type": "Debug",
            "logs": logs,
            "settings": settings,
            "additional": f"OS: {oss} \nOS Version: {osversion} \n\nApp version: {appversion} \nPython Version: {pythonversion} \nGit Version: {gitversion} \nDlls installed: \nInput_semantical: {input_semantical_found} \nScs-telemetry: {scs_telemetry_found} \n\nCPU: {cpu}GPU: {gpu}"
        } 
    else:
        jsonData = {
            "type": "Debug",
            "logs": logs,
            "settings": settings,
            "pluginEnabled": app_enabled,
            "additional": f"OS: {oss} \nOS Version: {osversion} \n\nApp version: {appversion} \nPython Version: {pythonversion} \nGit Version: {gitversion} \nDlls installed: \nInput_semantical: {input_semantical_found} \nScs-telemetry: {scs_telemetry_found} \nCPU: {cpu} GPU: {gpu}"
        }
    
    jsonDatadumped = json.dumps(jsonData, indent=4) 
    subprocess.run(['clip'], input=jsonDatadumped, text=True, check=True)
    return jsonData

def send_debug_data():
    global root  # Declare root as a global variable
    data = get_os_info()

    url = 'https://crash.tumppi066.fi/debug'  # Replace with your actual endpoint
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=data)
        print("Data sent successfully")
        
        # Switch to the "Sent Complete" menu
        show_frame(sent_complete_frame)
        
    except Exception as e:
        print(f"Failed to send data: {e}")

def show_frame(frame):
    frame.tkraise()

def create_gui():
    json_data = get_os_info()
    global sent_complete_frame  # Declare sent_complete_frame as a global variable
    root = tk.Tk()
    root.title("Debug Information")

    # Frame for debug information
    debug_frame = ttk.Frame(root, padding="10")
    debug_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    title_label = ttk.Label(debug_frame, text=f"Please review the following information before sending the debug data: \n - OS: {oss} \n - OS version: {osversion} \n - App version: {appversion} \n - Python version: {platform.python_version()} \n - Git version: {gitversion} \n - CPU \n - GPU \n - Logs \n - Settings", font=("Helvetica", 14))
    title_label.grid(column=0, row=0, columnspan=2, pady=5)

    text_label = ttk.Label(debug_frame, text="Raw Debug Being Sent:")
    text_label.grid(column=0, row=1, columnspan=2, pady=5)

    info_text = tk.Text(debug_frame, height=15, width=50)
    info_text.grid(column=0, row=2, columnspan=2, pady=5)

    # Call the function to get JSON data and display it in the text box
    info_text.insert(tk.END, json.dumps(json_data, indent=2))

    send_button = ttk.Button(debug_frame, text="Send Debug Data", command=send_debug_data)
    send_button.grid(column=0, row=3, columnspan=2, pady=10)

    # Frame for "Sent Complete" message
    sent_complete_frame = ttk.Frame(root, padding="10")
    sent_complete_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Increase font size for the "Sent Complete" frame
    message_label = ttk.Label(sent_complete_frame, text="Sent complete. You can now close the window. \nThe debug data has also been copied to your clipboard. \nThanks for helping in the development of ETS2LA", font=("Helvetica", 18))
    message_label.grid(column=0, row=0, pady=10)

    close_button = ttk.Button(sent_complete_frame, text="Close", command=root.destroy)
    close_button.grid(column=0, row=1, pady=10)

    # Initially, show the debug information frame
    show_frame(debug_frame)

    root.mainloop()

# Run the GUI
create_gui()
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

GITHUB_APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/"
SOURCEFORGE_APP_URL = "https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code"
FOLDER = r"$($scriptDirectory)"

try:
    with open("version.txt", 'r') as file:
        VERSION = file.read()
except:
    printRed("Could not find version.txt file, please rerun installer.bat or else the installer will be outdated")
    checkupdate = 0
    VERSION = "Unknown (Please rerun installer.bat)"

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

    ttk.Label(infoPage, text="Please select the mirror you want to use:", font=("Roboto", 16, "bold")).grid(pady=5, sticky="w", padx=10)
    mirror = tk.StringVar()
    ttk.Radiobutton(infoPage, text="GitHub: This is the recommended mirror as it is the most up-to-date", variable=mirror, value="github").grid(pady=5, sticky="w", padx=10)
    ttk.Radiobutton(infoPage, text="SourceForge: This mirror is not always up to date, \nit is not recommended for most users", variable=mirror, value="sourceforge").grid(pady=5, sticky="w", padx=10)
    mirror.set("github")
    
    ttk.Label(infoPage, text="Please select the branch you want to install:", font=("Roboto", 16, "bold")).grid(pady=5, sticky="w", padx=10)
    branch = tk.StringVar()
    ttk.Radiobutton(infoPage, text="Stable", variable=branch, value="main").grid(pady=5, sticky="w", padx=10)
    ttk.Radiobutton(infoPage, text="Experimental (development)", variable=branch, value="experimental").grid(pady=5, sticky="w", padx=10)
    
    while branch.get() == "" or mirror.get() == "":
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
        urrlib.urlopen(GITHUB_APP_URL)
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
        if mirror.get() == "github":
            os.system("git clone -b " + branch.get() + " " + GITHUB_APP_URL + " app")
        else:
            os.system("git clone -b " + branch.get() + " " + SOURCEFORGE_APP_URL)
            os.rename("code", "app")
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
    
    dir = FOLDER
    
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

    preferenceslabel = ttk.Label(preferenceFrame, text="Preferences", font=("Roboto", 16, "bold"))
    preferenceslabel.grid(columnspan=3, row=0, sticky='n', padx=150, pady=0)
    canchange = ttk.Label(preferenceFrame, text="You can change these in the settings later", font=("Roboto", 10))
    canchange.grid(columnspan=3, row=1, sticky='n', padx=150, pady=5)

    selectotherslabel = ttk.Label(preferenceFrame, text="Other Settings", font=("Roboto", 12))
    selectotherslabel.grid(columnspan=3, row=5, sticky='w', pady=5, padx=10)

    shortcut = tk.IntVar()
    iconcheckbox = ttk.Checkbutton(preferenceFrame, text="Enable Desktop and Start Menu Shortcuts", variable=shortcut)
    iconcheckbox.grid(columnspan=3, row=6, sticky='w', pady=5, padx=10)
    shortcut.set(1)
    iconcheckbox.var = shortcut

    # Runs when the confirm button is pressed
    def confirmselection():
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
        restoreconsole()

    

    # Restore the console after preferences are saved
    def restoreconsole():
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

InstallerThread = threading.Thread(target=root.mainloop())
InstallerThread.start()

"@

$updatedata = @"
cmd /k "cd $($scriptDirectory)/venv/Scripts & .\activate & cd $($scriptDirectory)/app & git stash & git pull & exit" & cd $($scriptDirectory) & git stash & git pull & pause
"@

$activatedata = @"
cmd /k"cd "$($scriptDirectory)/venv/Scripts" & .\activate.bat & cd $($scriptDirectory)"
"@

$steamparserpydata = @"
import os
try:
    import json, vdf, winreg
except:
    os.system("pip install json")
    os.system("pip install vdf")
    os.system("pip install winreg")
import json, vdf, winreg

foundGames = []

def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

try:
    STEAM_INSTALL_FOLDER = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam"), "SteamPath")[0]
except:
    STEAM_INSTALL_FOLDER = r"C:\Program Files (x86)\Steam"

LIBRARY_FOLDER_LOCATION = r"steamapps\libraryfolders.vdf"
SECONDARY_LIBRARY_FOLDER_LOCATION = r"D:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
ETS2_PATH_IN_LIBRARY = r"steamapps\common\Euro Truck Simulator 2"
ATS_PATH_IN_LIBRARY = r"steamapps\common\American Truck Simulator"
VERIFY_FILE = "base.scs"

def ReadSteamLibraryFolders():
    libraries = []
    
    if os.path.isfile(os.path.join(STEAM_INSTALL_FOLDER, LIBRARY_FOLDER_LOCATION)):
        file = open(os.path.join(STEAM_INSTALL_FOLDER, LIBRARY_FOLDER_LOCATION), "r")
    else:
        file = open(SECONDARY_LIBRARY_FOLDER_LOCATION, "r")
        
    file = vdf.load(file)   
    for key in file["libraryfolders"]:
        if key.isnumeric():
            libraries.append(file["libraryfolders"][key]["path"])    
    
    return libraries

def FindSCSGames():
    try:
        libraries = ReadSteamLibraryFolders()
    except:
        libraries = [r"C:\Games"]
    
    for library in libraries:
        if os.path.isfile(library + "\\" + ETS2_PATH_IN_LIBRARY + "\\" + VERIFY_FILE):
            foundGames.append(library + "\\" + ETS2_PATH_IN_LIBRARY)
        else:
            foundGames.append("None")
        
        if os.path.isfile(library + "\\" + ATS_PATH_IN_LIBRARY + "\\" + VERIFY_FILE):
            foundGames.append(library + "\\" + ATS_PATH_IN_LIBRARY)
        else:
            foundGames.append("None")

    return foundGames

if __name__ == "__main__":
    print(FindSCSGames())
"@

# Save the content to the bat file
$installerdata | Set-Content -Path $installerFilePath
$uninstallerdataarray[0] | Set-Content -Path $uninstallerFilePath -NoNewline
$uninstallerdataarray[1] | Add-Content -Path $uninstallerFilePath
$uninstallerdataarray[2] | Add-Content -Path $uninstallerFilePath -NoNewline
$uninstallerdataarray[3] | Add-Content -Path $uninstallerFilePath
$uninstallerdataarray[4] | Add-Content -Path $uninstallerFilePath
$debugdata | Set-Content -Path $debugfilepath
$installpydata | Set-Content -Path $installpyFilePath -Encoding utf8
$updatedata | Set-Content -Path $updatebatFilePath
$activatedata | Set-Content -Path $activatebatFilePath
$steamparserpydata | Set-Content -Path $steamparserpyFilePath -Encoding utf8

Set-Location $scriptDirectory

function RunScript($file) {
    $file_type = $file.Split(".")[1]
    $file_name = $file.Split(".")[0]
    $file_name = $file_name.TrimEnd(".")
    Write-Host "Running $file_name Script"

    Set-Location $tempDir

    if ($file_type -eq "bat") {
    Start-Process -FilePath "./$($file)"
    } else {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-File $($file)"
    }
    Set-Location $scriptDirectory
}

# Check if file exists
if (Test-Path -Path "app\profiles\installer_config.cfg") {
    $file_contents = Get-Content -Path "app\profiles\installer_config.cfg"
    $theme_file = $file_contents.Split("=")[1].Split(" ")[1]
    $app_installed = $true
}
else {
    if (-Not(Test-Path -Path "$scriptDirectory\app")) {
        $app_installed = $false
        Write-Host "App does not exist. Click the installer button to install the app. Other buttons will not function until the app is installed."
    }
    else {
        # Create a new file
        $app_installed = $true
        New-Item -Path "app\profiles\installer_config.cfg" -Value "theme = dark" -ItemType File -Force | Out-Null
        $file_contents = Get-Content -Path "app\profiles\installer_config.cfg"
        $theme_file = $file_contents.Split("=")[1].Split(" ")[1]
    }
}

Function ButtonEnabled(){
    if ($app_installed -eq $true) {
        $Enabled = $true
    }
    else {
        $Enabled = $false
    }
    return $Enabled
}

Function ButtonColor(){
    if ($app_installed -eq $true) {
        $Color = "#077FFF"
    }
    else {
        $Color = "#6B6B6B"
    }
    return $Color
}

        
if ($theme_file -eq "dark") {
    $label_color = "#FFFFFF"
    $gui_color = "#000000"
}
elseif ($theme_file -eq "light") {
    $label_color = "#000000"
    $gui_color = "#FFFFFF"
} 
elseif ($theme_file -eq "system") {
    $label_color = "#000000"
    $gui_color = "#FFFFFF"
}
else {
    $label_color = "#FFFFFF"
    $gui_color = "#000000"
}

# Init PowerShell Gui
Add-Type -AssemblyName System.Windows.Forms

# Create a new form
$gui = New-Object system.Windows.Forms.Form

# Define the size, title and background color
$gui.ClientSize = '410,340'
$gui.text = "ETS2 Lane Assist Installer"
$gui.BackColor = $gui_color

# Title
$Title = New-Object system.Windows.Forms.Label
$Title.text = "ETS2 Lane Assist Menu"
$Title.AutoSize = $true
$Title.location = New-Object System.Drawing.Point(20,20)
$Title.Font = 'Microsoft Sans Serif,18'
$Title.ForeColor = $label_color
$gui.controls.Add($Title)

# Subbcategories
$Installersubcategory = New-Object system.Windows.Forms.Label
$Installersubcategory.text = "Install"
$Installersubcategory.AutoSize = $true
$Installersubcategory.location = New-Object System.Drawing.Point(20,60)
$Installersubcategory.Font = 'Microsoft Sans Serif,12'
$Installersubcategory.ForeColor = $label_color
$gui.controls.Add($Installersubcategory)

$Uninstallersubcategory = New-Object system.Windows.Forms.Label
$Uninstallersubcategory.text = "Uninstall"
$Uninstallersubcategory.AutoSize = $true
$Uninstallersubcategory.location = New-Object System.Drawing.Point(20,180)
$Uninstallersubcategory.Font = 'Microsoft Sans Serif,12'
$Uninstallersubcategory.ForeColor = $label_color
$gui.controls.Add($Uninstallersubcategory)

$UtilitiesSubcategory = New-Object system.Windows.Forms.Label
$UtilitiesSubcategory.text = "Utilities"
$UtilitiesSubcategory.AutoSize = $true
$UtilitiesSubcategory.location = New-Object System.Drawing.Point(230,60)
$UtilitiesSubcategory.Font = 'Microsoft Sans Serif,12'
$UtilitiesSubcategory.ForeColor = $label_color
$gui.controls.Add($UtilitiesSubcategory)

# Buttons
$InstallerButton = New-Object system.Windows.Forms.Button
$InstallerButton.BackColor = "#0080FF"
$InstallerButton.text = "Installer"
$InstallerButton.width = 160
$InstallerButton.height = 45
$InstallerButton.location = New-Object System.Drawing.Point(20,90)
$InstallerButton.Font = 'Microsoft Sans Serif,12'
$InstallerButton.ForeColor = "#FFFFFF"
$InstallerButton.add_click({RunScript("installer.bat")})
$gui.controls.Add($InstallerButton)

$UninstallerButton = New-Object system.Windows.Forms.Button
$UninstallerButton.BackColor = ButtonColor
$UninstallerButton.text = "Uninstaller"
$UninstallerButton.width = 160
$UninstallerButton.height = 45
$UninstallerButton.location = New-Object System.Drawing.Point(20,210)
$UninstallerButton.Font = 'Microsoft Sans Serif,12'
$UninstallerButton.ForeColor = "#FFFFFF"
$UninstallerButton.Enabled = ButtonEnabled
$UninstallerButton.add_click({RunScript("uninstaller.ps1")})
$gui.controls.Add($UninstallerButton)

$UpdateButton = New-Object system.Windows.Forms.Button
$UpdateButton.BackColor = ButtonColor
$UpdateButton.text = "Update"
$UpdateButton.width = 160
$UpdateButton.height = 45
$UpdateButton.location = New-Object System.Drawing.Point(230,90)
$UpdateButton.Font = 'Microsoft Sans Serif,12'
$UpdateButton.ForeColor = "#FFFFFF"
$UpdateButton.Enabled = ButtonEnabled
$UpdateButton.add_click({RunScript("update.bat")})
$gui.controls.Add($UpdateButton)

$DebugButton = New-Object system.Windows.Forms.Button
$DebugButton.text = "Debug"
$DebugButton.width = 160
$DebugButton.height = 45
$DebugButton.location = New-Object System.Drawing.Point(230,150)
$DebugButton.Font = 'Microsoft Sans Serif,12'
$DebugButton.ForeColor = "#FFFFFF"
if ([System.Windows.Forms.Control]::IsKeyLocked('NumLock')) {
    [System.Windows.Forms.MessageBox]::Show("Numlock bypass is on. Click the installer button to install the app. Other buttons will not function until the app is installed besides debug.", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
    $DebugButton.BackColor = "#077FFF"
} else {
    $DebugButton.Enabled = ButtonEnabled
    $DebugButton.BackColor = ButtonColor
}
$DebugButton.add_click({python($debugfilepath)})
$gui.controls.Add($DebugButton)

$ActivateButton = New-Object system.Windows.Forms.Button
$ActivateButton.BackColor = ButtonColor
$ActivateButton.text = "Activate"
$ActivateButton.width = 160
$ActivateButton.height = 45
$ActivateButton.location = New-Object System.Drawing.Point(230,210)
$ActivateButton.Font = 'Microsoft Sans Serif,12'
$ActivateButton.ForeColor = "#FFFFFF"
$ActivateButton.Enabled = ButtonEnabled
$ActivateButton.add_click({RunScript("activate.bat")})
$gui.controls.Add($ActivateButton)

# Display the fGUI
[void]$gui.ShowDialog()

# Remove the bat files
Remove-Item -Path $installerFilePath -Force
Remove-Item -Path $uninstallerFilePath -Force
Remove-Item -Path $debugfilepath -Force
Remove-Item -Path $installpyFilePath -Force
Remove-Item -Path $updatebatFilePath -Force
Remove-Item -Path $activatebatFilePath -Force
Remove-Item -Path $SteamParserpyFilePath -Force
