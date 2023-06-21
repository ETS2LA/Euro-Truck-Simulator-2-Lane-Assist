"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ShowImage", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will show the output image with cv2.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before UI", # Will run the plugin before anything else in the mainloop (data will be empty)
    noUI=True, # Will not show the UI button
    image="logo.png"
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import cv2



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
        if "-215" not in ex.args[0]:
            print(ex.args)
        return data