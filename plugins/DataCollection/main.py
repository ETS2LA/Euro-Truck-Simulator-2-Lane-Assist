"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DataCollection",
    description="Colect data for AI training.",
    version="0.1",
    author="DylDev",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic",
    dynamicOrder="before lane detection"
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.controls as controls
from src.mainUI import resizeWindow
import os
import cv2
import numpy as np
import time
from PIL import Image, ImageTk
import webbrowser
import requests
import threading
import base64
import pyautogui

def Initialize():
    global vd_data_collection, x1, y1, x2, y2, cooldown, last_capture, server_available, last_server_check
    vd_data_collection = settings.GetSettings("DataCollection", "VD Data Collection", False)

    screen_width, screen_height = pyautogui.size()
    x1 = settings.GetSettings("TrafficLightDetection", "x1ofsc", 0)
    y1 = settings.GetSettings("TrafficLightDetection", "y1ofsc", 0)
    x2 = settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1)
    y2 = settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)
    cooldown = 5
    last_capture = time.time()
    last_server_check = time.time() + 180
    server_available = "unknown"

Initialize()

def CheckServer():
    try:
        headers = {
            "Content-Type": "application/json"
        }
        r = requests.get("https://api.tumppi066.fi/heartbeat", headers=headers)
        return True
    except:
        return False
    
def SendImage(image):
    global server_available
    global last_server_check
    if last_server_check + 180 < time.time():
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == "unknown":
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == True:
        try:
            encoded_string = base64.b64encode(cv2.imencode('.png', image)[1]).decode()
            url = "https://api.tumppi066.fi/image/save"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "image": encoded_string,
                "category": "vehicle_detection_images"
            }
            response = requests.post(url, headers=headers, json=data)
        except:
            server_available = CheckServer()
            last_server_check = time.time()

def plugin(data):
    global vd_data_collection, x1, y1, x2, y2, cooldown, last_capture

    try:
        data["api"]
    except:
        return data
    if vd_data_collection and last_capture + cooldown < time.time() and data["api"]["sdkActive"] and data["api"]["pause"] == False:
        try:
            data["frameFull"]
        except:
            return data
        
        fullframe = data["frameFull"]
        frame = fullframe.copy()[y1:y2, x1:x2]
        
        SendImage(frame)
        last_capture = time.time()

    return data


def onEnable():
    pass

def onDisable():
    pass

class UI():
    try:
        
        def __init__(self, master) -> None:
            self.master = master
            self.exampleFunction()
            resizeWindow(900, 700)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):  
            try:
                self.root.destroy()
            except: pass
            
            self.root = tk.Canvas(self.master, width=900, height=700, border=0, highlightthickness=0)
            self.root.grid_propagate(0)
            self.root.pack_propagate(0)
        
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            vd_tab = ttk.Frame(notebook)
            vd_tab.columnconfigure(0, weight=1)
            vd_tab.columnconfigure(1, weight=1)
            vd_tab.columnconfigure(2, weight=1)

            ttk.Label(vd_tab, text="Vehicle Detection Data Collection", font=("Robot", 17, "bold")).grid(row=0, column=0, columnspan=2, pady=1)
            ttk.Label(vd_tab, text="", font=("Robot", 10, "bold")).grid(row=1, column=0, columnspan=2, pady=1)
            ttk.Label(vd_tab, text="Everyone has been waiting for it! Vehicle Detection is almost here!", font=("Robot", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="However, we still need some more data for the Vehicle Detection AI model.", font=("Robot", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="You can help us out by enabling this option which will send anonymous data to our server.", font=("Robot", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="This data will be used to train the AI model and nothing else.", font=("Robot", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="You can see an example of what data is collected below:", font=("Robot", 10, "bold")).grid(row=6, column=0, columnspan=2, pady=2)

            example_image_paths = ["1.png", "2.png"]
            for i, image_path in enumerate(example_image_paths):
                image_path = os.path.join(variables.PATH, "assets", "DataCollection", image_path)
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = image.resize((300, 150), resample=Image.BILINEAR)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(vd_tab, image=photo)
                image_label.grid(row=7, column=0 if i == 0 else 1, padx=10, pady=10)
                image_label.image = photo
            
            ttk.Label(vd_tab, text="Disclaimer: Every 5 seconds, a screenshot will be taken at the coordinates you select for Traffic Light Detection.", font=("Robot", 10, "bold")).grid(row=8, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="This data is public and we are not rsponsible for any personal data leaks. Do not enable unless you are in game.", font=("Robot", 10, "bold")).grid(row=9, column=0, columnspan=2, pady=2)

            def CheckbuttonCallback():
                if vd_data_collection_var.get() == True:
                    screen_cap_dialog = helpers.Dialog("Vehicle Detection Data Collection - Screen Capture", "In order to do Vehicle Detection Data Collection, you need to set a screen capture.\nFor simplicity, data collection uses your traffic light detection screen capture.\nJust go to the Traffic Light Detection plugin, and set your screen capture out of the windshield.", ["Cancel", "Set Screen Capture"])
                    if screen_cap_dialog == "Set Screen Capture":
                        mainUI.switchSelectedPlugin("plugins.TrafficLightDetection.main")
                    else:
                        pass
        
            vd_data_collection_var = helpers.MakeCheckButton(vd_tab, "Enable Data Collection (Anonymous data will be sent to our server)", "DataCollection", "VD Data Collection", 10, 0, width=80, columnspan=2, callback=CheckbuttonCallback)
            helpers.MakeButton(vd_tab, "View Collected Data", lambda: webbrowser.open("https://filebrowser.tumppi066.fi/share/Uw850Xow"), 11, 0, width=150, sticky="nw", columnspan=2)
            
            tl_tab = ttk.Frame(notebook)
            tl_tab.columnconfigure(0, weight=1)
            tl_tab.columnconfigure(1, weight=1)
            tl_tab.columnconfigure(2, weight=1)

            ttk.Label(tl_tab, text="Traffic Light Detection Data Collection", font=("Robot", 18, "bold")).grid(row=0, column=0, columnspan=3)
            ttk.Label(tl_tab, text="", font=("Robot", 10, "bold")).grid(row=1, column=0, columnspan=3, pady=1)
            ttk.Label(tl_tab, text="Traffic light detection is undergoing some changes which will make it faster and better!", font=("Robot", 10, "bold")).grid(row=2, column=0, columnspan=3, pady=2)
            ttk.Label(tl_tab, text="This includes an AI model that will detect traffic lights with very high accuracy.", font=("Robot", 10, "bold")).grid(row=3, column=0, columnspan=3, pady=2)
            ttk.Label(tl_tab, text="If you want to help collect some data for this model, head over to the TFLD plugin.", font=("Robot", 10, "bold")).grid(row=4, column=0, columnspan=3, pady=2)
            ttk.Label(tl_tab, text="Use this button to go to the Traffic Light Detection plugin", font=("Robot", 10, "bold")).grid(row=5, column=0, columnspan=3, pady=2)

            helpers.MakeButton(tl_tab, "Go to Traffic Light Detection", lambda: mainUI.switchSelectedPlugin("plugins.TrafficLightDetection.main"), 6, 0, width=150, sticky="nw", columnspan=3)
            
            notebook.add(vd_tab, text="Vehicle Detection")
            notebook.add(tl_tab, text="Traffic Light Detection")
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def tabFocused(self): # Called when the tab is focused
            pass
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)