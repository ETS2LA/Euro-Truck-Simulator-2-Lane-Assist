from lanedetection.lstr.LSTRLaneDetection.lstr.lstr import LSTR
import os
from enum import Enum
import numpy as np

model = None

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
    dir = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(dir, "models")):
        if file.endswith(".onnx"):
            models.append(file)

    return models

def load_model(model_name, use_gpu=False):
    try:
        global model
        # Discover model type
        model_type = None
        for type in ModelType:
            if type.value in model_name:
                model_type = type
                break
        
        # Load model
        dir = os.path.dirname(__file__)
        model = LSTR(model_type, dir + "/models/" + model_name, use_gpu=use_gpu)
        return True
    except Exception as e:
        print("Error loading model: " + str(e))
        return False
    
def detect_lanes(image, steering_offset, draw_points=True, draw_poly=True, color=(255,191,0)):
    global model
    global lanes_points
    global lane_ids
    if model is not None:
        # Detect lanes
        detected_lanes, lane_ids = model.detect_lanes(image)
        output_img = model.draw_lanes(image, color=color, fillPoly=draw_poly)
        lanes_points = detected_lanes
        lane_ids = lane_ids
        
        # Calculate difference
        rightLane = np.where(lane_ids==0)[0]
        leftLane = np.where(lane_ids==5)[0]
        #print(laneDetection.lane_ids)
        #print(leftLane)
        #print(rightLane)
        try:
            # Get the left and right lane position
            leftx = lanes_points[leftLane[0]][0][0]
            rightx = lanes_points[rightLane[0]][0][0]
            # Calculate difference
            difference = (leftx + rightx) / 2
            w = output_img.shape[1]
            difference = difference - (w / 2)
            difference = difference + steering_offset
        except:
            difference = 0
            pass

        return output_img, difference