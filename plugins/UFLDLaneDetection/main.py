"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""
from plugins.plugin import PluginInformation


PluginInfo = PluginInformation(
    name="UFLDLaneDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Most credit goes to jason-li-831202 for his\nVehicle-CV-ADAS repository.\nHe did most of the work, I just made it work in ETS2.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/jason-li-831202/Vehicle-CV-ADAS/tree/master",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="LaneDetection", # Will disable the other lane detection plugins
    noUI = True
)


from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import LaneModelType
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.ultrafastLaneDetectorV2 import UltrafastLaneDetectorV2
from src.logger import print

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os

import cv2
import numpy as np

# This will temporarily add the NVIDIA CUDA libraries to the system path

nvidiaPath = "src/NVIDIA"
nvidiaPath = os.path.join(variables.PATH, nvidiaPath)

os.environ["PATH"] = nvidiaPath

def ProcessFrame(data):
    image = data["frame"]
    
    input_tensor = laneDetector.prepare_input(image)

    # Perform inference on the image
    output = laneDetector.infer.inference(input_tensor)

    # Process output data
    try:
        laneDetector.lanes_points, laneDetector.lanes_detected = laneDetector.process_output(output, laneDetector.cfg, original_image_width =  laneDetector.img_width, original_image_height = laneDetector.img_height)
    except:
        import traceback
        traceback.print_exc()
        
    return laneDetector.lanes_points, laneDetector.lanes_detected

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
laneDetector = None
def plugin(data):
    global laneDetector
    
    if laneDetector == None:
        try:
            laneDetector = UltrafastLaneDetectorV2(model_path, model_type)
        except:
            from tkinter import messagebox
            messagebox.showerror("ULFD", "Could not load the model file. Most likely it's missing.\nUFLD will now disable itself.")
            settings.RemoveFromList("Plugins", "Enabled", "UFLDLaneDetection")
            variables.UpdatePlugins()
    
    try:
        lanePoints, lanesDetected = ProcessFrame(data)
        
        farLeftLane = lanePoints[0]
        leftLane = lanePoints[1]
        rightLane = lanePoints[2]
        farRightLane = lanePoints[3]
            
            
        
        data["LaneDetection"] = {}
        data["LaneDetection"]["farLeftLane"] = farLeftLane
        data["LaneDetection"]["leftLane"] = leftLane
        data["LaneDetection"]["rightLane"] = rightLane
        data["LaneDetection"]["farRightLane"] = farRightLane
        data["LaneDetection"]["lanesDetected"] = lanesDetected
        
        # Calculate difference between lanes
        leftLanePoints = leftLane[len(leftLane)-10:len(leftLane)]
        rightLanePoints = rightLane[len(rightLane)-10:len(rightLane)]
        leftLaneX = np.mean(leftLanePoints, axis=0)[0]
        rightLaneX = np.mean(rightLanePoints, axis=0)[0]
        
        frame = data["frame"]
        
        w = frame.shape[1]
        h = frame.shape[0]
        
        difference = (rightLaneX - leftLaneX) / 2
        difference = difference + leftLaneX
        
        cv2.circle(frame, (int(leftLaneX), int(h/8*7)), 4, (0,255,0), -1, cv2.LINE_AA)
        cv2.circle(frame, (int(rightLaneX), int(h/8*7)), 4, (0,255,0), -1, cv2.LINE_AA)
        cv2.circle(frame, (int(difference), int(h/8*7)), 4, (0,0,255), -1, cv2.LINE_AA)
        data["frame"] = frame
        
        difference = difference / w - 0.5 # Scale it between -1 and 1
        
        data["LaneDetection"]["difference"] = difference 
        
    except Exception as ex:
        print(ex)

    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    
    global model_path, model_type
    
    path = variables.PATH
    if os.name == "nt":
        model_path = os.path.join(path, r"plugins\UFLDLaneDetection\UFLD\models\tusimple_res34.onnx")
    else:
        model_path = os.path.join(path, r"plugins\UFLDLaneDetection\UFLD\models\tusimple_res34.onnx")
    print("Model path: " + model_path)
    model_type = LaneModelType.UFLDV2_TUSIMPLE
    pass

def onDisable():
    pass

# Plugins can also have UIs, this works the same as the panel example
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
            
            # Helpers provides easy to use functions for creating consistent widgets!
            helpers.MakeLabel(self.root, "This is a plugin!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # Use the mainUI.quit() function to quit the app
            helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 1,0, padx=30, pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
