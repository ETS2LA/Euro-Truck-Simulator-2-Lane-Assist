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
            window = LoadingWindow("Uninstalling ONNX...")
            os.system("pip uninstall onnxruntime -y")
            window.update(text="Installing ONNX GPU...")
            os.system("pip install onnxruntime-gpu -y")
            window.destroy()
        
        def convertToCPU(self):
            window = LoadingWindow("Uninstalling ONNX GPU...")
            os.system("pip uninstall onnxruntime-gpu -y")
            window.update(text="Installing ONNX...")
            os.system("pip install onnxruntime -y")
            window.destroy()
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeButton(self.root, "Convert to GPU runtime.", lambda: self.convertToGPU(), 1,0, padx=30, pady=10, width=30)
            helpers.MakeButton(self.root, "Convert to CPU runtime.", lambda: self.convertToCPU(), 1,1, padx=30, pady=10, width=30)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)