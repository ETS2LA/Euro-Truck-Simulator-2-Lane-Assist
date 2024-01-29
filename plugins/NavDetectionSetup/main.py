from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="NavDetectionSetup", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Setup for the nav detection plugin. \nWill be ran when selected in first time setup",
    version="0.1",
    author="DylDev",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.translator import Translate
import os
import webview
from PIL import ImageTk, Image
import mouse
import cv2 
import pyautogui
try:
    import bettercam
except:
    print("Bettercam is not installed, Grab cordinates will not work")

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur

        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.introPage()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        global grabnavcords
        def grabnavcords():
            if variables.ENABLELOOP == True:
                variables.ENABLELOOP = False
                cv2.destroyAllWindows()

            camera = bettercam.create(device_idx=0,output_color="BGR")

            min_x = settings.GetSettings("bettercam", "x")
            min_y = settings.GetSettings("bettercam", "y")
            height = settings.GetSettings("bettercam", "height")
            width = settings.GetSettings("bettercam", "width")

            cv2.namedWindow("Lane Assist", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Lane Assist", cv2.WND_PROP_TOPMOST, 1)

            while True:
                left, top = min_x, min_y
                right, bottom = left + width, top + height
                frame = camera.grab(region=(left,top,right,bottom))
                
                if frame is None: 
                    continue

                mousex, mousey = mouse.get_position()
                circlex = mousex - min_x
                circley = mousey - min_y
                if circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
                    cv2.circle(frame, (circlex,circley), round(width/40), (40,130,210), 2)

                if mouse.is_pressed(button="left") == True and circlex > 5 and circlex < width-5 and circley > 5 and circley < height-5:
                    settings.CreateSettings("NavigationDetectionV2", "navsymbolx", circlex)    
                    settings.CreateSettings("NavigationDetectionV2", "navsymboly", circley)
                    cv2.destroyAllWindows()
                    variables.ToggleEnable()
                    variables.RELOAD = True
                    break
                cv2.imshow("Lane Assist", frame)
                cv2.waitKey(1)
           
        def openwiki(self):
            webview.create_window("Lane Assist Wiki", "https://wiki.tumppi066.fi/en/LaneAssist/DetectionTypes#navigation-detection-v2-glas42")
            webview.start()

        def introPage(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            helpers.MakeLabel(self.root, "Navigation Detection Setup", 0,0, font=("Roboto", 20, "bold"), padx=80, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "This will guide you through setting up navigation detection.", 1,0, font=("Segoe UI", 10), padx=80, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "You can also use the wiki to set it up.", 2,0, font=("Segoe UI", 10), padx=80, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "Make sure you are in ETS2 and you have lane assist enabled.", 3,0, font=("Segoe UI", 10), padx=80, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "You should also make sure that your preview is directly over the minimap.", 4,0, font=("Segoe UI", 10), padx=80, pady=0, columnspan=2)
            helpers.MakeButton(self.root, "Wiki", self.openwiki, 5,0)
            helpers.MakeButton(self.root, "Next", lambda: self.placecircle(), 5,1)
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def placecircle(self):
            self.root.destroy()
            del self.root
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            height = 220
            width = round(height * 1.7777) # 16:9
            self.circleimg = Image.open(os.path.join(variables.PATH, "plugins", "NavDetectionSetup", "images", "placecircle.png"))
            self.circleimg = self.circleimg.resize((width, height), resample=Image.LANCZOS)
            self.circleimg = ImageTk.PhotoImage(self.circleimg)

            helpers.MakeLabel(self.root, "Set Nav Symbol Position", 0,0, font=("Roboto", 20, "bold"), padx=50, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "You should now hit the Grab Cordinates button below.", 1,0, font=("Segoe UI", 10), padx=50, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "If you move your mouse over the map, you should see an orange circle in the preview.", 2,0, font=("Segoe UI", 10), padx=50, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "Move this circle directly over the symbol for your truck.", 3,0, font=("Segoe UI", 10), padx=50, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "Just left click on your mouse, and the app will restart with lane assist enabled.", 4,0, font=("Segoe UI", 10), padx=50, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "It should look something like this:", 5,0, font=("Segoe UI", 10), padx=50, pady=0, columnspan=2)

            ttk.Label(self.root, text="", image=self.circleimg).grid(row=6, column=0, padx=50, pady=10, columnspan=2)
            helpers.MakeButton(self.root, "Back", lambda: self.introPage(), 7, 0, pady=20)
            helpers.MakeButton(self.root, "Grab Coordinates", lambda: grabnavcords(), 7, 1, pady=20)
            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    except Exception as ex:
        print(ex.args)