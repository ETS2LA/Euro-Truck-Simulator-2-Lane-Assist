from norfair import Detection, Tracker, OptimizedKalmanFilterFactory
from vehicleUtils import UpdateVehicleSpeed, GetVehicleSpeed
from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
from ETS2LA.utils.values import SmoothedValue
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
from ETS2LA.utils.logging import logging
import ETS2LA.variables as variables
from typing import Literal
from classes import Vehicle
import numpy as np
import screeninfo
import pyautogui
import pathlib
import torch
import json
import time
import cv2
import os

try:
    from ETS2LA.plugins.AR.main import ScreenLine, Text
except:
    pass

# Silence the goddamn torch warnings...
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

runner:PluginRunner = None
MODE: Literal["Performance", "Quality"] = \
    settings.Get("ObjectDetection", "mode", "Performance")
YOLO_FPS: int = \
    settings.Get("ObjectDetection", "yolo_fps", 2)
MODEL_TYPE: Literal["YoloV5", "YoloV7"] = \
    settings.Get("ObjectDetection", "model", "YoloV5")
MODEL_NAME: str = \
    "5-31-24_1_yolov7.pt" if MODEL_TYPE == "YoloV7" else "best_v5s.pt"
LOADING_TEXT: str = \
    "Loading Object Detection Model..."
USE_EXTERNAL_VISUALIZATION: bool = \
    True
TRACK_SPEED: list = \
    ["car", "van", "bus", "truck"]


def Initialize():
    global ShowImage
    global TruckSimAPI
    global ScreenCapture
    global Raycast
    global capture_y, capture_x, capture_width, capture_height
    global model, frame, temp

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    ScreenCapture.mode = "grab"
    Raycast = runner.modules.Raycasting
    
    screen = screeninfo.get_monitors()[0]
    
    dimensions = settings.Get("ObjectDetection", "dimensions", None)
    
    if dimensions == None:
        if screen.height >= 1440:
            if screen.width >= 5120:
                screen_cap = "1440p32:9"
            else:
                screen_cap = "1440p"
        else:
            if screen.height == 1200:
                screen_cap = "1080p16:10"
            else:
                screen_cap = "1080p"

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
        elif screen_cap == "1080p16:10":
            capture_x = 600
            capture_y = 280
            capture_width = 1020
            capture_height = 480
            
        runner.sonner("Object Detection is using screen capture profile: " + screen_cap)
        settings.Set("ObjectDetection", "dimensions", [capture_x, capture_y, capture_width, capture_height])  
    else:
        capture_x, capture_y, capture_width, capture_height = dimensions    
        
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    time.sleep(0.5) # Let the profile text show for a bit

    runner.sonner(LOADING_TEXT, "promise")

    settings_device = settings.Get("ObjectDetection", "device", "Automatic")
    if settings_device == "Automatic":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        if settings_device == "GPU":
            torch_available = torch.cuda.is_available()
            if torch_available:
                device = "cuda"
            else:
                device = "cpu"
        else:
            device = "cpu"

    MODEL_PATH = os.path.dirname(__file__) + f"/models/{MODEL_NAME}"
    
    if MODEL_TYPE == "YoloV7":
        model = torch.hub.load('WongKinYiu/yolov7', 'custom', path=MODEL_PATH, _verbose=False)
    elif MODEL_TYPE == "YoloV5":
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, _verbose=False)
    model.conf = 0.70
    model.to(device)

    runner.sonner(f"Object Detection model loaded on {device.upper()}", "success", promise=LOADING_TEXT)

    cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Object Detection', int(capture_width), int(capture_height))
    cv2.setWindowProperty('Object Detection', cv2.WND_PROP_TOPMOST, 1)

frame = None
boxes = None
yolo_frame = None
cur_yolo_fps = 0
def detection_thread():
    global boxes, cur_yolo_fps
    while True:
        if type(yolo_frame) is None:
            time.sleep(1/YOLO_FPS)
            continue
        startTime = time.time()
        # Run YOLO model
        try: results = model(yolo_frame)
        except: time.sleep(1/YOLO_FPS); continue # Model is not ready
        boxes = results.pandas().xyxy[0]
        #print(boxes)
        timeToSleep = 1/YOLO_FPS - (time.time() - startTime)
        if timeToSleep > 0:
            time.sleep(timeToSleep)
        cur_yolo_fps = round(1 / (time.time() - startTime), 1)
    
import threading
if MODE == "Performance":
    threading.Thread(target=detection_thread, daemon=True).start()

trackers = []
def create_trackers(boxes, frame):
    global trackers
    try:
        trackers = []
        for _, box in boxes.iterrows():
            x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
            tracker = cv2.legacy.TrackerMOSSE_create()
            tracker.init(frame, (x, y, w, h))
            trackers.append(tracker)
    except Exception as e:
        pass

# Use openCV to track the boxes
last_boxes = None
def track_cars(boxes, frame):
    global last_boxes, trackers
    
    if type(boxes) is type(None):
        return None
    
    if type(last_boxes) is type(None):
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if not last_boxes.equals(boxes):
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if type(trackers) is None:
        return None
    
    # Update the trackers and return the yolo data with updated boxes
    updated_boxes = boxes.copy()
    count = 0
    for tracker, box in zip(trackers, boxes.iterrows()):
        try:
            success, pos = tracker.update(frame)
            if not success:
                print(f"Tracking failed for {box[0]['name']} with confidence {box[0]['confidence']}")
                continue
            x, y, w, h = int(pos[0]), int(pos[1]), int(pos[2]), int(pos[3])
            updated_boxes.loc[box[0], 'xmin'] = x
            updated_boxes.loc[box[0], 'ymin'] = y
            updated_boxes.loc[box[0], 'xmax'] = x + w
            updated_boxes.loc[box[0], 'ymax'] = y + h
            count += 1
        except:
            pass

    return updated_boxes

if MODE == "Performance":
    tracker = Tracker(
        distance_function="euclidean",
        distance_threshold=100,
        hit_counter_max=1
    )
elif MODE == "Quality":
        tracker = Tracker(
        distance_function="euclidean",
        distance_threshold=100,
        hit_counter_max=YOLO_FPS,
        filter_factory=OptimizedKalmanFilterFactory(R=10, Q=1),
    )
    
smoothedFPS = SmoothedValue("time", 1)
smoothedYOLOFPS = SmoothedValue("time", 1)
smoothedTrackTime = SmoothedValue("time", 1)
smoothedVisualTime = SmoothedValue("time", 1)
smoothedInputTime = SmoothedValue("time", 1)
smoothedRaycastTime = SmoothedValue("time", 1)
    
fps = 0
start_time = time.time()
fpsValues = []
frameCounter = 0
def plugin():
    global frame, yolo_frame, fps, cur_yolo_fps, start_time, model, capture_x, capture_y, capture_width, capture_height, boxes, frameCounter
    
    ScreenCapture.monitor_x1 = capture_x
    ScreenCapture.monitor_y1 = capture_y
    ScreenCapture.monitor_x2 = capture_x + capture_width
    ScreenCapture.monitor_y2 = capture_y + capture_height
    
    inputTime = time.time()
    data = {}
    data["api"] = TruckSimAPI.run()
    data["frame"] = ScreenCapture.run(imgtype="cropped")
    inputTime = time.time() - inputTime

    frame = data["frame"]
    if frame is None: 
        return None
    
    yolo_frame = frame.copy()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    if MODE == "Quality" and frameCounter % YOLO_FPS == 0:
        results = model(yolo_frame)
        boxes = results.pandas().xyxy[0]
        frameCounter = 0
        cur_yolo_fps = fps / YOLO_FPS

    trackTime = time.time()
    
    if MODE == "Performance":
        tracked_boxes = track_cars(boxes, yolo_frame)
        
        if type(tracked_boxes) != None:
            norfair_detections = []
            try:
                for _, box in tracked_boxes.iterrows():
                    label = box['name']
                    score = box['confidence']
                    x1, y1, x2, y2 = int(box['xmin']), int(box['ymin']), int(box['xmax']), int(box['ymax'])
                    detection = Detection(
                        points=np.array([x1, y1, x2, y2]),
                        scores=np.array([score]),
                        label=label
                    )
                    norfair_detections.append(detection)
                
                tracked_boxes = tracker.update(norfair_detections)
            except:
                tracked_boxes = tracker.update()
        else:
            tracked_boxes = tracker.update()
            
    elif MODE == "Quality":
        if frameCounter == 0: # We updated the boxes in the previous frame
            norfair_detections = []
            for _, box in boxes.iterrows():
                label = box['name']
                score = box['confidence']
                x1, y1, x2, y2 = int(box['xmin']), int(box['ymin']), int(box['xmax']), int(box['ymax'])
                detection = Detection(
                    points=np.array([x1, y1, x2, y2]),
                    scores=np.array([score]),
                    label=label
                )
                norfair_detections.append(detection)
            tracked_boxes = tracker.update(norfair_detections, period=YOLO_FPS)
        else:
            tracked_boxes = tracker.update()
    
    trackTime = time.time() - trackTime

    carPoints = []
    vehicles = []
    visualTime = time.time()
    
    try:
        for tracked_object in tracked_boxes:
            box = tracked_object.estimate
            x1, y1, x2, y2 = box[0]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"{tracked_object.label} : {tracked_object.id} : {str(round(GetVehicleSpeed(tracked_object.id)*3.6)) + 'kph' if tracked_object.label in TRACK_SPEED else 'static'}", (int(x1), int(y1-10)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    except:
        pass
    
    visualTime = time.time() - visualTime
    raycastTime = time.time()
    
    if type(tracked_boxes) != None:
        try:
            for object in tracked_boxes:
                label = object.label
                x1, y1, x2, y2 = object.estimate[0]
                # Add the offset to the x and y coordinates
                x1r = x1 + capture_x
                y1r = y1 + capture_y
                x2r = x2 + capture_x
                y2r = y2 + capture_y
                bottomLeftPoint = (int(x1r), int(y2r))
                bottomRightPoint = (int(x2r), int(y2r))
                
                if label in ['car', "van"]:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "car", object.id))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                if label in ['truck']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "truck", object.id))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                if label in ['bus']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "bus", object.id))
                    #cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
            
            for line in carPoints:
                id = line[3]
                line = line[:3]
                raycasts = []
                screenPoints = []
                for point in line:
                    if type(point) == str: # Skip the vehicle type
                        continue
                    raycast = Raycast.run(x=point[0], y=point[1])
                    raycasts.append(raycast)
                    screenPoints.append(point)
                
                firstRaycast = raycasts[0]
                secondRaycast = raycasts[1]
                middlePoint = ((firstRaycast.point[0] + secondRaycast.point[0]) / 2, (firstRaycast.point[1] + secondRaycast.point[1]) / 2, (firstRaycast.point[2] + secondRaycast.point[2]) / 2)
                
                vehicles.append(Vehicle(
                    id,
                    line[2],
                    screenPoints, 
                    raycasts, 
                    speed=UpdateVehicleSpeed(id, middlePoint)
                ))
        except:
            logging.exception("Error while processing vehicle data")
            pass
        
    raycastTime = time.time() - raycastTime

    fps = round(1 / (time.time() - start_time))
    fpsValues.append(fps)
    if fpsValues.__len__() > 10:
        fpsValues.pop(0)
    fps = round(sum(fpsValues) / len(fpsValues), 1)
    start_time = time.time()

    cv2.putText(frame, f"FPS: {round(smoothedFPS(fps), 1)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)   
    cv2.putText(frame, f"YOLO FPS: {round(smoothedYOLOFPS(cur_yolo_fps), 1)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)      
    cv2.putText(frame, f"Track Time: {round(smoothedTrackTime(trackTime)*1000, 2)}ms", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Visual Time: {round(smoothedVisualTime(visualTime)*1000, 2)}ms", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Input Time: {round(smoothedInputTime(inputTime)*1000, 2)}ms", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Raycast Time: {round(smoothedRaycastTime(raycastTime)*1000, 2)}ms", (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Object Detection', frame)
    cv2.waitKey(1)
    
    arData = {
        #"lines": [],
        #"circles": [],
        #"boxes": [],
        #"polygons": [],
        "texts": [],
        "screenLines": [],
    }
    
    if USE_EXTERNAL_VISUALIZATION:
        # Send data to the AR plugin
        x = data["api"]["truckPlacement"]["coordinateX"]
        y = data["api"]["truckPlacement"]["coordinateY"]
        z = data["api"]["truckPlacement"]["coordinateZ"]


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
                arData['texts'].append(Text(f"{round(middleDistance, 1)} m", (middlePoint[0], middlePoint[1]), color=[0, 255, 0, 100], size=15))
                try:
                    arData['texts'].append(Text(f"{int(round(vehicle.speed * 3.6, 0))} km/h", (middlePoint[0], middlePoint[1] + 20), color=[0, 255, 0, 100], size=15))
                except: pass
            except:
                continue
    
    vehicles = [vehicle.json() for vehicle in vehicles]
    
    frameCounter += 1

    return None, {
        "vehicles": vehicles,
        "ar": arData
    }