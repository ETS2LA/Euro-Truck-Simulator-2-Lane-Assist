from plugins.LSTRLaneDetection.LSTRLaneDetection.lstr.lstr import LSTR
import os
from enum import Enum
import numpy as np
from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="LSTRLaneDetection", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="The recommended lane detection type.\nWill use the CPU to detect lanes on the image.\nMad props to the LSTR team\nfor making something this lightweight and fast!",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="LaneDetection" # Will disable the other screen capture plugins
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import cv2
import numpy as np


model = None
useGPU = True

# LSTR model types
class ModelType(Enum):
    LSTR_180X320 = "lstr_180x320"
    LSTR_240X320 = "lstr_240x320"
    LSTR_360X640 = "lstr_360x640"
    LSTR_480X640 = "lstr_480x640"
    LSTR_720X1280 = "lstr_720x1280"

def discover_models():
    # Find all models in the models folder
    models = []
    dir = variables.PATH + "/plugins/LSTRLaneDetection/models"
    for file in os.listdir(dir):
        if file.endswith(".onnx"):
            models.append(file)

    return models

def load_model(model_name):
    global useGPU
    try:
        global model
        # Discover model type
        model_type = None
        for type in ModelType:
            if type.value in model_name:
                model_type = type
                break
        
        # Load model
        dir = variables.PATH + "/plugins/LSTRLaneDetection"
        print("There might be two error messages following this note, ignore them if you are not trying to get GPU acceleration to work.")
        print("Use the following link to set it up https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements")
        model = LSTR(model_type, dir + "/models/" + model_name, use_gpu=useGPU)
        return True
    except Exception as e:
        print("Error loading model: " + str(e))
        useGPU = False
        return False
    
def detect_lanes(image, draw_points=False, draw_poly=False, color=(255,191,0)):
    global model
    global lanes_points
    global lane_ids
    if model is not None:
        # Detect lanes
        detected_lanes, lane_ids = model.detect_lanes(image)
        # output_img = model.draw_lanes(image, color=color, fillPoly=draw_poly)
        lanes_points = detected_lanes
        lane_ids = lane_ids
        
        # Calculate difference
        rightLane = np.where(lane_ids==0)[0]
        leftLane = np.where(lane_ids==5)[0]
        #print(lane_ids)
        #print(leftLane)
        #print(rightLane)
        try:
            # Get the left and right lane position
            leftx = lanes_points[leftLane[0]][0][0]
            rightx = lanes_points[rightLane[0]][0][0]
            # Calculate difference
            difference = (leftx + rightx) / 2
            
        except:
            difference = int(modelName.split("_")[1].split("x")[1].split(".")[0]) / 2 
            pass

        return lanes_points, lane_ids, difference
    
def onEnable():
    pass

def onDisable():
    pass

# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    global modelName
    try: # Try and find the frame
        frame = data["frame"]
        # If we do then run the lane detection
        if model == None:
            modelName = settings.GetSettings("LSTR", "Model")
            if modelName == None:
                modelName = discover_models()[0]
            print("Model successful: " + str(load_model(modelName)))
            
        if model is not None:
            points, ids, difference = detect_lanes(frame)
            
            data["LSTR"] = {}
            data["LSTR"]["points"] = points
            data["LSTR"]["ids"] = ids
            
            frame = data["frame"]
            # Add a point for the middle of the lane
            try:
                cv2.circle(frame, (int(difference), int(frame.shape[0]- 10)), 5, (0,0,255), -1, cv2.LINE_AA)
                data["frame"] = frame
            except Exception as ex:
                print(ex)
                pass
            
            w = int(modelName.split("_")[1].split("x")[1].split(".")[0])
            difference = difference - (w / 2)
            difference = difference / w - 0.5 # Scale it between -1 and 1
            data["LaneDetection"] = {}
            data["LaneDetection"]["difference"] = difference
            #print(difference)
            
        return data
            
    except Exception as ex:
        print(ex)
        return data


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
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            models = discover_models()
            # Make a dropdown menu for selecting the model
            self.model = tk.StringVar(self.root)
            
            self.model.set(models[0]) # default value
                
            self.modelMenu = ttk.OptionMenu(self.root, self.model, *models, command=lambda: settings.CreateSettings("LSTRLaneDetection", "Model", self.model.get()))
            self.modelMenu.config(width=20)
            self.modelMenu.grid(row=0, column=0, padx=10, pady=10)
            
            helpers.MakeButton(self.root, "Load model", lambda: load_model(self.model.get()), 0, 1)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)