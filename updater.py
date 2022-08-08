def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m{}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m{}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m{}\033[00m" .format(skk))
# https://www.geeksforgeeks.org/print-colors-python-terminal/
# I didn't really use these a lot.

# Import everything
import os
import sys
import shutil
from urllib.parse import urljoin, urlparse
import urllib.request
import zipfile
import time

# For convenience a clear function.
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Default paths
hostname = "github.com" # For checking internet
dest = "Euro-Truck-Simulator-2-Lane-Assist-main"

# Starting text
clear()
print("---------------------------------------")
print("Update and installation script for ETS2 Lane Assist")
print("---------------------------------------")
print("This script will use the following packages:")
print("- os to check internet connection and get current path")
print("- shutil to delete files")
print("- urrlib to download the new version")
print("- zipfile to unzip the new version")
print("- time, for well time")
print("---------------------------------------")
# Check the local version
try:
    localVersion = open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[0] + " from " + open(os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\version.txt", "r").read().split(",")[1]
    print("Current program version is " + localVersion)
    # Check the newest version
    newestVersionFile, headers = urllib.request.urlretrieve("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt")
    newestVersion = open(newestVersionFile, "r").read().split(",")[0] + " from " + open(newestVersionFile, "r").read().split(",")[1]
    print("Most up to date version is " + newestVersion)
    # Check if the newest version is newer than the local version
    if localVersion == newestVersion:
        print("You are up to date!")
    else:
        print("Update might be required")
    print("---------------------------------------")
except:
    print("Could not get version information")
    print("This is normal if you are running the program for the first time")
# Remind the user to backup personal settings
prRed("BACKUP your personal settings (ie. sensitivity, capture position...) before updating!")
result = input("Are you sure you want to update? (y/n) ")
if(result == "n" or result == "N"):
    prRed("Aborting...")
    exit()

# Test the connection to github
clear()
print("Testing connection to github...")
response = os.system("ping " + hostname)
if response == 0:
  print('\nConnection to github successful\n')
else:
  prRed('Could not connect to github')
  exit()

# Make sure the user understands that the program will delete the old files
prRed("The application will remove all files in the folder "+dest)
result = input("Are you sure you want to continue? (y/n) ")
if(result == "n" or result == "N"):
    prRed("Aborting...")
    exit()
clear()
# Delete the old files
shutil.rmtree(dest, ignore_errors=True)
print("Files removed")

# Download percentage display
# Credits to https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
def reporthook(count, block_size, total_size):
    progress_size = int(count * block_size)
    sys.stdout.write("\r%d MB" %
                    (progress_size / (1024 * 1024)))
    sys.stdout.flush()

# Download the newest version
print("Cloning LaneDetection from github please wait...")
name, headers = urllib.request.urlretrieve("https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/main.zip", "tempFile.zip" ,reporthook=reporthook)

# Unzip the new version
print("\nDone unpacking...")
with zipfile.ZipFile(name, 'r') as zip_ref:
    zip_ref.extractall("")

# Remove the temporary zip
print("Removing temporary file")
os.remove(name)
print("Done")

# Check if the user needs to install the requirements
result = input("Do you want to install requirements? (y/n) ")
if(result == "n" or result == "N"):
    prGreen("Closing...")
    exit()
clear()
# Install the requirements from the requirements.txt file
# This piece of code get's the current path and appends the newly downloaded file path to it.
# os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt"
print("Installing requirements...")
os.system("pip install -r " + os.path.dirname(os.path.abspath(__file__)) +"\\"+ dest + "\\requirements.txt")
prGreen("Done")
print("---------------------------------------")
print("Also install torch https://pytorch.org/get-started/locally/ select pip and cuda/cpu depending on your system.")
print("And if you have a nvidia gpu then https://developer.nvidia.com/cuda-downloads select the newest version.")
print("In addition to a lane detection model https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist#lane-detection-models")
print("Recommended TuSimple34 for GPU or Culane18 for CPU")
print("---------------------------------------")