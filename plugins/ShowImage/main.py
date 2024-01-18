"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="ShowImage", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will show the output image with cv2.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before UI", # Will run the plugin before anything else in the mainloop (data will be empty)
    image="opencv.png"
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.translator import Translate
import os
import cv2

def onEnable():
    pass

def onDisable():
    pass

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    try:
        frame = data["frame"]
        cv2.namedWindow("Lane Assist", cv2.WINDOW_NORMAL)
        # Make it on top
        cv2.setWindowProperty("Lane Assist", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Lane Assist", frame)
        return data
    
    except Exception as ex:
        if "-215" not in ex.args[0] and "frame" not in ex.args[0]:
            print(ex.args)
        return data
    
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur

        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
            resizeWindow(900,600)
        
        def tabFocused(self):
            resizeWindow(900,600)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def UpdateScaleValueFromSlider(self):
            self.windowscale.set(self.windowscaleSlider.get())
            settings.CreateSettings("ShowImage", "windowscale", self.windowscaleSlider.get())
        
        def exampleFunction(self):
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=800, height=580, border=0, highlightthickness=0)
            self.root.grid_propagate(0) 
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            notebook.add(generalFrame, text=Translate("General"))
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
            
            helpers.MakeButton(generalFrame, "Save window location", self.save_position, 2, 0, width=90)
            helpers.MakeButton(generalFrame, "Set to normal aspect ratio, apply scale and save window location", self.set_aspect_ratio, 3, 0, width=90)
            self.windowscaleSlider = tk.Scale(generalFrame, from_=0.1, to=3, resolution=0.01, orient=tk.HORIZONTAL, length=480, command=lambda x: self.UpdateScaleValueFromSlider())
            self.windowscaleSlider.set(settings.GetSettings("ShowImage", "windowscale", 1))
            self.windowscaleSlider.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.windowscale = helpers.MakeComboEntry(generalFrame, "Window Scale", "ShowImage", "windowscale", 4, 0)
            helpers.MakeEmptyLine(generalFrame, 5, 0)
            helpers.MakeLabel(generalFrame, "Note:\nMake sure that the app and this plugin are enabled and the window is visible\nfor the buttons and the slider to take action!", 6, 0, sticky="nw")

        def set_aspect_ratio(self):
            try:
                windowwidth = settings.GetSettings("dxcam", "width")
                windowheight = settings.GetSettings("dxcam", "height")
                cv2.resizeWindow('Lane Assist', round(windowwidth*self.windowscaleSlider.get()), round(windowheight*self.windowscaleSlider.get()))
                cv2.destroyWindow('Lane Assist')
            except:
                pass

        def save_position(self):
            try:
                cv2.destroyWindow('Lane Assist')
            except:
                pass

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    except Exception as ex:
        print(ex.args)