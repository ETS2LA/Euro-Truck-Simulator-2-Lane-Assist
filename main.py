'''
The main file that runs the programs loop.
'''

# This section is for modules that I've added later as they might 
# not have been installed yet

import os
try:
    import colorama
except:
    os.system("pip install colorama")
    import colorama

try:
    import matplotlib
except:
    os.system("pip install matplotlib")
    import matplotlib

try:
    import webview
except:
    os.system("pip install pywebview")
    import webview

try:
    import vdf
except:
    os.system("pip install vdf")
    import vdf

try:
    import deep_translator
except:
    os.system("pip install deep_translator")
    import deep_translator

try: 
    import babel
except:
    os.system("pip install babel")
    import babel

# Load the UI framework
import src.mainUI as mainUI
import src.loading as loading # And then create a loading window


# Load the rest of the modules
import sys
import time
import json
import src.variables as variables # Stores all main variables for the program
from src.logger import print
import src.logger as logger
import traceback
import src.settings as settings
import src.translator as translator
import psutil
import requests

logger.printDebug = settings.GetSettings("logger", "debug")
if logger.printDebug == None:
    logger.printDebug = False
    settings.CreateSettings("logger", "debug", False)
    

def GetEnabledPlugins():
    global enabledPlugins
    enabledPlugins = settings.GetSettings("Plugins", "Enabled")
    if enabledPlugins == None:
        enabledPlugins = [""]

def UpdateChecker():
    currentVer = variables.VERSION.split(".")
    url = "https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt"
    remoteVer = requests.get(url).text.split(".")
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
        if messagebox.askokcancel("Updater", translator.Translate(f"We have detected an update, do you want to install it?\nCurrent - {'.'.join(currentVer)}\nUpdated - {'.'.join(remoteVer)}")):
            os.system("git stash")
            os.system("git pull")
            if messagebox.askyesno("Updater", translator.Translate("The update has been installed and the application needs to be restarted. Do you want to quit the app?")):
                quit()
        else:
            pass

UpdateChecker()

def FindPlugins():
    global plugins
    global pluginObjects
    
    # Find plugins
    path = os.path.join(variables.PATH, "plugins")
    plugins = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            # Check for main.py
            if "main.py" in os.listdir(os.path.join(path, file)):
                # Check for PluginInformation class
                try:
                    pluginPath = "plugins." + file + ".main"
                    plugin = __import__(pluginPath, fromlist=["PluginInformation"])
                    if plugin.PluginInfo.type == "dynamic":
                        if plugin.PluginInfo.name in enabledPlugins:
                            plugins.append(plugin.PluginInfo)
                except Exception as ex:
                    print(str(ex.args) + f" [{file}]")
                    pass

    pluginObjects = []
    for plugin in plugins:
        pluginObjects.append(__import__("plugins." + plugin.name + ".main", fromlist=["plugin", "UI", "PluginInfo", "onEnable"]))
        pluginObjects[-1].onEnable()
        

def RunOnEnable():
    for plugin in pluginObjects:
        try:
            plugin.onEnable()
        except Exception as ex:
            print(ex.args)
            pass
        

def UpdatePlugins(dynamicOrder, data):
    for plugin in pluginObjects:
        try:
            if plugin.PluginInfo.dynamicOrder == dynamicOrder:
                startTime = time.time()
                data = plugin.plugin(data)
                endTime = time.time()
                data["executionTimes"][plugin.PluginInfo.name] = endTime - startTime
        except Exception as ex:
            print(ex.args + f"[{plugin.PluginInfo.name}]")
            pass
    return data


def InstallPlugins():
    global startInstall
    global loadingWindow
    
    list = settings.GetSettings("Plugins", "Installed")
    if list == None:
        settings.CreateSettings("Plugins", "Installed", [])
    
    # Find plugins
    path = os.path.join(variables.PATH, "plugins")
    installers = []
    pluginNames = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            # Check for main.py
            if "main.py" in os.listdir(os.path.join(path, file)):
                # Check for PluginInformation class
                try:
                    # Get installers for plugins that are not installed
                    if file not in settings.GetSettings("Plugins", "Installed"):
                        pluginPath = "plugins." + file + ".install"
                        try:
                            pluginNames.append(f"{file}")
                            installers.append(__import__(pluginPath, fromlist=["install"]))
                        except: # No installer
                            pass
                        
                    
                except Exception as ex:
                    print(ex.args)
                    pass
    
    if installers == []:
        return
    
    import tkinter as tk
    from tkinter import ttk
    
    try:
        loadingWindow.destroy()
    except:
        pass
    
    ttk.Label(mainUI.pluginFrame, text="The app has detected plugins that have not yet been installed.").pack()
    ttk.Label(mainUI.pluginFrame, text="Please install them before continuing.").pack()
    ttk.Label(mainUI.pluginFrame, text="").pack()
    ttk.Label(mainUI.pluginFrame, text="WARNING: Make sure you trust the authors of the plugins.").pack()
    ttk.Label(mainUI.pluginFrame, text="If you are at all skeptical then you can see the install script at").pack()
    ttk.Label(mainUI.pluginFrame, text="app/plugins/<plugin name>/installer.py").pack()
    ttk.Label(mainUI.pluginFrame, text="").pack()
    
    startInstall = False
    def SetInstallToTrue():
        global startInstall
        startInstall = True
    ttk.Button(mainUI.pluginFrame, text="Install plugins", command=lambda: SetInstallToTrue()).pack()
    
    ttk.Label(mainUI.pluginFrame, text="").pack()
    ttk.Label(mainUI.pluginFrame, text="The following plugins require installation: ").pack()
    # Make tk list object
    listbox = tk.Listbox(mainUI.pluginFrame, width=75, height=30)
    listbox.pack()
    # Add the plugins there
    for plugin in pluginNames:
        listbox.insert(tk.END, plugin)
    # Center the listbox text
    listbox.config(justify=tk.CENTER)
    
    while not startInstall:
        mainUI.root.update()
    
    # Destroy all the widgets
    for child in mainUI.pluginFrame.winfo_children():
        child.destroy()
        
    # Create the progress indicators
    currentPlugin = tk.StringVar(mainUI.pluginFrame)
    currentPlugin.set("Installing plugins...")
    ttk.Label(mainUI.pluginFrame, textvariable=currentPlugin).pack()
    bar = ttk.Progressbar(mainUI.pluginFrame, orient=tk.HORIZONTAL, length=200, mode='determinate')
    bar.pack(pady=15)
    percentage = tk.StringVar(mainUI.pluginFrame)
    ttk.Label(mainUI.pluginFrame, textvariable=percentage).pack()
    ttk.Label(mainUI.pluginFrame, text="").pack()
    ttk.Label(mainUI.pluginFrame, text="This may take a while...").pack()
    ttk.Label(mainUI.pluginFrame, text="For more information check the console.").pack()
    
    mainUI.root.update()
    
    loadingWindow = loading.LoadingWindow("Installing plugins...")
    
    index = 0
    for installer, name in zip(installers, pluginNames):
        print(f"Installing '{name}'...")
        currentPlugin.set(f"Installing '{name}'...")
        bar.config(value=(index / len(installers)) * 100)
        percentage.set(f"{round((index / len(installers)) * 100)}%")
        mainUI.root.update()
        installer.install()
        settings.AddToList("Plugins", "Installed", name.split(" - ")[0])
        index += 1
        loadingWindow.update(text=f"Installing '{name}'...")
    
    # Destroy all the widgets
    for child in mainUI.pluginFrame.winfo_children():
        child.destroy()
        

def CheckForONNXRuntimeChange():
    change = settings.GetSettings("SwitchLaneDetectionDevice", "switchTo")
    if change != None:
        if change == "GPU":
            loadingWindow.update(text="Uninstalling ONNX...")
            os.system("pip uninstall onnxruntime -y")
            loadingWindow.update(text="Installing ONNX GPU...")
            os.system("pip install onnxruntime-gpu")
        else:
            loadingWindow.update(text="Uninstalling ONNX GPU...")
            os.system("pip uninstall onnxruntime-gpu -y")
            loadingWindow.update(text="Installing ONNX...")
            os.system("pip install onnxruntime")
            
    settings.CreateSettings("SwitchLaneDetectionDevice", "switchTo", None)

def CheckLastKnownVersion():
    lastVersion = settings.GetSettings("User Interface", "version")
    if lastVersion == None:
        settings.UpdateSettings("User Interface", "version", variables.VERSION)
        mainUI.switchSelectedPlugin("plugins.Changelog.main")
        return
    
    if lastVersion != variables.VERSION:
        settings.UpdateSettings("User Interface", "version", variables.VERSION)
        mainUI.switchSelectedPlugin("plugins.Changelog.main")
        return
    
def CloseAllPlugins():
    for plugin in pluginObjects:
        plugin.onDisable()
        del plugin
        

def LoadApplication():
    global mainUI
    global uiUpdateRate
    global loadingWindow

    loadingWindow = loading.LoadingWindow("Please wait initializing...")
    
    try:
        mainUI.DeleteRoot()
        del mainUI
        import src.mainUI as mainUI
        mainUI.CreateRoot()
    except:
        pass
    

    CheckForONNXRuntimeChange()

    # Check for new plugin installs
    InstallPlugins()

    # Load all plugins 
    loadingWindow.update(text="Loading plugins...")
    GetEnabledPlugins()
    FindPlugins()
    loadingWindow.update(text="Initializing plugins...")
    RunOnEnable()

    logger.printDebug = settings.GetSettings("logger", "debug")
    if logger.printDebug == None:
        logger.printDebug = False
        settings.CreateSettings("logger", "debug", False)

    # We've loaded all necessary modules
    mainUI.root.title("Lane Assist - " + open(settings.currentProfile, "r").readline().replace("\n", ""))
    mainUI.root.update()
    mainUI.drawButtons()

    loadingWindow.destroy()
    del loadingWindow

    uiUpdateRate = settings.GetSettings("User Interface", "updateRate")
    if uiUpdateRate == None: 
        uiUpdateRate = 0
        settings.CreateSettings("User Interface", "updateRate", 0)

    CheckLastKnownVersion()

LoadApplication()

data = {}
uiFrameTimer = 0
while True:
    # Main Application Loop
    try:
        
        allStart = time.time()
        
        # Remove "last" from the data and set it as this frame's "last"
        try: 
            data.pop("last")
            data = {
                "last": data, 
                "executionTimes": {}
            }
        except Exception as ex:
            data = {
                "last": {},
                "executionTimes": {}
            }  
        
        if variables.RELOAD:
            print("Reloading application...")
            LoadApplication()
            variables.RELOAD = False
        
        # Enable / Disable the main loop
        if variables.ENABLELOOP == False:
            mainUI.update(data)
            allEnd = time.time()
            data["executionTimes"]["all"] = allEnd - allStart
            continue
        
        if variables.UPDATEPLUGINS:
            GetEnabledPlugins()
            FindPlugins()
            variables.UPDATEPLUGINS = False
        
        UpdatePlugins("before image capture", data)
        UpdatePlugins("image capture", data)
        
        UpdatePlugins("before lane detection", data)
        UpdatePlugins("lane detection", data)
        
        UpdatePlugins("before controller", data)
        UpdatePlugins("controller", data)
        
        UpdatePlugins("before game", data)
        UpdatePlugins("game", data)
        
        UpdatePlugins("before UI", data)
        
        # Calculate the execution time of the UI
        start = time.time()
        uiFrameTimer += 1
        if uiFrameTimer > uiUpdateRate:
            mainUI.update(data)
            uiFrameTimer = 0
        end = time.time()
        data["executionTimes"]["UI"] = end - start
        
        UpdatePlugins("last", data)
        
        # And then the entire app
        allEnd = time.time()
        data["executionTimes"]["all"] = allEnd - allStart

    
    except Exception as ex:
        if ex.args != ('The main window has been closed.', 'If you closed the app this is normal.'):
            from tkinter import messagebox
            import traceback
            exc = traceback.format_exc()
            traceback.print_exc()
            # Pack everything in ex.args into one string
            if not messagebox.askretrycancel("Error", translator.Translate("The application has encountered an error in the main thread!\nPlease either retry execution or close the application (cancel)!\n\n") + exc):
                break
            else:
                pass
        else:
            CloseAllPlugins()
            break