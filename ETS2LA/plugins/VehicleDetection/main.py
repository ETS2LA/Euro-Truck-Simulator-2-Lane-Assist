from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import pyautogui
import bettercam
import torch
import numpy as np
import time
import cv2

runner:PluginRunner = None

def SendCrashReport(): # REMOVE THIS LATER
    return

def Initialize():
    print("initializing")
    global ShowImage
    global TruckSimAPI
    global ScreenCapture
    global Raycast

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    Raycast = runner.modules.Raycasting


model = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # 'yolov5n', 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x'

screen_width, screen_height = pyautogui.size()

cv2.namedWindow('YOLOv5 Detection', cv2.WINDOW_NORMAL)
cv2.resizeWindow('YOLOv5 Detection', 960, 540)
cv2.setWindowProperty('YOLOv5 Detection', cv2.WND_PROP_TOPMOST, 1)


def plugin():
    data = {}
    data["api"] = TruckSimAPI.run()
    data["frame"] = ScreenCapture.run(imgtype="full")

    frame = data["frame"]
    if frame is None: 
        return None
    
    start_time = time.time()
    if frame is None: return None
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  

    results = model(rgb_frame)

    boxes = results.pandas().xyxy[0]
    
    carPoints = []

    for _, box in boxes.iterrows():
        label = box['name']
        score = box['confidence']
        x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
        
        if label in ['car', 'truck', 'bus']:
            bottomMiddlePoint = (x + w // 2, y + h)
            carPoints.append(bottomMiddlePoint)
            cv2.circle(rgb_frame, bottomMiddlePoint, 5, (0, 255, 0), -1)

    fps = round(1 / (time.time() - start_time), 1)
    cv2.putText(rgb_frame, f"FPS: {fps}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)         
    cv2.imshow('YOLOv5 Detection', rgb_frame)
    cv2.resizeWindow('YOLOv5 Detection', int(854/1.33), int(480/1.33))
    
    cv2.waitKey(1)
    
    carCoordinates = []
    for point in carPoints:
        coordinates, distance = Raycast.run(x=point[0], y=point[1])
        carCoordinates.append(coordinates)
    
    # print(carCoordinates)
    
    return None, {
        "vehicles": carCoordinates,
    }