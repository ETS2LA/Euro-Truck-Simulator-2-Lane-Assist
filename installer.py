import sys
import subprocess
import os
import tkinter as tk
import threading

def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))

# Check for path spaces
if " " in os.getcwd():
    printRed("The path of this app includes spaces.")
    printRed("Please move the app to a folder path without spaces.")
    input()
    quit()

# Check python version (must be 3.9.x)
if sys.version_info[0] != 3 or sys.version_info[1] != 9:
    printRed("This app requires python version 3.9.x to create the correct virtual environment.")
    printRed("Please install python 3.9.x and run the installer again.")
    printRed("You might also have to run the app with 'python3' instead of 'python'.")
    input()
    quit()

# Check for a .bat file
if not os.path.exists("installer.bat"):
    # Create it
    with open("installer.bat", "w") as file:
        file.write("python installer.py")
        file.write("\npause")
        printGreen("Created installer.bat to run the application easier.")


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


MINICONDA_URL = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
APP_URL = "https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/archive/refs/heads/LSTR-Development.zip"

# Make the installer window
root = ctk.CTk()
root.title("ETS2 Lane Assist Installer")
root.geometry("300x140")
root.resizable(True, True)

# Make the installer window widgets
title = ctk.CTkLabel(root, text="ETS2 Lane Assist Installer", font=("Arial", 20))
title.pack(pady=10)

status = ctk.CTkLabel(root, text="Status: Waiting for user input", font=("Arial", 10))
status.pack(pady=0)

def createEnv():
    dir = os.path.dirname(os.path.realpath(__file__))
    venv.create(dir + "/venv", with_pip=True)

def downloadRequirements():
    dir = os.path.dirname(os.path.realpath(__file__))
    os.system(f"{dir}/venv/Scripts/pip install -r {dir}/app/Euro-Truck-Simulator-2-Lane-Assist-LSTR-Development/requirements.txt")
    printGreen("> Done")
    print("Installing pytorch... please wait...")
    ChangeStatus("Installing torch, check the console...")
    os.system(f"{dir}/venv/Scripts/pip install torch==1.13.1 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117")

def runApp():
    # Open a new terminal and run the app
    dir = os.path.dirname(os.path.realpath(__file__))
    os.system(f'start cmd /C "cd {dir}/app/Euro-Truck-Simulator-2-Lane-Assist-LSTR-Development & {dir}/venv/Scripts/python AppUI.py & pause"')
    quit()

# Install function
def install():
    # Check for install confirmation
    if not tk.messagebox.askokcancel("Install", "Are you sure you want to install?"):
        root.destroy()
        quit()

    # Check for virtual environment
    if not os.path.exists("venv"):
        if not tk.messagebox.askokcancel("Virtual Environment", "The installer will create a new virtual environment."):
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
        if tk.messagebox.askokcancel("App", "Do you want to redownload the app?"):
            print("Please wait, downloading the app...")
            ChangeStatus("Downloading...")
            progress.start()
            file = urrlib.urlretrieve(APP_URL, "app.zip", DownloadProgressBar)
            printGreen("> Done")

            # Extract the app
            print("Please wait, extracting the app...")
            ChangeStatus("Extracting...")
            with zipfile.ZipFile("app.zip", 'r') as zip_ref:
                zip_ref.extractall("app")
            printGreen("> Done")
            progress.stop()

    else:
        if not tk.messagebox.askokcancel("App", "Download the app?"):
            root.destroy()
            quit()
        
        print("Please wait, downloading the app...")
        ChangeStatus("Downloading...")
        progress.start()
        file = urrlib.urlretrieve(APP_URL, "app.zip", DownloadProgressBar)
        printGreen("> Done")

        # Extract the app
        print("Please wait, extracting the app...")
        ChangeStatus("Extracting...")
        with zipfile.ZipFile("app.zip", 'r') as zip_ref:
            zip_ref.extractall("app")
        printGreen("> Done")
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
    button.configure(text="Run", command=runApp)
    printGreen("> Done\n > Installation complete, you can now run the app.")

    # Check for a .bat file
    if not os.path.exists("run.bat"):
        with open("run.bat", "w") as f:
            dir = os.path.dirname(os.path.realpath(__file__))
            f.write(f"cd {dir}/app/Euro-Truck-Simulator-2-Lane-Assist-LSTR-Development & {dir}/venv/Scripts/python AppUI.py & pause")
            print("Created run.bat, to run th app easier.")



    

button = ctk.CTkButton(root, text="Install", command=install, width=200)
button.pack(pady=0)

if os.path.exists("app"):
    button2 = ctk.CTkButton(root, text="Run", command=runApp, width=200)
    button2.pack(pady=10)
    root.geometry("300x170")
    
    progress = ctk.CTkProgressBar(root, width=250)
    progress.configure(mode="indeterminate")
    progress.pack(pady=2)

else:
    progress = ctk.CTkProgressBar(root, width=250)
    progress.configure(mode="indeterminate")
    progress.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", quit)

root.mainloop()
