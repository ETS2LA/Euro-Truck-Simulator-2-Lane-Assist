"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Wiki", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will show the wiki.",
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
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

RESET = True

def LoadURL(url):
    global RESET
    RESET = False
    mainUI.switchSelectedPlugin("plugins.Wiki.main")

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            global RESET
            self.master = master # "master" is the mainUI window
            if RESET:
                variables.WIKI_URL = "https://wiki.tumppi066.fi"
                RESET = False
            else:
                RESET = True
            self.exampleFunction()
            mainUI.resizeWindow(1336, 720)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def tabFocused(self):
            mainUI.resizeWindow(1336, 720)
        
        def exampleFunction(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=1336, height=720, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            if not have_runtime():#没有 (no) webview2 runtime
                install_runtime()
                
            self.frame=WebView2(self.root,1336,720)
            self.frame.pack()
            self.frame.load_url(variables.WIKI_URL)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            pass
    
    
    except Exception as ex:
        print(ex.args)