# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from ETS2LA.Controls import ControlEvent

# ETS2LA imports
from Plugins.ObjectDetection.classes import Vehicle
from ETS2LA.Networking.cloud import SendCrashReport
import ETS2LA.Handlers.controls as controls
import ETS2LA.Utils.settings as settings
from ETS2LA.Utils.Console.logging import logging
from ETS2LA.Utils.Values.numbers import SmoothedValue
import ETS2LA.variables as variables
from Plugins.AR.classes import *

# Python imports
from Plugins.AdaptiveCruiseControl.speed import get_maximum_speed_for_points
from typing import cast
import math
import time

FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3) # seconds
OVERSPEED = settings.Get("AdaptiveCruiseControl", "overspeed", 0) # 0-100
BRAKING_DISTANCE = settings.Get("AdaptiveCruiseControl", "braking_distance", 60) # meters
STOPPING_DISTANCE = settings.Get("AdaptiveCruiseControl", "stopping_distance", 15) # meters
OVERWRITE_SPEED = settings.Get("AdaptiveCruiseControl", "overwrite_speed", 30) # km/h
TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = settings.Get("AdaptiveCruiseControl", "traffic_light_distance_multiplier", 1.5) # times
ACC_ENABLED = False
TYPE = settings.Get("AdaptiveCruiseControl", "type", "Percentage")
SHOW_NOTIFICATIONS = settings.Get("AdaptiveCruiseControl", "show_notifications", False)

def LoadSettings(data: dict):
    global FOLLOW_TIME, OVERSPEED, BRAKING_DISTANCE, STOPPING_DISTANCE, OVERWRITE_SPEED, TRAFFIC_LIGHT_DISTANCE_MULTIPLIER, TYPE, SHOW_NOTIFICATIONS
    FOLLOW_TIME = data.get("time", 3)
    OVERSPEED = data.get("overspeed", 0)
    BRAKING_DISTANCE = data.get("braking_distance", 60)
    STOPPING_DISTANCE = data.get("stopping_distance", 15)
    OVERWRITE_SPEED = data.get("overwrite_speed", 30)
    TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = data.get("traffic_light_distance_multiplier", 1.5)
    TYPE = data.get("type", "Percentage")
    SHOW_NOTIFICATIONS = data.get("show_notifications", False)

enable_disable = ControlEvent(
    "toggle_acc",
    "Toggle Adaptive Cruise Control",
    "button",
    description="When ACC is running this will toggle it on/off.",
    default="n"
)

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "AdaptiveCruiseControl"
    def render(self):
        Title("acc.settings.1.title")
        Description("acc.settings.1.description")
        Separator()
        with TabView():
            with Tab("Adaptive Cruise Control"):
                Slider("acc.settings.2.name", "time", 1, 0, 4, 0.5, suffix="s", description="acc.settings.2.description")
                Slider("acc.settings.4.name", "stopping_distance", 15, 0, 100, 2.5, suffix="m", description="acc.settings.4.description")
                Switch("acc.settings.6.name", "show_notifications", False, description="acc.settings.6.description")
            with Tab("Speed Control"):
                Slider("Coefficient of friction", "MU", 0.5, 0.1, 1, 0.1, description="Controls the (imaginary) friction between the tires and the road. Lower values will make the truck slow down more, while higher values will make it go faster in turns.")
                Slider("acc.settings.7.name", "overwrite_speed", 50, 0, 130, 5, suffix="km/h", description="acc.settings.7.description")
                with EnabledLock():
                    Selector("acc.settings.5.name", "type", "Percentage", ["Percentage", "Absolute"], description="acc.settings.5.description")
                    if self.settings.type is not None and self.settings.type == "Percentage":
                        Slider("acc.settings.3.name", "overspeed", 0, 0, 30, 1, suffix="%", description="acc.settings.3.description")
                    else:
                        Slider("acc.settings.3.name", "overspeed", 0, 0, 30, 1, suffix="km/h", description="acc.settings.3.description")
        return RenderUI()
        

class Plugin(ETS2LAPlugin):
    fps_cap = 15
    
    description = PluginDescription(
        name="plugins.adaptivecruisecontrol",
        version="1.0",
        description="plugins.adaptivecruisecontrol.description",
        modules=["SDKController", "TruckSimAPI", "Traffic"],
        tags=["Base", "Speed Control"]
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    controls = [enable_disable]
    
    settings_menu = SettingsMenu()
    
    status_data = (0, 0)
    last_vehicle_distance = math.inf
    last_time_to_vehicle = math.inf
    last_vehicle_time = time.perf_counter()
    vehicle_speed = math.inf
    vehicle_id = 0
    
    max_speed = SmoothedValue("time", 0.5)
    target_speed = 0
    
    last_red_light_time = 0
    
    last_intersection_distance = math.inf
    last_intersection_distance_time = time.perf_counter()
    
    def imports(self):
        global Controller, np, screeninfo, pyautogui, json, cv2, os
        from Modules.SDKController.main import SCSController as Controller
        import numpy as np
        import screeninfo
        import pyautogui
        import json
        import cv2
        import os
        
        # Update settings on change
        settings.Listen("AdaptiveCruiseControl", LoadSettings)


    def Initialize(self):
        global TruckSimAPI, SDKController
        TruckSimAPI = self.modules.TruckSimAPI
        SDKController = self.modules.SDKController.SCSController()
        SDKController = cast(Controller, SDKController)
        logging.warning("AdaptiveCruiseControl plugin initialized")
        self.globals.tags.status = {"AdaptiveCruiseControl": ACC_ENABLED}
    
    @events.on("toggle_acc")
    def on_toggle_acc(self, state:bool):
        if not state:
            return # Callback for the lift up event
        
        global ACC_ENABLED
        ACC_ENABLED = not ACC_ENABLED
        self.globals.tags.status = {"AdaptiveCruiseControl": ACC_ENABLED}
        
    def DistanceFunction(self, x):
        if x < 0:
            return 0
        if x > 1:
            return 1
        return math.sin((x * math.pi) / 2)
        
    def CalculateAcceleration(self, targetSpeed: float, currentSpeed: float, currentDistance: float, time: float, vehicleSpeed: float, falloffDistance: float = BRAKING_DISTANCE, stoppingDistance: float = STOPPING_DISTANCE) -> tuple:
        distance = currentDistance
        if distance <= 0:
            distance = 999
            
        type = "map"
        if ((time < FOLLOW_TIME and time > 0) or distance < falloffDistance) and (vehicleSpeed < 30/3.6 or vehicleSpeed < currentSpeed*1.1):
            timePercent = time / FOLLOW_TIME
            timeTargetSpeed = timePercent * targetSpeed
            
            distancePercent = self.DistanceFunction(distance / (falloffDistance * 2/3) - (stoppingDistance / (falloffDistance * 2/3)))
            if vehicleSpeed < targetSpeed and vehicleSpeed > 30/3.6:
                distanceTargetSpeed = targetSpeed - (targetSpeed - vehicleSpeed) * (1-distancePercent) * 1.5
            else:
                distanceTargetSpeed = distancePercent * targetSpeed
            
            if timeTargetSpeed < distanceTargetSpeed:
                type = "time"
                targetSpeed = timeTargetSpeed
                self.status_data = (time, FOLLOW_TIME) # f" {time:.1f}s / {FOLLOW_TIME}s"
            else:
                type = "distance"
                targetSpeed = distanceTargetSpeed
                self.status_data = (distance, falloffDistance) # f" {distance:.1f}m / 40m"
            

        # Base accel to stay at current speed
        acceleration = (targetSpeed - currentSpeed) / 3.6
        
        # To accelerate towards the target speed
        acceleration += (targetSpeed - currentSpeed) / 3.6 / 10
        
        return acceleration, targetSpeed, type

    def GetDistanceToPoint(self, point1: list, point2: list) -> float:
        if len(point1) == 2 and len(point2) == 2:
            return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        elif len(point1) == 3 and len(point2) == 3:
            return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

    def GetTimeToVehicleAhead(self, apiData: dict) -> float:
        vehicles = self.modules.Traffic.run()
        
        plugin_vehicles = self.globals.tags.vehicles
        plugin_vehicles = self.globals.tags.merge(plugin_vehicles)
        
        if plugin_vehicles is not None:
            vehicles += [self.modules.Traffic.create_vehicle_from_dict(vehicle) for vehicle in plugin_vehicles]

        if vehicles is None or vehicles == []:
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.inf
            self.last_vehicle_distance = math.inf
            return math.inf
        
        vehiclesInFront = []
        
        truckX = apiData["truckPlacement"]["coordinateX"]
        truckY = apiData["truckPlacement"]["coordinateZ"]
        truckHeight = apiData["truckPlacement"]["coordinateY"]
        truckSpeed = apiData["truckFloat"]["speed"]
        rotation = apiData["truckPlacement"]["rotationX"] * 360
        if rotation < 0: rotation += 360
        rotation = math.radians(rotation)
        
        points = self.plugins.Map
        
        if type(points) != list or len(points) == 0 or (type(points[0]) != list and type(points[0]) != tuple):
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.inf
            self.last_vehicle_distance = math.inf
            return math.inf
        
        if len(points) == 1:
            point = points[0]
            points = [[truckX, truckY], [point[0], point[1]]]
            
        if len(points) == 2:
            # Generate 10 points between the two points
            x1 = points[0][0]
            y1 = points[0][1]
            x2 = points[1][0]
            y2 = points[1][1]
            points = [[x1 + (x2 - x1) * i / 10, y1 + (y2 - y1) * i / 10] for i in range(10)]
        
        if type(vehicles) != list:
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.ifn
            self.last_vehicle_distance = math.inf
            return math.inf
        
        for vehicle in vehicles:
            if len(vehicle.trailers) > 0:
                x = vehicle.trailers[-1].position.x
                y = vehicle.trailers[-1].position.z
                z = vehicle.trailers[-1].position.y
            else:
                x = vehicle.position.x
                y = vehicle.position.z
                z = vehicle.position.y
            
            closestPointDistance = math.inf
            index = 0
            for point in points:
                distance = self.GetDistanceToPoint([x, y, z], [point[0], point[2], point[1]])
                if distance < closestPointDistance:
                    closestPointDistance = distance
                else:
                    # Make an intermediate point
                    lastPoint = points[index - 1]
                    intermediatePoint = [(lastPoint[0] + point[0]) / 2, (lastPoint[2] + point[1]) / 2, (lastPoint[1] + point[2]) / 2]
                    distance = self.GetDistanceToPoint([x, y, z], intermediatePoint)
                    if distance < closestPointDistance:
                        closestPointDistance = distance
                    break
                index += 1
                    
            if closestPointDistance < 4: # Road is 4.5m wide, want to check 3m (to allow for a little bit of error)
                self.last_vehicle_time = time.perf_counter()
                vehiclesInFront.append((self.GetDistanceToPoint([x, y], [truckX, truckY]), vehicle))
                
        if len(vehiclesInFront) == 0:
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.inf
            self.last_vehicle_distance = math.inf
            return math.inf
        
        closestDistance = math.inf
        for distance, vehicle in vehiclesInFront:
            if distance < closestDistance:
                closestDistance = distance
                self.vehicle_speed = vehicle.speed
                self.vehicle_id = vehicle.id
                
        self.last_vehicle_distance = closestDistance
        timeToVehicle = closestDistance / truckSpeed
        timeToVehicle = (closestDistance + self.vehicle_speed / 2 * timeToVehicle) / truckSpeed
            
        self.last_time_to_vehicle = timeToVehicle
        self.last_vehicle_time = time.perf_counter()
        return timeToVehicle
            
    def Reset(self) -> None:
        SDKController.aforward = float(0)
        SDKController.abackward = float(0)

    def GetTargetSpeed(self, apiData: dict) -> float:
        points = self.plugins.Map
        if points is not None:
            max_speed = get_maximum_speed_for_points(points)
            smoothed_max_speed = self.max_speed(max_speed)
        else:
            smoothed_max_speed = 999
        
        target_speed = apiData['truckFloat']['speedLimit']
        
        if TYPE == "Percentage":
            target_speed = target_speed * (1 + OVERSPEED / 100)
            
        if target_speed > 0:
            target_speed += 0.49 / 3.6
        else:
            target_speed = OVERWRITE_SPEED / 3.6  
            
        if TYPE != "Percentage":
            target_speed = target_speed + OVERSPEED / 3.6
         
        if target_speed > smoothed_max_speed and smoothed_max_speed > 0:
            target_speed = smoothed_max_speed
        
        self.target_speed = target_speed

    def RedLightExists(self) -> bool:
        trafficLights = self.globals.tags.traffic_lights
        trafficLights = self.globals.tags.merge(trafficLights)
        
        if trafficLights is None:
            if time.perf_counter() - self.last_red_light_time < .5:
                return True
            return False
        else:
            if type(trafficLights) != list:
                if time.perf_counter() - self.last_red_light_time < .5:
                    return True
                return False
            for light in trafficLights:
                try:
                    if type(light) != dict:
                        continue
                    if light["state"] == "red":
                        self.last_red_light_time = time.perf_counter()
                        return True
                except:
                    continue
                
        if time.perf_counter() - self.last_red_light_time < .5:
            return True
        
        return False

    def GetIntersectionDistance(self) -> float:
        try:
            data = self.globals.tags.next_intersection_distance
            data = self.globals.tags.merge(data)
        except:
            if time.perf_counter() - self.last_intersection_distance_time < 0.5:
                return self.last_intersection_distance
            return math.inf
        
        if type(data) != str and type(data) not in [int, float]:
            if time.perf_counter() - self.last_intersection_distance_time < 0.5:
                return self.last_intersection_distance
            return math.inf

        self.last_intersection_distance_time = time.perf_counter()
        self.last_intersection_distance = float(data)
        return float(data)

    def SetAccelBrake(self, accel:float) -> None:
        if accel > 0:
            SDKController.aforward = float(accel * 10)
            SDKController.abackward = float(0)
        else:
            if self.vehicle_speed > 30/3.6:
                accel = accel * 0.25
            if accel < -1:
                accel = -1
                
            SDKController.abackward = float(-accel)
            SDKController.aforward = float(0)

    def GetStatus(self, type) -> str:
        if type == "time" and SHOW_NOTIFICATIONS:
            self.state.text = "Slowing dow to maintain time gap"
            self.state.progress = 1 - self.status_data[0] / self.status_data[1]
            self.globals.tags.AR = []
            return "Slowing dow to maintain time gap" + f" {self.status_data[0]:.1f}s / {self.status_data[1]}s"
        
        elif type == "distance" and SHOW_NOTIFICATIONS:
            self.state.text = "Slowing down to maintain distance gap"
            self.state.progress = 1 - self.status_data[0] / self.status_data[1]
            self.globals.tags.AR = []
            return "Slowing down to maintain distance gap" + f" {self.status_data[0]:.1f}m / {self.status_data[1]}m"
        
        elif type == "traffic light" and SHOW_NOTIFICATIONS:
            self.state.text = "Stopping for traffic light"
            self.state.progress = 1 - self.status_data[0] / self.status_data[1]
            
            self.globals.tags.AR = [
                Rectangle(
                    Coordinate(-2.25, 1, -self.status_data[0], relative=True, rotation_relative=True),
                    Coordinate(2.25, -1, -self.status_data[0], relative=True, rotation_relative=True),
                    thickness=5,
                    color=Color(255, 0, 0, 60),
                    fill=Color(255, 0, 0, 40),
                    fade=Fade(0, 0, 150, 170),
                )
            ]
            
            return f"Slowing down for traffic light in {self.status_data[0]:.1f}m"
        
        else:
            self.state.reset()
            self.globals.tags.AR = []
            return "Maintaining speed according to map"

    def run(self):
        if not ACC_ENABLED:
            self.globals.tags.AR = []
            self.Reset(); return
            
        apiData = TruckSimAPI.run()
        if apiData['truckFloat']['speedLimit'] == 0 and OVERWRITE_SPEED == 0:
            self.globals.tags.AR = []
            self.Reset(); return
        
        currentSpeed = apiData['truckFloat']['speed']
        
        self.GetTargetSpeed(apiData)
        
        try: timeToVehicle = self.GetTimeToVehicleAhead(apiData)
        except: timeToVehicle = math.inf; logging.exception("Failed to get time to vehicle ahead")
            
        if self.RedLightExists():
            intersectionDistance = self.GetIntersectionDistance()
            if intersectionDistance < self.last_vehicle_distance:
                self.last_vehicle_distance = intersectionDistance
                acceleration, self.target_speed, type = self.CalculateAcceleration(self.target_speed, currentSpeed, self.last_vehicle_distance, timeToVehicle, 0, falloffDistance=BRAKING_DISTANCE * TRAFFIC_LIGHT_DISTANCE_MULTIPLIER / 2, stoppingDistance=STOPPING_DISTANCE * TRAFFIC_LIGHT_DISTANCE_MULTIPLIER)
                self.status_data = (intersectionDistance, BRAKING_DISTANCE * TRAFFIC_LIGHT_DISTANCE_MULTIPLIER)
                type = "traffic light"
            else:
                acceleration, self.target_speed, type = self.CalculateAcceleration(self.target_speed, currentSpeed, self.last_vehicle_distance, timeToVehicle, self.vehicle_speed)
        else:
            acceleration, self.target_speed, type = self.CalculateAcceleration(self.target_speed, currentSpeed, self.last_vehicle_distance, timeToVehicle, self.vehicle_speed)
        
        if ACC_ENABLED:
            if self.target_speed == 0:
                acceleration = -1
            self.SetAccelBrake(acceleration)
        
        self.globals.tags.acc_status = self.GetStatus(type)
        self.globals.tags.acc = self.target_speed
        self.globals.tags.vehicle_highlights = [self.vehicle_id if time.perf_counter() - self.last_vehicle_time < 1 else None]

        if type == "traffic light":
            self.globals.tags.stopping_distance = intersectionDistance

        return None