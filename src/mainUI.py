from src.logger import print

'''
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.
'''

import time
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import src.helpers as helpers
from tkinter import font
import src.variables as variables
from src.loading import LoadingWindow
from src.logger import print

width = 800
height = 600

root = tk.Tk()
root.title("Lane Assist")


root.resizable(False, False)
root.geometry(f"{width}x{height}")
root.protocol("WM_DELETE_WINDOW", lambda: quit())

sv_ttk.set_theme("dark")

ttk.Label(root, text="ETS2 Lane Assist    ©Tumppi066 - 2023", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
fps = tk.StringVar()
ttk.Label(root, textvariable=fps, font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)

buttonFrame = ttk.LabelFrame(root, text="Lane Assist", width=width-675, height=height-20)
buttonFrame.pack_propagate(0)
buttonFrame.grid_propagate(0)
helpers.MakeButton(buttonFrame, "Panels", lambda: switchSelectedPlugin("plugins.PanelManager.main"), 0, 0, width=10, padx=8)
helpers.MakeButton(buttonFrame, "Plugins", lambda: switchSelectedPlugin("plugins.PluginManager.main"), 1, 0, width=10, padx=8)
themeButton = helpers.MakeButton(buttonFrame, sv_ttk.get_theme().capitalize(), lambda: changeTheme(), 2, 0, width=10, padx=8)


buttonFrame.pack(side="left", anchor="n", padx=10, pady=10)
pluginFrame = ttk.LabelFrame(root, text="Selected Plugin", width=width, height=height-20)
pluginFrame.pack_propagate(0)
pluginFrame.grid_propagate(0)
helpers.MakeLabel(pluginFrame, "Click 'Panels' on the left bar to start!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
helpers.MakeLabel(pluginFrame, "If this is your first time running the app, it is recommended to open the 'FirstTimeSetup' panel!", 1,0, font=("Roboto", 10), padx=30, pady=10, columnspan=2)
pluginFrame.pack(side="left", anchor="w", padx=10, pady=10)

root.update()


def quit():
    global root
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # Destroy the root window
        root.destroy()
        del root

prevFrame = 100
def update():
    global fps
    global prevFrame
    
    # Calculate the UI caused overhead
    frame = time.time()
    try:
        fps.set(f"UI Overhead: {round((frame-prevFrame)*1000)}ms ({round(1/(frame-prevFrame))}fps)")
    except: pass
    prevFrame = frame
        
    try:
        ui.update()
    except:
        pass

    try:
        root.update()
    except:
        raise Exception("The main window has been closed.", "If you closed the app this is normal.")
    
def switchSelectedPlugin(pluginName):
    global pluginFrame
    global ui

    try:
        pluginFrame.destroy()
    except:
        pass

    pluginFrame = ttk.LabelFrame(root, text=pluginName.split(".")[1], width=width, height=height-20)
    pluginFrame.pack_propagate(0)
    pluginFrame.grid_propagate(0)
    plugin = __import__(pluginName, fromlist=["UI"])
    ui = plugin.UI(pluginFrame)
    pluginFrame.pack(side="left", anchor="n", padx=10, pady=10, expand=True)
    
    print("Loaded " + pluginName)
    
def changeTheme():
    global themeButton
    #loading = LoadingWindow("Changing theme...", root)
    sv_ttk.toggle_theme()
    themeButton.config(text=sv_ttk.get_theme().capitalize())
    #loading.destroy()