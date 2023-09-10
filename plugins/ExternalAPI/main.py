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
    server.timeout = 0.001
    
    serverThread = threading.Thread(target=ServerThread)
    serverThread.start()
    

def plugin(data):
    global currentData
    currentData = data
    
    # Go though the data and if there are any ndarrays then convert them to lists
    for key in currentData:
        if type(currentData[key]) == np.ndarray:
            if key != "frame":
                currentData[key] = currentData[key].tolist()
            else:
                currentData[key] = "Frame is not provided through the api..."
    

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