import sys
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import threading


APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/"


def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

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

# Check for git
try:
    subprocess.check_call(["git", "--version"])
except:
    printRed("Git is not installed.")
    printRed("Git can be installed at https://gitforwindows.org/")
    if input(" Do you want to open the website? y/n ").lower == "y":
        try:
            import webbrowser
        except:
            os.system("pip install webbrowser")
            import webbrowser

        webbrowser.open("https://gitforwindows.org/")
        quit()
    quit() 


def Install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

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

# Check for customtkinter
try:
    import customtkinter as ctk

except ImportError:
    print("Please wait installing necessary UI library...")
    Install("customtkinter")
    printGreen("> Done")
    import customtkinter as ctk

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

# Make the installer window
root = ctk.CTk()
root.title("ETS2 Lane Assist Installer")
root.geometry("300x160")
root.resizable(True, True)

# Make the installer window widgets
title = ctk.CTkLabel(root, text="ETS2 Lane Assist Installer", font=("Arial", 20))
title.pack(pady=10)

status = ctk.CTkLabel(root, text="Status: Waiting for user input", font=("Arial", 10))
status.pack(pady=0)

def createEnv():
    dir = os.path.dirname(os.path.realpath(__file__))
    venv.create(dir + "/venv", with_pip=True)
    
    # Create a .bat file to activate the virtual environment
    with open("activate.bat", "a") as f:
        if os.name == "nt":
            f.write("@echo off\n")
            string = "cmd /k"
            string += fr'"cd "{dir}/venv/Scripts" & .\activate.bat"'
            f.write(string)
        else:
            f.write(f"cd {dir}/venv/Scripts & ./activate")

def downloadRequirements():
    dir = os.path.dirname(os.path.realpath(__file__))
    os.system(f"{dir}/venv/Scripts/pip install -r {dir}/app/requirements.txt")
    printGreen("> Done")

def runApp():
    # Open a new terminal and run the app
    dir = os.path.dirname(os.path.realpath(__file__))
    if os.name == "nt":
        os.system(r".\run.bat")
    else:
        os.system(r"./run.bat")
    quit()

# Install function
def install():
    # Check disk space (need 7.5gb)
    import shutil
    total, used, free = shutil.disk_usage("/")
    if free < 7500000000:
        printRed(f"Not enough free disk space to install the app ({round(free/1000000000, 1)}gb).")
        printRed("You need atleast 7.5gb of free space.")
        printRed("If you already have the app installed, then this might not be a problem and you can continue.")
        if input(" Continue? y/n ").lower() != "y":
            root.destroy()
            quit()

    # Check for install confirmation
    if not messagebox.askokcancel("Install", "Are you sure you want to install?"):
        root.destroy()
        quit()

    # Check for virtual environment
    if not os.path.exists("venv"):
        if not messagebox.askokcancel("Virtual Environment", "The installer will create a new virtual environment."):
            root.destroy()
            quit()

        progress.start()
        print("Please wait, creating a virtual environment...")
        ChangeStatus("Creating virtual environment...")
        thread = threading.Thread(target=createEnv)
        thread.start()
        while thread.is_alive():
            root.update()
        progress.stop()

    # Download the app
    if os.path.exists("app.zip"):
        if messagebox.askokcancel("App", "Do you want to redownload the app?"):
            print("Please wait, downloading the app...")
            ChangeStatus("Downloading...")
            progress.start()
            # Download the repo using git
            dir = os.path.dirname(os.path.realpath(__file__))
            # Make the directory
            if not os.path.exists(dir + "/app"):
                os.mkdir(dir + "/app")
            
            dir += r"\app"
            print(f"Cloning the repo to {dir}...")
            os.system(f"git clone -b {branch.get()} {APP_URL} {dir}")
            progress.stop()
            

    else:
        if not messagebox.askokcancel("App", "Download the app?"):
            root.destroy()
            quit()
        
        print("Please wait, downloading the app...")
        ChangeStatus("Downloading...")
        progress.start()
        # Download the repo using git
        dir = os.path.dirname(os.path.realpath(__file__))
        # Make the directory
        if not os.path.exists(dir + "/app"):
            os.mkdir(dir + "/app")

        dir += r"\app"
        print(f"git clone -b {branch.get()} {APP_URL} {dir}")
        subprocess.run(f"git clone -b {branch.get()} {APP_URL} {dir}")
        progress.stop()

    # Install requirements
    print("Please wait, installing requirements...")
    ChangeStatus("Installing requirements, check the console...")
    progress.start()
    thread = threading.Thread(target=downloadRequirements)
    thread.start()
    while thread.is_alive():
        root.update()
    progress.configure(mode="determinate")
    progress.stop()
    progress.set(1)
    ChangeStatus("Installation complete!")
    printGreen("> Done\n > Installation complete, you can now run the app.")

    # Check for a .bat file
    if not os.path.exists("run.bat"):
        with open("run.bat", "w") as f:
            dir = os.path.dirname(os.path.realpath(__file__))
            f.write(fr'cmd /k "cd {dir}/venv/Scripts & .\activate & cd {dir}/app & {dir}/venv/Scripts/python main.py & pause"')
            print("Created run.bat, to run the app easier.")

    button.configure(text="Run", command=runApp)


branch = tk.StringVar()
branch.set("v2.0-rewrite")
branchObject = ctk.CTkEntry(root, textvariable=branch, width=200)
branchObject.pack(pady=0)

button = ctk.CTkButton(root, text="Install", command=install, width=200)
button.pack(pady=5)

if os.path.exists("app"):
    button2 = ctk.CTkButton(root, text="Run", command=runApp, width=200)
    button2.pack(pady=2)
    root.geometry("300x200")
    
    progress = ctk.CTkProgressBar(root, width=250)
    progress.configure(mode="indeterminate")
    progress.pack(pady=8)

else:
    progress = ctk.CTkProgressBar(root, width=250)
    progress.configure(mode="indeterminate")
    progress.pack(pady=6)

root.protocol("WM_DELETE_WINDOW", quit)

root.mainloop()
