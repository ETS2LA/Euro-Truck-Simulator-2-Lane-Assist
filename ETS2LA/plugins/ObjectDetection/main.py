from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
from ETS2LA.utils.logging import logging
from norfair import Tracker, Detection
import ETS2LA.variables as variables
from math import ceil
import numpy as np
import screeninfo
import pyautogui
import pathlib
import norfair
import torch
import json
import time
import cv2
import os

# Silence the goddamn torch warnings...
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

runner:PluginRunner = None
profile = "reallygoodfps"
if profile == "reallygoodfps":
    RUN_YOLO_EVERY_N_FRAME = 3
elif profile == "goodfps":
    RUN_YOLO_EVERY_N_FRAME = 6
elif profile == "badfps":
    RUN_YOLO_EVERY_N_FRAME = 10
YOLO_FPS = 2 # How many times per second the YOLO model should run
MODEL_TYPE = "yolov5" # Change this to "yolov7" or "yolov5"

if MODEL_TYPE == "yolov7":
    MODEL_NAME = "5-31-24_1_yolov7.pt"
elif MODEL_TYPE == "yolov5":
    MODEL_NAME = "best_v5s.pt"

LOADING_TEXT = "Vehicle Detection loading model..."
USE_EXTERNAL_VISUALIZATION = True

try:
    from ETS2LA.plugins.AR.main import Line, Circle, Box, Polygon, Text, ScreenLine
except:
    USE_EXTERNAL_VISUALIZATION = False # Force external off

class Vehicle:
    raycasts: list
    screenPoints: list
    vehicleType: str
    def __init__(self, raycasts, screenPoints, vehicleType):
        self.raycasts = raycasts
        self.screenPoints = screenPoints
        self.vehicleType = vehicleType
    
    def json(self):
        return {
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "screenPoints": self.screenPoints,
            "vehicleType": self.vehicleType
        }
    

def Initialize():
    global ShowImage
    global TruckSimAPI
    global ScreenCapture
    global Raycast
    global capture_y, capture_x, capture_width, capture_height, model, frame, temp

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    Raycast = runner.modules.Raycasting
    
    screen = screeninfo.get_monitors()[0]
    
    if screen.height >= 1440:
        if screen.width >= 5120:
            screen_cap = "1440p32:9"
        else:
            screen_cap = "1440p"
    else:
        screen_cap = "1080p"

    runner.sonner("Vehicle Detection using profile: " + screen_cap)

    if screen_cap == "1440p32:9":
        capture_x = 2100
        capture_y = 300
        capture_width = 1280
        capture_height = 720
    elif screen_cap == "1440p":
        capture_x = 700
        capture_y = 300
        capture_width = 1280
        capture_height = 720
    elif screen_cap == "1080p":
        capture_x = 600
        capture_y = 200
        capture_width = 1020
        capture_height = 480

    #capture_x = 0
    #capture_y = 0
    #capture_width = screen.width
    #capture_height = screen.height

    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    time.sleep(0.5) # Let the profile text show for a bit

    runner.sonner(LOADING_TEXT, "promise")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    MODEL_PATH = os.path.dirname(__file__) + f"/models/{MODEL_NAME}"
    
    if MODEL_TYPE == "yolov7":
        model = torch.hub.load('WongKinYiu/yolov7', 'custom', path=MODEL_PATH, _verbose=False)
    elif MODEL_TYPE == "yolov5":
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, _verbose=False)
    model.conf = 0.70
    model.to(device)

    runner.sonner(f"Vehicle Detection model loaded on {device.upper()}", "success", promise=LOADING_TEXT)

    cv2.namedWindow('Vehicle Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vehicle Detection', int(capture_width), int(capture_height))
    #cv2.setWindowProperty('Vehicle Detection', cv2.WND_PROP_TOPMOST, 1)

boxes = []
cur_yolo_fps = 0
frame = None
yolo_frame = None
updated_boxes = False
frame_count_since_last_detection = 0
def detection_thread():
    global boxes, cur_yolo_fps, updated_boxes
    while True:
        if type(yolo_frame) is None:
            time.sleep(1/YOLO_FPS)
            continue
        startTime = time.time()
        # Run YOLO model
        try: results = model(yolo_frame)
        except: time.sleep(1/YOLO_FPS); continue # Model is not ready
        boxes = results.pandas().xyxy[0]
        updated_boxes = True

        timeToSleep = 1/YOLO_FPS - (time.time() - startTime)
        if timeToSleep > 0:
            time.sleep(timeToSleep)
        cur_yolo_fps = round(1 / (time.time() - startTime), 1)
    
import threading
#threading.Thread(target=detection_thread, daemon=True).start()

tracker = Tracker(
    distance_function="iou",
    distance_threshold=1.15,
    initialization_delay=2
)

fps = 0
start_time = time.time()
frameCounter = 0
def plugin():
    global frame, yolo_frame, fps, start_time, model, capture_x, capture_y, boxes, capture_width, capture_height, updated_boxes, frameCounter
    
    ScreenCapture.monitor_x1 = capture_x
    ScreenCapture.monitor_y1 = capture_y
    ScreenCapture.monitor_x2 = capture_x + capture_width
    ScreenCapture.monitor_y2 = capture_y + capture_height
    
    data = {}
    data["api"] = TruckSimAPI.run()
    inputTime = time.time()
    data["frame"] = ScreenCapture.run(imgtype="cropped")
    inputTime = time.time() - inputTime

    frame = data["frame"]
    if frame is None: 
        return None
    
    yolo_frame = frame.copy()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    trackTime = time.time()
    if frameCounter > RUN_YOLO_EVERY_N_FRAME:
        results = model(yolo_frame)
        boxes = results.pandas().xyxy[0]
        norfair_detections = [Detection(np.array(
            [
                box['xmin'], box['ymin'], 
                box['xmax'], box['ymax']
            ]
        ), scores=np.array([
                box['confidence']
            ]
        ), label=box['name']) for _, box in boxes.iterrows()]
        tracked_objects = tracker.update(norfair_detections, period=RUN_YOLO_EVERY_N_FRAME)
    else:
        tracked_objects = tracker.update(period=RUN_YOLO_EVERY_N_FRAME)
     
    #print(tracked_objects)   
    for tracked_object in tracked_objects:
        box = tracked_object.get_estimate()
        x1, y1, x2, y2 = box[0]
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"{tracked_object.label} : {tracked_object.id}", (int(x1), int(y1-10)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
    # frame = norfair.draw_boxes(frame, tracked_objects)
    trackTime = time.time() - trackTime

    carPoints = []
    vehicles = []
    visualTime = time.time()
    if type(tracked_objects) != None:
        try:
            for object in tracked_objects:
                label = object.label
                x1, y1, x2, y2 = object.get_estimate()[0]
                # Add the offset to the x and y coordinates
                x1r = x1 + capture_x
                y1r = y1 + capture_y
                x2r = x2 + capture_x
                y2r = y2 + capture_y
                bottomLeftPoint = (int(x1r), int(y2r))
                bottomRightPoint = (int(x2r), int(y2r))
                if label in ['car', "van"]:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "car"))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                if label in ['truck']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "truck"))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                if label in ['bus']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "bus"))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
            for line in carPoints:
                raycasts = []
                screenPoints = []
                for point in line:
                    if type(point) == str: # Skip the vehicle type
                        continue
                    raycastStart = time.time()
                    raycast = Raycast.run(x=point[0], y=point[1])
                    raycasts.append(raycast)
                    screenPoints.append(point)
                vehicles.append(Vehicle(raycasts, screenPoints, line[2]))
        except:
            logging.exception("Error while drawing the vehicles")
    visualTime = time.time() - visualTime

    fps = round(1 / (time.time() - start_time))
    start_time = time.time()

    cv2.putText(frame, f"FPS: {fps}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)   
    cv2.putText(frame, f"YOLO FPS: {round(fps / RUN_YOLO_EVERY_N_FRAME, 2)} ({len(boxes)} objects) (every {RUN_YOLO_EVERY_N_FRAME}th frame)", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)      
    cv2.putText(frame, f"Tracking Time: {round(trackTime*1000, 2)}ms ({len(tracked_objects)} objects)", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Visual Time: {round(visualTime*1000, 2)}ms", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Input Time: {round(inputTime*1000, 2)}ms", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Vehicle Detection', frame)
    cv2.waitKey(1)
    
    if USE_EXTERNAL_VISUALIZATION:
        # Send data to the AR plugin
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = data["api"]["truckPlacement"]["coordinateY"]
        z = data["api"]["truckPlacement"]["coordinateZ"]

        arData = {
            "lines": [],
            "circles": [],
            "boxes": [],
            "polygons": [],
            "texts": [],
            "screenLines": [],
        }

        # Add the cars to the external visualization as a line from the start point to y + 1
        for vehicle in vehicles:
            if vehicle == None: continue
            try:
                leftPoint = vehicle.screenPoints[0]
                leftPoint = (leftPoint[0], leftPoint[1] + 5)
                rightPoint = vehicle.screenPoints[1]
                rightPoint = (rightPoint[0], rightPoint[1] + 5)
                middlePoint = ((leftPoint[0] + rightPoint[0]) / 2, (leftPoint[1] + rightPoint[1]) / 2)
                # Add the truck location to the points
                # leftPoint = (leftPoint[0] + x, leftPoint[1], leftPoint[2] + z)
                # rightPoint = (rightPoint[0] + x, rightPoint[1], rightPoint[2] + z)
                # middlePoint = (middlePoint[0] + x, middlePoint[1], middlePoint[2] + z)
                # Get the distance
                leftDistance = vehicle.raycasts[0].distance
                rightDistance = vehicle.raycasts[1].distance
                middleDistance = (leftDistance + rightDistance) / 2
                # Add the lines
                arData['screenLines'].append(ScreenLine((leftPoint[0], leftPoint[1]), (rightPoint[0], rightPoint[1]), color=[0, 255, 0, 100], thickness=2))
                # Add the text
                arData['texts'].append(Text(f"{round(middleDistance, 1)}m", (middlePoint[0], middlePoint[1]), color=[0, 255, 0, 255], size=15))
            except:
                continue
    
    frameCounter += 1
    return None, {
        "vehicles": vehicles,
        "ar": arData
    }