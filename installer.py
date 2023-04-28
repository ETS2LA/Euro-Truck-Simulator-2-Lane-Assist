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

# Check for urrlib
try:
    import urllib.request as urrlib

except:
    print("Please wait installing urlrlib...")
    Install("urllib")
    printGreen("> Done")

# Check for zipfile
try:
    import zipfile

except:
    print("Please wait installing zipfile...")
    Install("zipfile")
    printGreen("> Done")

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
    
    # Check for miniconda
    if not os.path.exists("miniconda.exe"):
        if not tk.messagebox.askokcancel("Miniconda", "The installer will download miniconda to create a virtual environment."):
            root.destroy()
        # Download miniconda
        print("Please wait, downloading miniconda...")
        file = urrlib.urlretrieve(MINICONDA_URL, "miniconda.exe", DownloadProgressBar)
        printGreen("> Done")
        ChangeStatus("Status: Waiting for user input")

    # Check for virtual environment
    if not os.path.exists("env"):
        if not tk.messagebox.askokcancel("Virtual Environment", "The installer will create a new virtual environment."):
            root.destroy()
        print("Please wait, installing miniconda...")
        ChangeStatus("Installing miniconda THE APP WILL HANG...")
        # Get current directory
        cwd = os.getcwd()
        # Install conda of python 3.9
        subprocess.call("miniconda.exe /InstallationType=JustMe /RegisterPython=0 /S /D=" + cwd + "\\env", shell=True)
        printGreen("> Done")
        ChangeStatus("Status: Waiting for user input")

    # Create the virtual environment
    if not os.path.exists("env/envs/laneassist"):
        if not tk.messagebox.askokcancel("Virtual Environment", "The installer will create a new virtual environment."):
            root.destroy()
        print("Please wait, creating a virtual environment...")
        ChangeStatus("Creating virtual environment...")
        path = os.path.dirname(os.path.realpath(__file__))
        os.system(f'"env\_conda.exe" create -p {path + "/env/envs/laneassist"} python=3.9 -y')
        printGreen("> Done")
        ChangeStatus("Status: Waiting for user input")

    # Download the app
    if os.path.exists("app.zip"):
        if tk.messagebox.askokcancel("App", "Do you want to redownload the app?"):
            print("Please wait, downloading the app...")
            ChangeStatus("Downloading...")
            file = urrlib.urlretrieve(APP_URL, "app.zip", DownloadProgressBar)
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
    ChangeStatus("Installing requirements...")
    filename = "requirements.txt"
    
    # Open a new terminal in the env
    # (this was all copilot xD)
    subprocess.call(f"""start cmd /k \"cd {os.getcwd() + '/env/envs/laneassist'} && activate && cd {os.getcwd() + '/app/Euro-Truck-Simulator-2-Lane-Assist-LSTR-Development'} && conda activate laneassist && pip install -r {filename} && pip install torch==1.13.1 torchvision==0.13.1 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu117\"""", shell=True)
    


    

button = ctk.CTkButton(root, text="Install", command=install, width=200)
button.pack(pady=0)

progress = ctk.CTkProgressBar(root, width=250)
progress.set(0)
progress.pack(pady=10)

root.mainloop()
