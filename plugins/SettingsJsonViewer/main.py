"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="SettingsJsonViewer", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will allow you to edit the settings.json file in app.",
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
import pygments.lexers
from chlorophyll import CodeView

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master, filename="/profiles/settings.json") -> None:
            self.master = master # "master" is the mainUI window
            self.defaultFileName = filename
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.filename = helpers.MakeComboEntry(self.root, "Filename", "Settings Json Viewer", "filename", 0, 0, width=15, isString=True, value=self.defaultFileName)
            helpers.MakeButton(self.root, "Open", lambda: self.open(), 0, 1)
            
            self.codeview = CodeView(self.root, lexer=pygments.lexers.JsonLexer, color_scheme="mariana", tab_width=6)
            self.codeview.grid(row=1, column=0, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def open(self):
            # Remake the codeview
            self.codeview.destroy()
            self.codeview = CodeView(self.root, lexer=pygments.lexers.JsonLexer, color_scheme="mariana", tab_width=6)
            self.codeview.grid(row=1, column=0, columnspan=2)
            
            settings.CreateSettings("Settings Json Viewer", "filename", self.filename.get())
            
            with open(variables.PATH + self.filename.get()) as f:
                lines = f.readlines()
                for line in lines:
                    self.codeview.insert("end", line)
            
            self.root.update()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)