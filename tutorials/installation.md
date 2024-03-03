---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-3-3
icon: checklist
tags: 
  - tutorial
---

[!embed](https://www.youtube.com/watch?v=0pic0rzjvik)

!!! Note
This page will be expanded in the future once the new installer is released. There is no reason for us to write a tutorial for something that is going to be replaced in a week or so :+1:

For now you can enjoy my extremely enthusiastic video tutorial👌
!!!


## Manual Installation  
This is a guide for installing the app manually. Manual installation doesn't use any .exe or .bat files, but is also less convenient than the installer.

||| Features you will miss:
- A shortcut to the app on your desktop / start menu.
- A virtual python environment for the app, we will install everything globally.
- Access to the debug script (send us data when we're troubleshooting).
  
||| Features you will still have:
- Automatic updates (if you use the git download method).
- And every app feature the installer has too (the versions are identical, and get pulled from the same repository).
|||
‎
#### Step 1: Download python and git
=== Python
- Go to the [Python website](https://www.python.org/downloads/) and download the latest version of Python 3.11 (as of writing this is [3.11.8](https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe)).
- Make sure to enable **Add python to Path** during the installation.
- Other settings can be on default.
=== Git
- Go to the [Git website](https://git-scm.com/download/win) and download the latest version of Git.
- The settings can all be on default.
===
‎
#### Step 2: Download the app
==- With Git (recommended)
- Make a new folder for the app, preferably `C:\LaneAssist\` as that is the default location the installer uses.
- Open a cmd or powershell in that folder.
  - Either right click empty space in the folder while holding shift and select `Open Powershell window here` or `Open cmd window here`.
  - Or open a cmd or powershell and navigate to the folder with `cd C:\LaneAssist\`.
- Run the following command to clone the app to the `C:\LaneAssist\app` folder.
`git clone https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist.git app`
- Move your console to that folder: `cd app`
!!! Note
If this part for some reason fails, try and restart your computer.
!!!
==- Without Git 
- Go to the [app repository](https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist) and click the green `Code` button and select `Download ZIP`.
- Extract the zip file to `C:\LaneAssist\app`.
- Open a new cmd or powershell in the folder.
  - Either right click empty space in the folder while holding shift and select `Open Powershell window here` or `Open cmd window here`.
  - Or open a cmd or powershell and navigate to the folder with `cd C:\LaneAssist\app`.
===
‎
#### Step 3: Install the app
==- With the custom `install.py` script.
- Make sure you have a cmd or powershell open in the `C:\LaneAssist\app` folder.
- Run the following command to install the app.
  - `python install.py`
==- Without the custom `install.py` script.
- Make sure you have a cmd or powershell open in the `C:\LaneAssist\app` folder.
- Run the following command to install the app.
  - `pip install -r requirements.txt`
===
‎
#### Step 4: Run the app
==- With a shortcut we will create.
- Create the `run.bat` file in the `C:\LaneAssist` folder.
- Type the following into the file and save it.
```bat
@echo off
cd app
python main.py
pause
```
- You can now easily run the app by double clicking the `run.bat` file.
- You can also right click the `run.bat` file and select `Send to` -> `Desktop (create shortcut)` to create a shortcut on your desktop.
==- Without a shortcut
- Make sure you have a cmd or powershell open in the `C:\LaneAssist\app` folder.
- Run the following command to run the app.
  - `python main.py`
===
‎
#### Troubleshooting
There are no known issues yet, if you find one, then please report it to me on [Discord](https://discord.gg/DpJpkNpqwD)