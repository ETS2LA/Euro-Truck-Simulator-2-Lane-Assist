"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="About", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="About panel.",
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
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def findDevelopers(self):
            path = os.path.join(variables.PATH, "plugins")
            developers = []
            for file in os.listdir(path):
                if os.path.isdir(os.path.join(path, file)):
                    # Check for main.py
                    if "main.py" in os.listdir(os.path.join(path, file)):
                        # Check for PluginInformation class
                        try:
                            pluginPath = "plugins." + file + ".main"
                            plugin = __import__(pluginPath, fromlist=["PluginInformation"])
                            authors = plugin.PluginInfo.author.split(",")
                            for author in authors:
                                if author.strip() not in developers:
                                    developers.append(author.strip())
                        except Exception as ex:
                            print(ex.args)
                            pass
        
            
            return developers
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            helpers.MakeLabel(self.root, "About", 0,0, font=("Roboto", 20, "bold"), padx=0, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "The app backend was made by Tumppi066. In addition to the following plugin developers:", 1,0, font=("Roboto", 10), padx=0, pady=10, columnspan=2)
            developers = self.findDevelopers()
            helpers.MakeLabel(self.root, ", ".join(developers), 2,0, font=("Roboto", 8), padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, " ", 3,0, font=("Roboto", 10), padx=0, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "To all those who supported me:", 4,0, font=("Roboto", 10), padx=0, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Thank you from the bottom of my heart!", 5,0, font=("Roboto", 20, "bold"), padx=0, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, " ", 6,0, padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "In addition this app wouldn't be possible without the work of ibaiGorordo, who translated ", 7,0, padx=30, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "all the models I used in the default plugins to pytorch and onnx.", 8,0, padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "And of course the researchers who made those models in the first place!", 9,0, padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, " ", 10,0, padx=30, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "I'm also going to give a shoutout to the developers of sv_ttk and dxcam. They have been essential ", 11,0, padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "in the development of this app.", 12,0, padx=0, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, " ", 13,0, padx=0, pady=2, columnspan=2)
            
            import webbrowser
            helpers.MakeButton(self.root, "Support me on Ko-fi", lambda: webbrowser.open("https://ko-fi.com/tumppi066"), 14,0, padx=0, pady=10, columnspan=3, width=20, style="Accent.TButton")
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)