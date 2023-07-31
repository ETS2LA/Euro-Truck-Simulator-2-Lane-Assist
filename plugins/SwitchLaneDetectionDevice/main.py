"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="SwitchLaneDetectionDevice", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will convert your ONNX version to the GPU one.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
from src.loading import LoadingWindow
import subprocess

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def convertToGPU(self):
            settings.CreateSettings("SwitchLaneDetectionDevice", "switchTo", "GPU")
            from tkinter import messagebox
            messagebox.showinfo("Restart required", "Please restart the program for the changes to take effect.")

        
        def convertToCPU(self):
            settings.CreateSettings("SwitchLaneDetectionDevice", "switchTo", "CPU")
            from tkinter import messagebox
            messagebox.showinfo("Restart required", "Please restart the program for the changes to take effect.")
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeButton(self.root, "Convert to GPU runtime.", lambda: self.convertToGPU(), 1,0, padx=30, pady=10, width=25)
            helpers.MakeButton(self.root, "Convert to CPU runtime.", lambda: self.convertToCPU(), 1,1, padx=30, pady=10, width=25)
            
            import webbrowser
            helpers.MakeButton(self.root, "Open Instructions to downloading NVIDIA files.", lambda: webbrowser.open("https://wiki.tumppi066.xyz/en/LaneAssist/Installation"), 2,0, padx=30, pady=10, width=60, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)