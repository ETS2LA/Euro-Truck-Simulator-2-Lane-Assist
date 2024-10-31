from ETS2LA.Plugin import *
from ETS2LA.UI import *

from ETS2LA.utils.translator import Translate
from ETS2LA.utils.values import SmoothedValue
import ETS2LA.backend.settings as settings
from ETS2LA.utils.logging import logging
import ETS2LA.variables as variables

from plugins.ObjectDetection.vehicleUtils import UpdateVehicleSpeed, GetVehicleSpeed
from plugins.ObjectDetection.classes import Vehicle, RoadMarker, Sign, TrafficLight

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "ObjectDetection"
    def render(self):
        Title("object_detection.settings.1.title")
        Description("object_detection.settings.1.description")
        Separator()
        Selector("object_detection.settings.2.name", "device", "Automatic", ["Automatic", "CPU", "GPU"], description="object_detection.settings.2.description", requires_restart=True)
        Selector("object_detection.settings.3.name", "mode", "Performance", ["Performance", "Quality"], description="object_detection.settings.3.description", requires_restart=True)
        Input("object_detection.settings.4.name", "yolo_fps", "number", 2, description="object_detection.settings.4.description", requires_restart=True)
        Selector("object_detection.settings.5.name", "model", "YoloV5", ["YoloV5", "YoloV7"], description="object_detection.settings.5.description", requires_restart=True)
        # TODO: Add array element back!
        return RenderUI()

class Plugin(ETS2LAPlugin):
    fps_cap = 30
    
    description = PluginDescription(
        name="plugins.objectdetection",
        version="1.0",
        description="plugins.objectdetection.description",
        modules=["TruckSimAPI", "ScreenCapture", "ShowImage", "Raycasting", "PositionEstimation"],
    )
    
    author = [Author(
        name="DylDev",
        url="https://github.com/DylDevs",
        icon="https://avatars.githubusercontent.com/u/110776467?v=4"
    ), Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )]
    
    settings_menu = SettingsMenu()
    
    def imports(self):
        try:
            # Import libraries
            from norfair import Detection, Tracker, OptimizedKalmanFilterFactory
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
                global win32gui
                import win32gui
            else:
                print("ObjectDwetection is not supported on non-windows systems. Disabled.")
                self.terminate()

            try:
                from plugins.AR.main import ScreenLine, Text # type: ignore (Ignore import errors)
            except ImportError:
                ScreenLine = Text = None

            # Silence torch warnings
            warnings.simplefilter(action='ignore', category=FutureWarning)

            self.Detection = Detection
            self.Tracker = Tracker
            self.OptimizedKalmanFilterFactory = OptimizedKalmanFilterFactory
            self.Literal = Literal
            self.tqdm = tqdm
            self.np = np
            self.screeninfo = screeninfo
            self.threading = threading
            self.warnings = warnings
            self.requests = requests
            self.pathlib = pathlib
            self.torch = torch
            self.time = time
            self.math = math
            self.cv2 = cv2
            self.os = os
            self.win32gui = win32gui
            self.ScreenLine = ScreenLine
            self.Text = Text
        except:
            import traceback
            traceback.print_exc()

    def init(self):
        try:
            monitor_index = settings.Get("Global", "display", 0)
            settings_yolo_fps = settings.Get("ObjectDetection", "yolo_fps", 2)
            self.MODE = settings.Get("ObjectDetection", "mode", "Performance")
            self.YOLO_FPS = settings_yolo_fps if settings_yolo_fps > 0 else 2
            self.USE_EXTERNAL_VISUALIZATION = True
            self.TRACK_SPEED = ["car", "van", "bus", "truck"]
            MODEL_TYPE = settings.Get("ObjectDetection", "model", "YoloV5")
            MODEL_NAME = "YOLOv7-tiny.pt" if MODEL_TYPE == "YoloV7" else "YOLOv5s.pt"
            MODELS_DIR = self.os.path.join(self.os.path.dirname(__file__), "models")
            MODEL_PATH = self.os.path.join(MODELS_DIR, MODEL_NAME)
            MODEL_REPO = "https://huggingface.co/DylDev/ETS2-Vehicle-Detection"
            MODEL_DOWNLOAD_LINK = f"{MODEL_REPO}/resolve/main/{MODEL_NAME}?download=true"
            
            
            MODEL_DOWNLOAD_HTNL = \
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

            CONNECTION_FAILED_HTML = \
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

            self.ShowImage = self.modules.ShowImage
            self.TruckSimAPI = self.modules.TruckSimAPI
            self.ScreenCapture = self.modules.ScreenCapture
            self.PositionEstimation = self.modules.PositionEstimation
            self.ScreenCapture.mode = "grab"
            self.Raycast = self.modules.Raycasting
            
            screen = self.screeninfo.get_monitors()[monitor_index]
            dimensions = settings.Get("ObjectDetection", "dimensions", None)
            
            def SetScreenCaptureDimensions():
                height_scale = screen.height / 1080
                width_scale = screen.width / 1920

                capture_x = round(600 * width_scale)
                capture_y = round(200 * height_scale)
                capture_width = 1020
                capture_height = round(480 * height_scale)

                self.notify(Translate("object_detection.screen_capture_profile", [f"{screen.width}x{screen.height}"]))
                settings.Set("ObjectDetection", "dimensions", [capture_x, capture_y, capture_width, capture_height])  
                self.time.sleep(0.5) # Let the profile text show for a bit

                return capture_x, capture_y, capture_width, capture_height
            
            # Set the capture dimensions based on the screen resolution
            if dimensions == None:
                dimensions = SetScreenCaptureDimensions()
            else:
                if len(dimensions) != 4:
                    dimensions = SetScreenCaptureDimensions()

            self.capture_x, self.capture_y, self.capture_width, self.capture_height = dimensions

            if not self.os.path.exists(MODELS_DIR):
                self.os.makedirs(MODELS_DIR)

            if not self.os.path.exists(MODEL_PATH):
                try:
                    self.requests.get(MODEL_REPO)
                except:
                    self.ask(CONNECTION_FAILED_HTML, ["Ok"])
                    self.terminate()
                    return False
                
                choice = self.ask(MODEL_DOWNLOAD_HTNL, [Translate("cancel"), Translate("download")])
                translated_downloading = Translate("downloading", [MODEL_NAME])
                if choice == Translate("download"):
                    self.state.text = translated_downloading
                    self.state_progress = 0

                    chunk_size = 1024
                    response = self.requests.get(MODEL_DOWNLOAD_LINK, stream=True)
                    total_size = int(response.headers.get('content-length', 0))
                    with open(MODEL_PATH, 'wb') as file, self.tqdm(desc=f"Downloading {MODEL_PATH}", total=total_size,
                            unit='B', unit_scale=True, unit_divisor=chunk_size) as progress_bar:
                        downloaded_size = 0
                        total_mb = total_size / (chunk_size ** 2) 
                        for data in response.iter_content(chunk_size=chunk_size):
                            size = file.write(data)
                            downloaded_size += size
                            progress_bar.update(size)
                            downloaded_mb = downloaded_size / (chunk_size ** 2)  # Convert to MB
                            self.state.text = f"{translated_downloading} ({round(downloaded_mb, 2)} / {round(total_mb, 2)} MB)"
                            self.state.progress = downloaded_size / total_size
                    self.state.reset()
                else:
                    self.terminate()
                    return False
                
            # Fix the torch temp path for Windows
            if self.os.name == 'nt':
                temp = self.pathlib.PosixPath
                self.pathlib.PosixPath = self.pathlib.WindowsPath

            # Display loading text
            loading_model = Translate("object_detection.loading_model")
            
            self.state.text = loading_model

            # Get device
            settings_device = settings.Get("ObjectDetection", "device", "Automatic")
            if settings_device == "Automatic":
                device = "cuda" if self.torch.cuda.is_available() else "cpu"
            else:
                if settings_device == "GPU":
                    torch_available = self.torch.cuda.is_available()
                    if torch_available:
                        device = "cuda"
                    else:
                        device = "cpu"
                else:
                    device = "cpu"

            # Set cache directory for torch
            self.torch.hub.set_dir(f"{variables.PATH}cache/ObjectDetection")

            # Load model
            if MODEL_TYPE == "YoloV7":
                self.model = self.torch.hub.load('WongKinYiu/yolov7', 'custom', path=MODEL_PATH, _verbose=False)
            elif MODEL_TYPE == "YoloV5":
                self.model = self.torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, _verbose=False)
                
            self.model.conf = 0.70  # NMS confidence threshold (x% confidence to keep)
            self.model.to(device)  # Move model to GPU if available

            # Display loaded text
            self.state.reset()

            # Create OpenCV window
            self.cv2.namedWindow('Object Detection', self.cv2.WINDOW_NORMAL)
            self.cv2.resizeWindow('Object Detection', int(screen.width / 3), int(screen.height / 3))
            self.cv2.setWindowProperty('Object Detection', self.cv2.WND_PROP_TOPMOST, 1)

            self.smoothedFPS = SmoothedValue("time", 1)
            self.smoothedYOLOFPS = SmoothedValue("time", 1)
            self.smoothedTrackTime = SmoothedValue("time", 1)
            self.smoothedVisualTime = SmoothedValue("time", 1)
            self.smoothedInputTime = SmoothedValue("time", 1)
            self.smoothedRaycastTime = SmoothedValue("time", 1)
            
            self.boxes = None
            self.start_time = self.time.time()
            self.cur_yolo_fps = 0
            self.frame_counter = 0
            self.fps_values = []
            self.fps = 0
            self.frame = None
            self.yolo_frame = None
            self.last_boxes = None

            if self.MODE == "Performance":
                self.threading.Thread(target=self.detection_thread, daemon=True).start()
                self.tracker = self.Tracker(
                    distance_function="euclidean",
                    distance_threshold=100,
                    hit_counter_max=1
                )
            elif self.MODE == "Quality":
                self.tracker = self.Tracker(
                    distance_function="euclidean",
                    distance_threshold=100,
                    hit_counter_max=self.YOLO_FPS,
                    filter_factory=self.OptimizedKalmanFilterFactory(R=10, Q=1),
                )
        except:
            import traceback
            traceback.print_exc()

    def detection_thread(self):
        while True:
            if self.yolo_frame is None:
                self.time.sleep(1 / self.YOLO_FPS)
                continue
            
            # Run YOLO model
            startTime = self.time.time()
            try:
                results = self.model(self.yolo_frame)
            except:
                self.time.sleep(1 / self.YOLO_FPS)
                continue  # Model is not ready

            self.boxes = results.pandas().xyxy[0]
            timeToSleep = 1 / self.YOLO_FPS - (self.time.time() - startTime)
            if timeToSleep > 0:
                self.time.sleep(timeToSleep)
            self.cur_yolo_fps = round(1 / (self.time.time() - startTime), 1)

    def create_trackers(self, boxes, frame):
        try:
            self.trackers = []
            for _, box in boxes.iterrows():
                x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
                tracker = self.cv2.legacy.TrackerMOSSE_create()
                tracker.init(frame, (x, y, w, h))
                self.trackers.append(tracker)
        except Exception as e:
            pass

    # Use openCV to track the boxes
    def track_cars(self, boxes, frame):
        if boxes is None:
            return None
        
        if self.last_boxes is None:
            self.last_boxes = boxes
            self.create_trackers(boxes, frame)
            
        if not self.last_boxes.equals(boxes):
            self.last_boxes = boxes
            self.create_trackers(boxes, frame)
            
        if self.trackers is None:
            return None
        
        updated_boxes = boxes.copy()
        count = 0
        for tracker, box in zip(self.trackers, boxes.iterrows()):
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

    def run(self):
        self.ScreenCapture.monitor_x1 = self.capture_x
        self.ScreenCapture.monitor_y1 = self.capture_y
        self.ScreenCapture.monitor_x2 = self.capture_x + self.capture_width
        self.ScreenCapture.monitor_y2 = self.capture_y + self.capture_height
        
        inputTime = self.time.time()
        data = {}
        data["api"] = self.TruckSimAPI.run()
        data["frame"] = self.ScreenCapture.run(imgtype="cropped")
        inputTime = self.time.time() - inputTime
        
        truckX = data["api"]["truckPlacement"]["coordinateX"]
        truckY = data["api"]["truckPlacement"]["coordinateY"]
        truckZ = data["api"]["truckPlacement"]["coordinateZ"]

        frame = data["frame"]
        if frame is None: 
            return None
        
        self.yolo_frame = frame.copy()
        frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        
        if self.MODE == "Quality" and self.frame_counter % self.YOLO_FPS == 0:
            results = self.model(self.yolo_frame)
            self.boxes = results.pandas().xyxy[0]
            self.frame_counter = 0
            self.cur_yolo_fps = self.fps / self.YOLO_FPS

        trackTime = self.time.time()
        
        if self.MODE == "Performance":
            tracked_boxes = self.track_cars(self.boxes, self.yolo_frame)
            
            if tracked_boxes is not None:
                norfair_detections = []
                try:
                    for _, box in tracked_boxes.iterrows():
                        label = box['name']
                        score = box['confidence']
                        x1, y1, x2, y2 = int(box['xmin']), int(box['ymin']), int(box['xmax']), int(box['ymax'])
                        detection = self.Detection(
                            points=self.np.array([x1, y1, x2, y2]),
                            scores=self.np.array([score]),
                            label=label
                        )
                        norfair_detections.append(detection)
                    
                    tracked_boxes = self.tracker.update(norfair_detections)
                except:
                    tracked_boxes = self.tracker.update()
            else:
                tracked_boxes = self.tracker.update()
                
        elif self.MODE == "Quality":
            if self.frame_counter == 0:  # We updated the boxes in the previous frame
                norfair_detections = []
                for _, box in self.boxes.iterrows():
                    label = box['name']
                    score = box['confidence']
                    x1, y1, x2, y2 = int(box['xmin']), int(box['ymin']), int(box['xmax']), int(box['ymax'])
                    detection = self.Detection(
                        points=self.np.array([x1, y1, x2, y2]),
                        scores=self.np.array([score]),
                        label=label
                    )
                    norfair_detections.append(detection)
                tracked_boxes = self.tracker.update(norfair_detections, period=self.YOLO_FPS)
            else:
                tracked_boxes = self.tracker.update()
        
        trackTime = self.time.time() - trackTime

        carPoints = []
        objectPoints = []
        trafficLightPoints = []
        vehicles = []
        objects = []
        trafficLights = []
        visualTime = self.time.time()
        
        try:
            for tracked_object in tracked_boxes:
                box = tracked_object.estimate
                x1, y1, x2, y2 = box[0]
                self.cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                self.cv2.putText(frame, f"{tracked_object.label} : {tracked_object.id} {': ' + str(round(GetVehicleSpeed(tracked_object.id)*3.6)) + 'kph' if tracked_object.label in self.TRACK_SPEED else ': static'}", (int(x1), int(y1-10)), self.cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, self.cv2.LINE_AA)
        except:
            pass
        
        visualTime = self.time.time() - visualTime
        raycastTime = self.time.time()
        
        if tracked_boxes is not None:
            try:
                for object in tracked_boxes:
                    label = object.label
                    x1, y1, x2, y2 = object.estimate[0]
                    width = x2 - x1
                    height = y2 - y1
                    x1r = x1 + self.capture_x
                    y1r = y1 + self.capture_y
                    x2r = x2 + self.capture_x
                    y2r = y2 + self.capture_y
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
                        raycast = self.Raycast.run(x=point[0], y=point[1])
                        raycasts.append(raycast)
                        screenPoints.append(point)
                    
                    firstRaycast = raycasts[0]
                    secondRaycast = raycasts[1]
                    middlePoint = ((firstRaycast.point[0] + secondRaycast.point[0]) / 2, (firstRaycast.point[1] + secondRaycast.point[1]) / 2, (firstRaycast.point[2] + secondRaycast.point[2]) / 2)
                    
                    speed = UpdateVehicleSpeed(id, middlePoint)
                    distance = self.math.sqrt((middlePoint[0] - truckX)**2 + (middlePoint[1] - truckY)**2 + (middlePoint[2] - truckZ)**2)
                    
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
                            raycast = self.Raycast.run(x=point[0], y=point[1])
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
                        track = self.PositionEstimation.run(id, (middlePoint[0], middlePoint[1], width, height))
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
            
        raycastTime = self.time.time() - raycastTime

        # Calculate FPS
        self.fps = round(1 / (self.time.time() - self.start_time))
        self.fps_values.append(self.fps)
        if self.fps_values.__len__() > 10:
            self.fps_values.pop(0)
        self.fps = round(sum(self.fps_values) / len(self.fps_values), 1)
        self.start_time = self.time.time()

        # Display FPS values
        self.cv2.putText(frame, f"FPS: {round(self.smoothedFPS(self.fps), 1)}", (20, 60), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)   
        self.cv2.putText(frame, f"YOLO FPS: {round(self.smoothedYOLOFPS(self.cur_yolo_fps), 1)}", (20, 100), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)      
        self.cv2.putText(frame, f"Objects: {len(vehicles)}", (20, 300), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)
        self.cv2.putText(frame, f"Track Time: {round(self.smoothedTrackTime(trackTime)*1000, 2)}ms", (20, 140), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)
        self.cv2.putText(frame, f"Visual Time: {round(self.smoothedVisualTime(visualTime)*1000, 2)}ms", (20, 180), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)
        self.cv2.putText(frame, f"Input Time: {round(self.smoothedInputTime(inputTime)*1000, 2)}ms", (20, 220), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)
        self.cv2.putText(frame, f"Raycast Time: {round(self.smoothedRaycastTime(raycastTime)*1000, 2)}ms", (20, 260), self.cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, self.cv2.LINE_AA)
        self.cv2.imshow('Object Detection', frame)
        self.cv2.waitKey(1)
        
        # Get the data for the AR plugin
        if self.USE_EXTERNAL_VISUALIZATION:
            arData = {
                #"lines": [],
                #"circles": [],
                #"boxes": [],
                #"polygons": [],
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

                    # Get the distance
                    leftDistance = vehicle.raycasts[0].distance
                    rightDistance = vehicle.raycasts[1].distance
                    middleDistance = (leftDistance + rightDistance) / 2

                    # Add the lines
                    arData['screenLines'].append(self.ScreenLine((leftPoint[0], leftPoint[1]), (rightPoint[0], rightPoint[1]), color=[0, 255, 0, 100], thickness=2))
                    
                    # Add the text
                    arData['texts'].append(self.Text(f"{round(middleDistance, 1)} m", (middlePoint[0], middlePoint[1]), color=[0, 255, 0, 100], size=15))
                    
                    try:
                        arData['texts'].append(self.Text(f"{int(round(vehicle.speed * 3.6, 0))} km/h", (middlePoint[0], middlePoint[1] + 20), color=[0, 255, 0, 100], size=15))
                    except: pass
                except:
                    continue
        
        self.frame_counter += 1
        
        # Return data to the main thread
        self.globals.tags.vehicles = [vehicle.json() for vehicle in vehicles]
        self.globals.tags.objects = [object.json() for object in objects]
        self.globals.tags.traffic_lights = [light.json() for light in trafficLights]
        self.globals.tags.ar = arData
        
        return None