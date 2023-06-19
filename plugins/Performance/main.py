"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Performance", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will display current app performance.",
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

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.once = False
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            self.fps = helpers.MakeLabel(self.root, "", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=1)
            self.list = ttk.Treeview(self.root, columns=("plugin", "ms"), show="headings", height=12)
            self.list.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
            helpers.MakeLabel(self.root, "Running this constantly would take a lot of cpu power so use the button to manually update!", 2,0, font=("Roboto", 10), padx=30, pady=10)
            helpers.MakeLabel(self.root, "* all information is for the last frame", 3,0, font=("Roboto", 10), padx=30, pady=10)
            self.toggle = tk.BooleanVar()
            # ttk.Checkbutton(self.root, text="Update list", variable=self.toggle).grid(row=1, column=1, padx=10, pady=10)
            helpers.MakeButton(self.root, "Update", lambda: self.updateOnce(), 4,0, padx=10, pady=10, width=15)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def updateOnce(self):
            self.once = True
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
            data = data["last"] # Get last frame's data
            try:
                lastFrameTime = data["executionTimes"]["all"]
                fps = 1/lastFrameTime
                ms = lastFrameTime*1000
                self.fps.set(f"{round(fps)} fps ({round(ms, 1)} ms)")
                
                if (self.toggle.get() == True or self.once == True):
                    self.once = False
                    self.list.delete(*self.list.get_children())
                    for plugin in data["executionTimes"]:
                        self.list.insert("", "end", values=(plugin, round(data["executionTimes"][plugin]*1000, 1)))
                    
            except Exception as ex:
                print(ex.args)
    
    
    except Exception as ex:
        print(ex.args)