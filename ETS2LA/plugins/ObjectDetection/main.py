# Import libraries
from norfair import Detection, Tracker, OptimizedKalmanFilterFactory
from vehicleUtils import UpdateVehicleSpeed, GetVehicleSpeed
from classes import Vehicle, RoadMarker, Sign, TrafficLight
from ETS2LA.utils.translator import Translate
from ETS2LA.plugins.runner import PluginRunner  
from ETS2LA.utils.values import SmoothedValue
import ETS2LA.backend.settings as settings
from ETS2LA.utils.logging import logging
import ETS2LA.variables as variables
from typing import Literal
from tqdm import tqdm
import numpy as np
import screeninfo
import threading
import warnings
import requests
import pathlib
import torch
import time
import math
import cv2
import os

# Conditional import for window management
if os.name == "nt":
    import win32gui
    from ETS2LA.plugins.AR.main import ScreenLine, Text
else:
    from Xlib import X, display
    import Xlib.error
    import Xlib.ext
    import Xlib.XK

try:
    from ETS2LA.plugins.AR.main import ScreenLine, Text
except ImportError:
    pass

# Silence torch warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

settings_yolo_fps = settings.Get("ObjectDetection", "yolo_fps", 2)

# Literals
runner: PluginRunner = None
MODE: Literal["Performance", "Quality"] = \
    settings.Get("ObjectDetection", "mode", "Performance")
YOLO_FPS: int = \
    settings_yolo_fps if settings_yolo_fps > 0 else 2
MODEL_TYPE: Literal["YoloV5", "YoloV7"] = \
    settings.Get("ObjectDetection", "model", "YoloV5")
MODEL_NAME: str = \
    "YOLOv7-tiny.pt" if MODEL_TYPE == "YoloV7" else "YOLOv5s.pt"
MODELS_DIR: str = \
    os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH: str = \
    os.path.join(MODELS_DIR, MODEL_NAME)
MODEL_REPO: str = \
    "https://huggingface.co/DylDev/ETS2-Vehicle-Detection"
MODEL_DOWNLOAD_LINK: str = \
    f"{MODEL_REPO}/resolve/main/{MODEL_NAME}?download=true"
USE_EXTERNAL_VISUALIZATION: bool = \
    True
TRACK_SPEED: list = \
    ["car", "van", "bus", "truck"]

model_download_html = \
    f"""
    <div>
        <h1 style="font-size: 1rem; line-height: 1.25rem;">Object Detection - Model Download</h1>
        <div style="margin-top: 18px; font-size: 1rem; line-height: 0.75rem;">
            <p style="color: rgb(82 82 91); margin-bottom: 12px;">{Translate("object_detection.not_found.1")}</p></p>
            <p style="color: rgb(82 82 91); margin-bottom: 12px;">- {MODEL_NAME}</p>
            <br />
            <p style="color: rgb(82 82 91); margin-bottom: 6px;">{Translate("object_detection.not_found.2")} </p><a style="text-decoration-line: underline;" href="{MODEL_REPO}">Hugging Face</a></p>
        </div>
    </div>
    """

connection_failed_html = \
    f"""
    <div>
        <h1 style="font-size: 1rem; line-height: 1.25rem;">Object Detection - Connection Failed</h1>
        <div style="margin-top: 18px; font-size: 1rem; line-height: 0.75rem;">
            <p style="color: rgb(82 82 91); margin-bottom: 12px;">{Translate("object_detection.connection_failed.1")}</p>
            <p style="color: rgb(82 82 91); margin-bottom: 12px;">{Translate("object_detection.connection_failed.2")}</p>
            <p style="color: rgb(82 82 91); margin-bottom: 12px;">{Translate("object_detection.connection_failed.3")}</p>
            <p style="color: rgb(82 82 91); margin-bottom: 6px;">{Translate("object_detection.connection_failed.4")}</p>
        </div>
    </div>
    """

def Initialize():
    global ShowImage
    global TruckSimAPI
    global ScreenCapture
    global Raycast
    global PositionEstimation
    global capture_x, capture_y, capture_width, capture_height
    global model, frame, temp

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    PositionEstimation = runner.modules.PositionEstimation
    ScreenCapture.mode = "grab"
    Raycast = runner.modules.Raycasting
    
    screen = screeninfo.get_monitors()[0]
    dimensions = settings.Get("ObjectDetection", "dimensions", None)
    
    def SetScreenCaptureDimensions():
        height_scale = screen.height / 1080
        width_scale = screen.width / 1920

        capture_x = round(600 * width_scale)
        capture_y = round(200 * height_scale)
        capture_width = 1020
        capture_height = round(480 * height_scale)

        runner.sonner(Translate("object_detection.screen_capture_profile", [f"{screen.width}x{screen.height}"]))
        settings.Set("ObjectDetection", "dimensions", [capture_x, capture_y, capture_width, capture_height])  
        time.sleep(0.5) # Let the profile text show for a bit

        return capture_x, capture_y, capture_width, capture_height
    
    # Set the capture dimensions based on the screen resolution
    if dimensions == None:
        dimensions = SetScreenCaptureDimensions()
    else:
        if len(dimensions) != 4:
            dimensions = SetScreenCaptureDimensions()

    capture_x, capture_y, capture_width, capture_height = dimensions   

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    if not os.path.exists(MODEL_PATH):
        try:
            requests.get(MODEL_REPO)
        except:
            runner.ask(connection_failed_html, ["Ok"])
            runner.terminate()
            return False
        choice = runner.ask(model_download_html, [Translate("cancel"), Translate("download")])
        translated_downloading = Translate("downloading", [MODEL_NAME])
        if choice == Translate("download"):
            runner.state = translated_downloading
            runner.state_progress = 0

            chunk_size = 1024
            response = requests.get(MODEL_DOWNLOAD_LINK, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            with open(MODEL_PATH, 'wb') as file, tqdm(desc=f"Downloading {MODEL_PATH}", total=total_size,
                    unit='B', unit_scale=True, unit_divisor=chunk_size) as progress_bar:
                downloaded_size = 0
                total_mb = total_size / (chunk_size ** 2) 
                for data in response.iter_content(chunk_size=chunk_size):
                    size = file.write(data)
                    downloaded_size += size
                    progress_bar.update(size)
                    downloaded_mb = downloaded_size / (chunk_size ** 2)  # Convert to MB
                    runner.state = f"{translated_downloading} ({round(downloaded_mb, 2)} / {round(total_mb, 2)} MB)"
                    runner.state_progress = downloaded_size / total_size
                    runner.UpdateState()
            
            runner.state = "running"
            runner.state_progress = -1
            runner.UpdateState()
        else:
            runner.terminate()
            return False
        
    # Fix the torch temp path for Windows
    if os.name == 'nt':
        temp = pathlib.PosixPath
        pathlib.PosixPath = pathlib.WindowsPath

    # Display loading text
    loading_model = Translate("object_detection.loading_model")
    runner.sonner(loading_model, "promise")

    # Get device
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

    # Set cache directory for torch
    torch.hub.set_dir(f"{variables.PATH}cache/ObjectDetection")

    # Load model
    if MODEL_TYPE == "YoloV7":
        model = torch.hub.load('WongKinYiu/yolov7', 'custom', path=MODEL_PATH, _verbose=False)
    elif MODEL_TYPE == "YoloV5":
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, _verbose=False)
    model.conf = 0.70  # NMS confidence threshold (x% confidence to keep)
    model.to(device)  # Move model to GPU if available

    # Display loaded text
    runner.sonner(Translate("object_detection.loaded_model", [device.upper()]), "success", promise=loading_model)

    # Create OpenCV window
    cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Object Detection', int(screen.width / 3), int(screen.height / 3))
    cv2.setWindowProperty('Object Detection', cv2.WND_PROP_TOPMOST, 1)

    if MODE == "Performance":
        threading.Thread(target=detection_thread, daemon=True).start()

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
        try:
            results = model(yolo_frame)
        except:
            time.sleep(1/YOLO_FPS)
            continue  # Model is not ready
        boxes = results.pandas().xyxy[0]
        timeToSleep = 1/YOLO_FPS - (time.time() - startTime)
        if timeToSleep > 0:
            time.sleep(timeToSleep)
        cur_yolo_fps = round(1 / (time.time() - startTime), 1)

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
    
    if boxes is None:
        return None
    
    if last_boxes is None:
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if not last_boxes.equals(boxes):
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if trackers is None:
        return None
    
    updated_boxes = boxes.copy()
    count = 0
    for tracker, box in zip(trackers, boxes.iterrows()):
        try:
            success, pos = tracker.update(frame)
            if not success:
                print(Translate("object_detection.tracking_failed", [box[0]['name'], box[0]['confidence']]))
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
    
    truckX = data["api"]["truckPlacement"]["coordinateX"]
    truckY = data["api"]["truckPlacement"]["coordinateY"]
    truckZ = data["api"]["truckPlacement"]["coordinateZ"]

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
        
        if tracked_boxes is not None:
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
        if frameCounter == 0:  # We updated the boxes in the previous frame
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
    objectPoints = []
    trafficLightPoints = []
    vehicles = []
    objects = []
    trafficLights = []
    visualTime = time.time()
    
    try:
        for tracked_object in tracked_boxes:
            box = tracked_object.estimate
            x1, y1, x2, y2 = box[0]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"{tracked_object.label} : {tracked_object.id} {': ' + str(round(GetVehicleSpeed(tracked_object.id)*3.6)) + 'kph' if tracked_object.label in TRACK_SPEED else ': static'}", (int(x1), int(y1-10)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    except:
        pass
    
    visualTime = time.time() - visualTime
    raycastTime = time.time()
    
    if tracked_boxes is not None:
        try:
            for object in tracked_boxes:
                label = object.label
                x1, y1, x2, y2 = object.estimate[0]
                width = x2 - x1
                height = y2 - y1
                x1r = x1 + capture_x
                y1r = y1 + capture_y
                x2r = x2 + capture_x
                y2r = y2 + capture_y
                bottomLeftPoint = (int(x1r), int(y2r))
                bottomRightPoint = (int(x2r), int(y2r))
                middlePoint = (int((x1r + x2r) / 2), int((y1r + y2r) / 2))
                
                if label in ['car', "van"]:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "car", object.id))
                elif label in ['truck']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "truck", object.id))
                elif label in ['bus']:
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "bus", object.id))
                elif label in ["road_marker"]:
                    objectPoints.append((bottomLeftPoint, bottomRightPoint, label, object.id))
                elif label in ["red_traffic_light", "green_traffic_light", "yellow_traffic_light"]:
                    trafficLightPoints.append((middlePoint, label, object.id))
                else:
                    objectPoints.append((bottomLeftPoint, bottomRightPoint, label, object.id, middlePoint, x1, y1, width, height))
            
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
                
                speed = UpdateVehicleSpeed(id, middlePoint)
                distance = math.sqrt((middlePoint[0] - truckX)**2 + (middlePoint[1] - truckY)**2 + (middlePoint[2] - truckZ)**2)
                
                vehicles.append(Vehicle(
                    id,
                    line[2],
                    screenPoints, 
                    raycasts, 
                    speed=speed,
                    distance=distance
                ))
                
            for line in objectPoints:
                if len(line) == 4:
                    id = line[3]
                    line = line[:3]
                    label = line[2]
                    raycasts = []
                    screenPoints = []
                    for point in line:
                        if type(point) == str:
                            continue
                        raycast = Raycast.run(x=point[0], y=point[1])
                        raycasts.append(raycast)
                        screenPoints.append(point)
                        
                    firstRaycast = raycasts[0]
                    secondRaycast = raycasts[1]
                    middlePoint = ((firstRaycast.point[0] + secondRaycast.point[0]) / 2, (firstRaycast.point[1] + secondRaycast.point[1]) / 2, (firstRaycast.point[2] + secondRaycast.point[2]) / 2)
                    
                    if label == "road_marker":
                        objects.append(RoadMarker(
                            id,
                            label,
                            screenPoints,
                            middlePoint
                        ))
                else:
                    id = line[3]
                    label = line[2]
                    middlePoint = line[4]
                    x1 = line[5]
                    y1 = line[6]
                    width = line[7]
                    height = line[8]
                    track = PositionEstimation.run(id, (middlePoint[0], middlePoint[1], width, height))
                    if track != None and track.position != None:
                        position = track.position.tuple()
                    else:
                        position = (0, 0, 0)
                        
                    if "sign" in label:
                        objects.append(Sign(
                            id,
                            "sign",
                            middlePoint,
                            label.replace("_sign", ""),
                            position
                        ))
                        
            for point, label, id in trafficLightPoints:
                state = label.replace("_traffic_light", "")
                label = "traffic_light"
                trafficLights.append(TrafficLight(
                    id,
                    label,
                    [point],
                    state
                ))
                        
        except:
            logging.exception("Error while processing vehicle data")
            pass
        
    raycastTime = time.time() - raycastTime

    # Calculate FPS
    fps = round(1 / (time.time() - start_time))
    fpsValues.append(fps)
    if fpsValues.__len__() > 10:
        fpsValues.pop(0)
    fps = round(sum(fpsValues) / len(fpsValues), 1)
    start_time = time.time()

    # Display FPS values
    cv2.putText(frame, f"FPS: {round(smoothedFPS(fps), 1)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)   
    cv2.putText(frame, f"YOLO FPS: {round(smoothedYOLOFPS(cur_yolo_fps), 1)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)      
    cv2.putText(frame, f"Objects: {len(vehicles)}", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
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
    
    # Get the data for the AR plugin
    if USE_EXTERNAL_VISUALIZATION:
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
    
    frameCounter += 1
    # Return data to the main thread
    return None, {
        "vehicles": [vehicle.json() for vehicle in vehicles],
        "objects": [object.json() for object in objects],
        "traffic_lights": [light.json() for light in trafficLights],
        "ar": arData
    }