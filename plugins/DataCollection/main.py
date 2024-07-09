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
import subprocess
import tqdm

def OptInDialog():
    '''
    Dialog to opt in or out of data collection.
    '''
    selection = helpers.Dialog("Vehicle Detection Data Collection", "Hey there! It looks lie you have Vehicle Detection Data Collection enabled.\nWe have collected enough images through the windshield to train the main AI to detect objects.\nHowever, we need to train a model to detect vehicles in the mirrors to assist in lane changing.\nAll you need to do is press F2 in the game until both mirrors are shown at the top of your screen.\nIt is also higly recommended to turn up your mirror resolution and distance in the ETS2 Settings.\nIt would also help if you use the Borderless Gaming application, you can click the button below to get it.\nNOTE: This will take a screenshot of your screen where the mirrors are every 5 seconds.\nPlase stay in game while using this plugin to avoid leaking private data.\nWe aren't responsible if any of your personal data gets leaked (the images are public).\nThank you for your continued support, we really appreciate it and it helps us continue to develop ETS2LA!\n\nYou can opt out if you would not like to collect data or accept to start collecting.", options=["Opt Out", "Accept", "Accept and Install Borderless Gaming"])
    if selection == "Opt Out":
        settings.CreateSettings("VehicleDetectionDataCollection", "enabled", False)
    else:
        settings.CreateSettings("VehicleDetectionDataCollection", "enabled", True)
        if "DataCollection" not in settings.GetSettings("Plugins", "Enabled"):
            settings.AddToList("Plugins", "Enabled", "DataCollection")
        
        if selection == "Accept and Install Borderless Gaming":
            print("Downloading Borderless Gaming...")
            if os.path.exists(os.path.join(variables.PATH, "assets", "BorderlessGaming")) == False:
                os.mkdir(os.path.join(variables.PATH, "assets", "BorderlessGaming"))
                open(os.path.join(variables.PATH, "assets", "BorderlessGaming", "BorderlessGaming.exe"), 'a').close()
            borderless_gaming_path = os.path.join(variables.PATH, "assets", "BorderlessGaming", "BorderlessGaming.exe")

            response = requests.get("https://github.com/Codeusa/Borderless-Gaming/releases/download/9.5.6/BorderlessGaming9.5.6_admin_setup.exe", stream=True)
            with open(borderless_gaming_path, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    if data:
                        file.write(data)

            helpers.ShowSuccess(text="Borderless Gaming was download successfully!\nYou should now follow the instructions in the dialog to complete installation.\nOnce the install is complete you should open the program and set ETS2 to borderless.\nThen press F2 to get the mirrors on screen.\nThank you for your support!", title="Borderless Gaming Downloaded!")
            print(f"Borderless Gaming downloaded and saved to {borderless_gaming_path}")
            subprocess.Popen(borderless_gaming_path)
    settings.CreateSettings("VehicleDetectionDataCollection", "dialog_shown", True)

def CalculateMirrorCoordinates(window):
    '''
    Calculates the mirror coordinates based on the game coordinates.

    Args:
        window (tuple): The game coordinates. (x1, y1, x2, y2)

    Returns:
        tuple: Both mirror coordinates. ((left_x1, left_y1, left_x2, left_y2), (right_x1, right_y1, right_x2, right_y2))
    '''

    mirrorDistanceFromLeft = 23
    mirrorDistanceFromTop = 90
    mirrorWidth = 273
    mirrorHeight = 362
    scale = (window[3] - window[1])/1080

    xCoord = window[0] + (mirrorDistanceFromLeft * scale)
    yCoord = window[1] + (mirrorDistanceFromTop * scale)
    left_top_left = (round(xCoord), round(yCoord))

    xCoord = window[0] + (mirrorDistanceFromLeft * scale + mirrorWidth * scale)
    yCoord = window[1] + (mirrorDistanceFromTop * scale + mirrorHeight * scale)
    left_bottom_right = (round(xCoord), round(yCoord))

    right_top_left = window[0] + window[2] - left_bottom_right[0] - 1, left_top_left[1]
    right_bottom_right = window[0] + window[2] - left_top_left[0] - 1, left_bottom_right[1]

    return ((left_top_left[0], left_top_left[1], left_bottom_right[0], left_bottom_right[1]), (right_top_left[0], right_top_left[1], right_bottom_right[0], right_bottom_right[1]))

def Initialize():
    global vd_data_collection, cooldown, last_capture, server_available, last_server_check, last_github_version_check, last_game_coords, game_coords, mirror_coords, app_on_newest_version

    vd_data_collection = settings.GetSettings("VehicleDetectionDataCollection", "enabled", True)
    dialog_shown = settings.GetSettings("VehicleDetectionDataCollection", "dialog_shown", False)

    #screen_width, screen_height = pyautogui.size()
    #x1 = settings.GetSettings("TrafficLightDetection", "x1ofsc", 0)
    #y1 = settings.GetSettings("TrafficLightDetection", "y1ofsc", 0)
    #x2 = settings.GetSettings("TrafficLightDetection", "x2ofsc", screen_width-1)
    #y2 = settings.GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)

    cooldown = 5
    last_capture = time.time()
    last_server_check = time.time() + 180
    last_github_version_check = 0
    server_available = "unknown"
    game_coords = (0, 0, 0, 0)
    last_game_coords = (1, 1, 1, 1)
    mirror_coords = ((0, 0, 0, 0), (0, 0, 0, 0))
    app_on_newest_version = True

    if vd_data_collection == True and dialog_shown == False:
        OptInDialog()

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
    
'''
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
            print("Vehicle Detection Data Collection - Image Saved!")
        except:
            server_available = CheckServer()
            last_server_check = time.time()
'''

def SendMirrorImages(mirror1, mirror2):
    global server_available
    global last_server_check
    if last_server_check + 180 < time.time():
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == "unknown":
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == True:
        mirror1 = cv2.cvtColor(mirror1, cv2.COLOR_BGR2GRAY)
        mirror2 = cv2.cvtColor(mirror2, cv2.COLOR_BGR2GRAY)
        try:
            encoded_string = base64.b64encode(cv2.imencode('.png', mirror1)[1]).decode()
            url = "https://api.tumppi066.fi/image/save"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "image": encoded_string,
                "blackAndWhite": True,
                "category": "vehicle_detection_images"
            }
            response = requests.post(url, headers=headers, json=data)
            
            encoded_string = base64.b64encode(cv2.imencode('.png', mirror2)[1]).decode()
            data = {
                "image": encoded_string,
                "blackAndWhite": True,
                "category": "vehicle_detection_images"
            }
            response = requests.post(url, headers=headers, json=data)
            print("Vehicle Detection Data Collection - Image Saved!")
        except:
            server_available = CheckServer()
            last_server_check = time.time()

def plugin(data):
    '''
    FOR WINDSHIELD DATA COLLECTION

    global vd_data_collection, x1, y1, x2, y2, cooldown, last_capture

    if vd_data_collection and last_capture + cooldown < time.time():
        try:
            data["frameFull"]
        except:
            return data
        
        fullframe = data["frameFull"]
        frame = fullframe.copy()[y1:y2, x1:x2]

        threading.Thread(target=SendImage, args=(frame,), daemon=True).start()
        last_capture = time.time()
    '''

    global vd_data_collection, cooldown, last_capture, mirror_coords, last_game_coords, game_coords, last_github_version_check, app_on_newest_version

    if vd_data_collection and last_capture + cooldown < time.time() and app_on_newest_version == True:
        game_coords = helpers.GetGameWindowPosition()
        if helpers.IsGameWindowForegroundWindow() == False:
            return data
        if game_coords == None:
            return data
        if game_coords != last_game_coords:
            mirror_coords = CalculateMirrorCoordinates(game_coords)
        last_game_coords = game_coords

        try:
            data["frameFull"]
        except:
            return data

        fullframe = data["frameFull"]
        left_mirror = fullframe.copy()[mirror_coords[0][1]:mirror_coords[0][3], mirror_coords[0][0]:mirror_coords[0][2]]
        right_mirror = fullframe.copy()[mirror_coords[1][1]:mirror_coords[1][3], mirror_coords[1][0]:mirror_coords[1][2]]

        if last_github_version_check + 1800 < time.time():
            github_version = str(requests.get("https://raw.githubusercontent.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt").text.strip())
            with open(f"{variables.PATH}/version.txt", "r") as f:
                current_version = str(f.read().strip())
            app_on_newest_version = github_version == current_version
            last_github_version_check = time.time()

        threading.Thread(target=SendMirrorImages, args=(left_mirror, right_mirror,), daemon=True).start()
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
            ttk.Label(vd_tab, text="Vehicle Detection will be a very important part of ETS2LA full self driving.", font=("Robot", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="In order to make this model, we need to collect some training data for AI models", font=("Robot", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="Currently we are collecting screenshots of mirrors.", font=("Robot", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="NOTE: Before turning this on, make sure you go in game and hit F2 until both mirrors show up", font=("Robot", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="You can see an example of what data is collected below:", font=("Robot", 10, "bold")).grid(row=6, column=0, columnspan=2, pady=2)

            example_image_paths = ["1.png", "2.png"]
            for i, image_path in enumerate(example_image_paths):
                image_path = os.path.join(variables.PATH, "assets", "DataCollection", image_path)
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = image.resize((160, 250), resample=Image.BILINEAR)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(vd_tab, image=photo)
                image_label.grid(row=7, column=0 if i == 0 else 1, padx=10, pady=10)
                image_label.image = photo
            
            ttk.Label(vd_tab, text="Disclaimer: Every 5 seconds, a screenshot will be taken at the mirror coordinates.", font=("Robot", 10, "bold")).grid(row=8, column=0, columnspan=2, pady=2)
            ttk.Label(vd_tab, text="This data is public and we are not responsible for any personal data leaks. Do not enable unless you are in game.", font=("Robot", 10, "bold")).grid(row=9, column=0, columnspan=2, pady=2)

            def CheckbuttonCallback():
                if vd_data_collection_var.get() == True:
                    OptInDialog()
        
            vd_data_collection_var = helpers.MakeCheckButton(vd_tab, "Enable Data Collection (Anonymous data will be sent to our server)", "DataCollection", "VD Data Collection", 10, 0, width=80, columnspan=2, callback=CheckbuttonCallback)
            helpers.MakeButton(vd_tab, "View Collected Data", lambda: webbrowser.open("https://filebrowser.tumppi066.fi/share/Uw850Xow"), 11, 0, width=150, sticky="nw", columnspan=2)
            
            tl_tab = ttk.Frame(notebook)
            tl_tab.columnconfigure(0, weight=1)
            tl_tab.columnconfigure(1, weight=1)
            tl_tab.columnconfigure(2, weight=1)

            ttk.Label(tl_tab, text="Traffic Light Detection Data Collection", font=("Robot", 18, "bold")).grid(row=0, column=0, columnspan=3)
            ttk.Label(tl_tab, text="", font=("Robot", 10, "bold")).grid(row=1, column=0, columnspan=3, pady=1)
            ttk.Label(tl_tab, text="Traffic Light Detection is undergoing some changes which will make it faster and better!", font=("Robot", 10, "bold")).grid(row=2, column=0, columnspan=3, pady=2)
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