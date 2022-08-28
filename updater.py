
# Import everything
import os
import sys
import shutil
from urllib.parse import urljoin, urlparse
import urllib.request
import zipfile
import time
import tkinter as tk

width = 500
height = 500
root = tk.Tk()
root.title("Updater")
root.geometry("%dx%d" % (width, height))
root.configure(bg='#1c1c1c')

# For convenience a clear function.
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Default paths
hostname = "github.com" # For checking internet
dest = "Euro-Truck-Simulator-2-Lane-Assist-main"
localVersion = 0
newestVersion = 0
changeLog = ""

# Check the current version and the newest version
def CheckVersion():
    global localVersion
    global newestVersion
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
        print(changeLog)
        # Check if the newest version is newer than the local version
    except:
        newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt")
        newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
        os.remove(newestVersionFile)
        changeLogFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/experimental/changelog.txt")
        changeLog = open(changeLogFile, "r").read().split("Update")[1]
        os.remove(changeLogFile)
        print(changeLog)
        pass

CheckVersion()

# Make sure the user understands that the program will delete the old files
def RemoveOldFiles():
    # Delete the old files
    shutil.rmtree(dest, ignore_errors=True)
    print("Files removed")

# Download percentage display
# Credits to https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html

downloaded = 0
def reporthook(count, block_size, total_size):
    global downloaded
    progress_size = int(count * block_size)
    downloaded = progress_size / (1024 * 1024)

def DownloadNewVersion():
    # Download the newest version
    name, headers = urllib.request.urlretrieve("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/main.zip", "tempFile.zip" ,reporthook=reporthook)

    # Unzip the new version
    with zipfile.ZipFile(name, 'r') as zip_ref:
        zip_ref.extractall("")

    # Remove the temporary zip
    os.remove(name)

def InstallRequirements():
    # Install the requirements from the requirements.txt file
    # This piece of code get's the current path and appends the newly downloaded file path to it.
    # os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt"
    print("Installing requirements...")
    os.system("pip install -r " + os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt")
    print("Done")
    print("---------------------------------------")
    print("Also install torch https://pytorch.org/get-started/locally/ select pip and cuda/cpu depending on your system.")
    print("And if you have a nvidia gpu then https://developer.nvidia.com/cuda-downloads select the newest version.")
    print("In addition to a lane detection model https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist#lane-detection-models")
    print("Recommended TuSimple34 for GPU or Culane18 for CPU")
    print("---------------------------------------")