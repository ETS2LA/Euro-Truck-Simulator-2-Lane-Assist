from plugins.plugin import PluginInformation

PluginInfo = PluginInformation(
    name="PluginLoader",
    description="Loads plugins",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist"
)


import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
from src.mainUI import quit
import src.variables as variables
import src.settings as settings


class UI():
    
    def __init__(self, master) -> None:
        self.done = False
        self.master = master
        self.page0()
    
    def destroy(self):
        self.done = True
        self.root.destroy()
        del self

    
    def page0(self):
        
        #helpers.MakeLabel(self.master, "Welcome", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
        
        try:
            self.root.destroy()
        except: pass
        
        self.root = tk.Canvas(self.master, width=650, height=500)
        self.root.grid_propagate(0)
        
        helpers.MakeLabel(self.root, "Plugin Manager", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
        
        
        
        self.root.pack(anchor="center", expand=False)
        
        self.root.update()
    
    
    def update(self):
        self.root.update()
    