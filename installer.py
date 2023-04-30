import sys
import subprocess
import os
import tkinter as tk


def printRed(text):
    print("\033[91m {}\033[00m" .format(text))
def printGreen(text):
    print("\033[92m {}\033[00m" .format(text))


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

    if percent:
        sys.stdout.write("\r {}% {}kb".format(percent, kb))
        sys.stdout.flush()
        
        try:
            ChangeStatus("Downloading... " + "\r {}% {}kb".format(percent, kb))
            progress.set(percent/100)
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

# Install function
def install():
    # Check for install confirmation
    if not tk.messagebox.askokcancel("Install", "Are you sure you want to install?"):
        root.destroy()

    # Check for virtual environment
    if not os.path.exists("venv"):
        if not tk.messagebox.askokcancel("Virtual Environment", "The installer will create a new virtual environment."):
            root.destroy()
        print("Please wait, creating a virtual environment...")
        ChangeStatus("Creating virtual environment...")
        dir = os.path.dirname(os.path.realpath(__file__))
        venv.create(dir + "/venv", with_pip=True)

    # Download the app
    if os.path.exists("app.zip"):
        if tk.messagebox.askokcancel("App", "Do you want to redownload the app?"):
            print("Please wait, downloading the app...")
            ChangeStatus("Downloading...")
            file = urrlib.urlretrieve(APP_URL, "app.zip", DownloadProgressBar)
            printGreen("> Done")

            # Extract the app
            print("Please wait, extracting the app...")
            ChangeStatus("Extracting...")
            with zipfile.ZipFile("app.zip", 'r') as zip_ref:
                zip_ref.extractall("app")
            printGreen("> Done")

    else:
        if not tk.messagebox.askokcancel("App", "Download the app?"):
            root.destroy()
            quit()
        
        print("Please wait, downloading the app...")
        ChangeStatus("Downloading...")
        file = urrlib.urlretrieve(APP_URL, "app.zip", DownloadProgressBar)
        printGreen("> Done")

        # Extract the app
        print("Please wait, extracting the app...")
        ChangeStatus("Extracting...")
        with zipfile.ZipFile("app.zip", 'r') as zip_ref:
            zip_ref.extractall("app")
        printGreen("> Done")

    # Install requirements
    print("Please wait, installing requirements...")
    ChangeStatus("Installing requirements, check the console...")
    dir = os.path.dirname(os.path.realpath(__file__))
    os.system(f"{dir}/venv/Scripts/pip install -r {dir}/app/Euro-Truck-Simulator-2-Lane-Assist-LSTR-Development/requirements.txt")
    printGreen("> Done")
    ChangeStatus("Installing torch, check the console...")
    os.system(f"{dir}/venv/Scripts/pip install torch==1.13.1 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117")
    printGreen("> Done\n > Installation complete, you can now run the app.")



    

button = ctk.CTkButton(root, text="Install", command=install, width=200)
button.pack(pady=0)

progress = ctk.CTkProgressBar(root, width=250)
progress.set(0)
progress.pack(pady=10)

root.mainloop()
