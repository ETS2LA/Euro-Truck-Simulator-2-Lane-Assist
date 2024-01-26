

from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DataViewer", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Shows the current data in the data variable.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Cloud-121/ETS2-Python-Api",
    type="static", # = Panel
    dynamicOrder="last" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.loading import LoadingWindow
from src.translator import Translate
import src.mainUI as mainUI
import time
import os
import math

# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
    pass

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def readData(self, key, value, depth):
            if type(value) != dict:
                self.list.insert(tk.END, " " * depth + key + ": " + str(value))
            else:
                self.list.insert(tk.END, " " * depth + " " + key + ":")
                for key2, value2 in value.items():
                    self.readData(key2, value2, depth + 1)
            

        def updateData(self):
            self.list.delete(0, tk.END)
            # recursively get all the data
            self.readData("data", self.data, 0)
    
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            # Create a toggle to toggle updating the data
            self.toggle = tk.BooleanVar()
            self.toggle.set(True)
            self.toggleButton = tk.Checkbutton(self.root, text="Update data", variable=self.toggle)
            self.toggleButton.pack(anchor="w")
            # Create a list to hold all of the data
            self.listVar = tk.StringVar()
            self.list = tk.Listbox(self.root, width=600, height=520, border=0, highlightthickness=0, listvariable=self.listVar)
            self.list.pack()
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.data = data
            if self.toggle.get():
                self.updateData()
            self.root.update()
    
    except Exception as ex:
        print(ex.args)