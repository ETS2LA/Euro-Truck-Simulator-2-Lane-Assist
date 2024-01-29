"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="HUD", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Heads up display for essential data.",
    version="0.2",
    author="Tumppi066, DTheIcyDragon",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game",
    noUI=True, # Will not show the UI button
)

import tkinter as tk
from tkinter import ttk
import src.settings as settings
from PIL import Image, ImageTk
import numpy as np
import src.helpers as helpers

def plugin(data):
    global root
    global fps
    
    try:
        if root.winfo_exists() == 0:
            pass
    except:
        x = settings.GetSettings("bettercam", "x")
        y = settings.GetSettings("bettercam", "y")
        width = settings.GetSettings("bettercam", "width")
        height = settings.GetSettings("bettercam", "height")
        print("Creating Window")
        CreateWindow(x,y,width,height)
        print("Window Created")
    
    try:
        fps.config(text="FPS: " + str(round(1/data["last"]["executionTimes"]["all"], 1)))
        speed.config(text="Speed: " + str(round(data["last"]["api"]["truckFloat"]["speed"]*3.6, 1)) + str(" ({})".format(round(data["last"]["api"]["truckFloat"]["speedLimit"]*3.6, 1))))
        cruise.config(text="Cruise: " + str(round(data["last"]["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)))
        
        root.update()
        
    except Exception as ex:
        print(ex)
        pass
    
    return data
    
def onDisable():
    global root
    try:
        root.destroy()
    except: pass
    return True


def onEnable():
    pass


def CreateWindow(x,y,w,h):
    global root
    global fps
    global speed
    global cruise

    try:
        root.destroy()
    except: pass
    
    root = tk.Tk()
    root.config(bg="black", border=0)
    root.geometry("{}x{}+{}+{}".format(w, h, x, y))

    canvas = tk.Canvas(root, width=w, height=h, border=0, highlightthickness=0)
    canvas.config(bg="black")
    canvas.grid_propagate(0) # Don't fit the canvast to the widgets
    canvas.pack_propagate(0)
    canvas.pack(anchor="center", expand=False)
    
    # Create a text object
    fps = helpers.MakeLabel(canvas, "FPS: 30", 0,0, padx=10, pady=10, fg="white", bg="black")
    speed = helpers.MakeLabel(canvas, "Speed: 0", 1,0, padx=10, pady=10, fg="white", bg="black")
    cruise = helpers.MakeLabel(canvas, "Cruise: 0", 2,0, padx=10, pady=10, fg="white", bg="black")
    
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "black")
    root.update()
