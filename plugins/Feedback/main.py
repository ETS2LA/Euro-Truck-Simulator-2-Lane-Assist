"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Feedback", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    # In case the plugin is not the main file (for example plugins\Panel\Panel.py) then the name would be "Panel.Panel"
    
    description="A simple panel to send feedback to the devs.",
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
from src.server import SendCrashReport

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def sendReport(self):
            if self.description.get("1.0", tk.END) == "\n" or self.description.get("1.0", tk.END) == "": return
            success = SendCrashReport("FEEDBACK, NOT A CRASH", self.description.get("1.0", tk.END), self.optional.get("1.0", tk.END))
            if success:
                helpers.ShowPopup("\nFeedback sent", "Feedback", timeout=2)
            else:
                helpers.ShowPopup("\nThere was an error", "Feedback", timeout=2)
        
        def exampleFunction(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=800, height=1200, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Create a large text box for the input
            helpers.MakeLabel(self.root, text="                   ", row=0, column=0)
            helpers.MakeLabel(self.root, text="Description", row=0, column=1, columnspan=2, font=("Segoe UI", 12, "bold"))
            self.description = tk.Text(self.root, width=65, height=10, border=1, highlightthickness=0)
            self.description.grid(row=1, column=1, columnspan=1, padx=10, pady=10)
            helpers.MakeLabel(self.root, text="Optional information", row=2, column=1, font=("Segoe UI", 12, "bold"))
            self.optional = tk.Text(self.root, width=65, height=10, border=1, highlightthickness=0)
            self.optional.grid(row=3, column=1, columnspan=1, padx=10, pady=10)
            
            # Check if crash reporting is allowed
            if not settings.GetSettings("CrashReporter", "AllowCrashReports"):
                helpers.MakeLabel(self.root, text="Please enable crash reporting.", row=4, column=1, columnspan=1, font=("Segoe UI", 8, "bold"), fg="red")
                helpers.MakeButton(self.root, text="Open Settings", row=5, column=1, command=lambda: mainUI.switchSelectedPlugin("plugins.Settings.main"))
            else:
                helpers.MakeButton(self.root, text="Send", row=4, column=1, command=self.sendReport)
                helpers.MakeLabel(self.root, text="This report is sent exactly the same way as the crash reports are.\nUnless you've included such information\nwe cannot identify these reports in any way. They are anonymous.", row=6, column=1, font=("Segoe UI", 8), fg="gray")
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)