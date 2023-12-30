"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ExternalAPI", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will post the application data to\nlocalhost:39847\nUsed for external applications.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="last" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import numpy as np

url = "localhost"
port = settings.GetSettings("ExternalAPI", "port")

if port == None:
    settings.CreateSettings("ExternalAPI", "port", 39847)
    port = 39847

currentData = {}
close = False

# Send the data variable to the external application
class HttpHandler(BaseHTTPRequestHandler):
    global currentData
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", len(json.dumps(currentData)))
        self.end_headers()
        self.wfile.write(bytes(json.dumps(currentData), "utf-8"))
        
    # Disable logging
    def log_message(self, format, *args):
        return

def ServerThread():
    global close
    global server
    
    while not close:
        try:
            server.handle_request()
        except:
            pass
        time.sleep(0.1) # 10fps


def CreateServer():
    print("Starting server")
    global server
    global serverThread
    server = HTTPServer((url, port), HttpHandler)
    server.timeout = 0.1
    
    serverThread = threading.Thread(target=ServerThread)
    serverThread.start()
    

def convert_ndarrays(obj):
    if isinstance(obj, np.ndarray):
        return "ndarray not supported"
    elif isinstance(obj, dict):
        return {key: convert_ndarrays(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarrays(value) for value in obj]
    else:
        return obj

def plugin(data):
    global currentData
    tempData = {}
    # Go though the data and if there are any ndarrays then convert them to lists
    for key in data:
        if key == "frame" or key == "frameFull":
            tempData[key] = "too large to send"
            continue
        
        if key == "GPS":
            from plugins.Map.GameData.roads import RoadToJson
            tempData[key] = data[key]
            tempData[key]["roads"] = [RoadToJson(road) for road in data[key]["roads"]]
            continue
        
        tempData[key] = data[key]


    currentData = convert_ndarrays(tempData)
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    CreateServer()
    pass

def onDisable():
    global close
    global serverThread
    
    close = True
    serverThread.join()
    
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

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            def savenewport():
                print(self.newport.get())
                settings.CreateSettings("ExternalAPI", "port", self.newport.get())
            def validate_entry(text):
                # Make sure that only integers can be typed
                return text.isdecimal()

            ttk.Label(self.root, text="Port").grid(row=1, padx=5, pady=5)
            self.newport = tk.IntVar()
            ttk.Entry(self.root, validate="key", textvariable=self.newport,
    validatecommand=(self.root.register(validate_entry), "%S")).grid(row=2, padx=5, pady=5)
            ttk.Button(self.root, text="Save", command=savenewport).grid(row=3, padx=5, pady=5)

            ttk.button(self.root, text="button").grid()
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
