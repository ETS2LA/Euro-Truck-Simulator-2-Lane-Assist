from UltraFastLaneDetection import ultrafastLaneDetector
from LSTRLaneDetection.lstr import LSTR
import settingsInterface as settings
from enum import Enum

useLSTR = settings.GetSettings("modelSettings","useLSTR")
model = None
lanes_points = []

# Model types for LSTR
# Copied straight from ibaiGorordo's LSTR repo (ONNX-LSTR-Lane-Detection) -> LSTRLaneDetection
class ModelType(Enum):
    LSTR_180X320 = "lstr_180x320"
    LSTR_240X320 = "lstr_240x320"
    LSTR_360X640 = "lstr_360x640"
    LSTR_480X640 = "lstr_480x640"
    LSTR_720X1280 = "lstr_720x1280"


def initialize_model(model_path, model_type, model_depth,use_gpu=True):
    global model
    print("Initializing model...")
    if useLSTR: 
        for type in ModelType:
            if type.value == model_type:
                model_type = type
                break
        model = LSTR(model_type, model_path)
    else: 
        model = ultrafastLaneDetector.UltrafastLaneDetector(model_path, model_type, use_gpu, model_depth)
    
    print("Model initialized!")

def detect_lanes(image, draw_points=True, draw_poly=True, color=(255,191,0)):
    global lanes_points
    if useLSTR:
        detected_lanes, lane_ids = model.detect_lanes(image)
        output_img = model.draw_lanes(image, color=color, fillPoly=draw_poly)
        lanes_points = detected_lanes
        return output_img
    else:
        outputImg = model.detect_lanes(image, draw_points, draw_poly, color)
        lanes_points = model.lanes_points
        return outputImg
