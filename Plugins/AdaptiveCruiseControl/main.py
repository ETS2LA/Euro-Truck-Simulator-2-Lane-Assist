# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 

# ETS2LA imports
from Plugins.ObjectDetection.classes import Vehicle
from ETS2LA.Networking.cloud import SendCrashReport
import ETS2LA.Handlers.controls as controls
import ETS2LA.Utils.settings as settings
from ETS2LA.Utils.Console.logging import logging
import ETS2LA.variables as variables

# Python imports
from typing import cast
import math
import time

FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3) # seconds
OVERSPEED = settings.Get("AdaptiveCruiseControl", "overspeed", 0) # 0-100
BRAKING_DISTANCE = settings.Get("AdaptiveCruiseControl", "braking_distance", 60) # meters
STOPPING_DISTANCE = settings.Get("AdaptiveCruiseControl", "stopping_distance", 15) # meters
TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = settings.Get("AdaptiveCruiseControl", "traffic_light_distance_multiplier", 1.5) # times
ACC_ENABLED = False
TYPE = settings.Get("AdaptiveCruiseControl", "type", "Percentage")
SHOW_NOTIFICATIONS = settings.Get("AdaptiveCruiseControl", "show_notifications", True)

def LoadSettings():
    global FOLLOW_TIME, OVERSPEED, BRAKING_DISTANCE, STOPPING_DISTANCE, TRAFFIC_LIGHT_DISTANCE_MULTIPLIER, TYPE, SHOW_NOTIFICATIONS
    FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3)
    OVERSPEED = settings.Get("AdaptiveCruiseControl", "overspeed", 0)
    BRAKING_DISTANCE = settings.Get("AdaptiveCruiseControl", "braking_distance", 60)
    STOPPING_DISTANCE = settings.Get("AdaptiveCruiseControl", "stopping_distance", 15)
    TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = settings.Get("AdaptiveCruiseControl", "traffic_light_distance_multiplier", 1.5)
    TYPE = settings.Get("AdaptiveCruiseControl", "type", "Percentage")
    SHOW_NOTIFICATIONS = settings.Get("AdaptiveCruiseControl", "show_notifications", True)
    
# Update settings on change
settings.Listen("AdaptiveCruiseControl", LoadSettings)

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "AdaptiveCruiseControl"
    def render(self):
        Label("acc.settings.1.title", classname_preset=TitleClassname)
        Label("acc.settings.1.description", classname_preset=DescriptionClassname)
        Separator()
        Slider("acc.settings.2.name", "time", 1, 0, 4, 0.5, description="acc.settings.2.description")
        Slider("acc.settings.4.name", "stopping_distance", 15, 0, 100, 2.5, description="acc.settings.4.description")
        Switch("acc.settings.6.name", "show_notifications", True, description="acc.settings.6.description")
        Separator()
        with EnabledLock():
            Selector("acc.settings.5.name", "type", "Percentage", ["Percentage", "Absolute"], "acc.settings.5.description")
            if self.settings.type is not None and self.settings.type == "Percentage":
                Slider("acc.settings.3.name", "overspeed", 0, 0, 20, 1, description="acc.settings.3.description")
            else:
                Slider("acc.settings.3.name", "overspeed", 0, 0, 20, 1, description="acc.settings.3.description")
        return RenderUI()
        

class Plugin(ETS2LAPlugin):
    fps_cap = 15
    
    description = PluginDescription(
        name="plugins.adaptivecruisecontrol",
        version="1.0",
        description="plugins.adaptivecruisecontrol.description",
        modules=["SDKController", "ShowImage", "TruckSimAPI"],
        tags=["Base", "Speed Control"]
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    settings_menu = SettingsMenu()
    
    status_data = (0, 0)
    last_vehicle_distance = math.inf
    last_time_to_vehicle = math.inf
    last_vehicle_time = time.perf_counter()
    vehicle_speed = math.inf
    vehicle_id = 0
    
    last_target_speed_time = 0
    last_target_speed = 0
    target_speed = 0
    
    last_red_light_time = 0
    
    last_intersection_distance = math.inf
    last_intersection_distance_time = time.perf_counter()
    
    def imports(self):
        global Controller, np, screeninfo, pyautogui, torch, json, cv2, os
        from Modules.SDKController.main import SCSController as Controller
        import numpy as np
        import screeninfo
        import pyautogui
        import torch
        import json
        import cv2
        import os


    def Initialize(self):
        global ShowImage, TruckSimAPI, SDKController
        ShowImage = self.modules.ShowImage
        TruckSimAPI = self.modules.TruckSimAPI
        SDKController = self.modules.SDKController.SCSController()
        SDKController = cast(Controller, SDKController)
        logging.warning("AdaptiveCruiseControl plugin initialized")
        self.globals.tags.status = {"AdaptiveCruiseControl": ACC_ENABLED}
    
    @events.on("ToggleSteering")
    def ToggleSteering(self, state:bool, *args, **kwargs):
        global ACC_ENABLED
        ACC_ENABLED = state
        self.globals.tags.status = {"AdaptiveCruiseControl": state}
        
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
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def GetTimeToVehicleAhead(self, apiData: dict) -> float:
        vehicles = self.globals.tags.vehicles
        vehicles = self.globals.tags.merge(vehicles)

        if vehicles is None:
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.inf
            self.last_vehicle_distance = math.inf
            return math.inf
        
        vehiclesInFront = []
        
        truckX = apiData["truckPlacement"]["coordinateX"]
        truckY = apiData["truckPlacement"]["coordinateZ"]
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
            if isinstance(vehicle, dict):
                vehicle = Vehicle(None, None, None, None, None).fromJson(vehicle)
            if not isinstance(vehicle, Vehicle):
                continue
            
            # Create a line from the two relative points on the vehicle
            x1 = vehicle.raycasts[0].point[0]
            y1 = vehicle.raycasts[0].point[2]
            x2 = vehicle.raycasts[1].point[0]
            y2 = vehicle.raycasts[1].point[2]
            
            averageX = (x1 + x2) / 2
            averageY = (y1 + y2) / 2
            
            closestPointDistance = math.inf
            index = 0
            for point in points:
                distance = self.GetDistanceToPoint([averageX, averageY], [point[0], point[2]])
                if distance < closestPointDistance:
                    closestPointDistance = distance
                else:
                    # Make an intermediate point
                    lastPoint = points[index - 1]
                    intermediatePoint = [(lastPoint[2] + point[2]) / 2, (lastPoint[2] + point[2]) / 2]
                    distance = self.GetDistanceToPoint([averageX, averageY], intermediatePoint)
                    if distance < closestPointDistance:
                        closestPointDistance = distance
                    break
                index += 1
                    
            if closestPointDistance < 2: # Road is 4.5m wide, want to check 4m
                self.last_vehicle_time = time.perf_counter()
                vehiclesInFront.append((self.GetDistanceToPoint([averageX, averageY], [truckX, truckY]), vehicle))
                
        if len(vehiclesInFront) == 0:
            if time.perf_counter() - self.last_vehicle_time < 1:
                return self.last_time_to_vehicle
            self.vehicle_speed = math.inf
            self.last_vehicle_distance = math.inf
            return math.inf
        
        closestDistance = math.inf
        for distance, vehicle in vehiclesInFront:
            if distance < closestDistance:
                closestDistance = vehicle.distance
                self.vehicle_speed = vehicle.speed
                self.vehicle_id = vehicle.id
                
        self.last_vehicle_distance = closestDistance
        timeToVehicle = closestDistance / truckSpeed
        timeToVehicle = (closestDistance + self.vehicle_speed / 2 * timeToVehicle) / truckSpeed
            
        self.last_time_to_vehicle = timeToVehicle
        return timeToVehicle
            
    def Reset(self) -> None:
        SDKController.aforward = float(0)
        SDKController.abackward = float(0)

    def GetTargetSpeed(self, apiData: dict) -> float:
        targetSpeed = self.globals.tags.target_speed
        targetSpeed = self.globals.tags.merge(targetSpeed)
        
        if targetSpeed is None or not isinstance(targetSpeed, float):
            if time.perf_counter() - self.last_target_speed_time > 1:
                targetSpeed = apiData['truckFloat']['speedLimit']
                self.last_target_speed = targetSpeed
                self.last_target_speed_time = time.perf_counter()
            else: 
                targetSpeed = self.last_target_speed
        else:
            if TYPE == "Percentage":
                targetSpeed = targetSpeed * (1 + OVERSPEED / 100)
            else:
                targetSpeed = targetSpeed + OVERSPEED / 3.6
            self.last_target_speed = targetSpeed
            self.last_target_speed_time = time.perf_counter() 
            
        if targetSpeed > 0:
            targetSpeed += 0.5 / 3.6
        else:
            road_type = self.globals.tags.road_type
            road_type = self.globals.tags.merge(road_type)
            if road_type == "normal":
                targetSpeed = 30 / 3.6
            elif road_type == "highway":
                targetSpeed = 80 / 3.6
            else:
                targetSpeed = 0
                    
        return targetSpeed

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
            return "Slowing dow to maintain time gap" + f" {self.status_data[0]:.1f}s / {self.status_data[1]}s"
        elif type == "distance" and SHOW_NOTIFICATIONS:
            self.state.text = "Slowing down to maintain distance gap"
            self.state.progress = 1 - self.status_data[0] / self.status_data[1]
            return "Slowing down to maintain distance gap" + f" {self.status_data[0]:.1f}m / {self.status_data[1]}m"
        elif type == "traffic light" and SHOW_NOTIFICATIONS:
            self.state.text = "Stopping for traffic light"
            self.state.progress = 1 - self.status_data[0] / self.status_data[1]
            return f"Slowing down for traffic light in {self.status_data[0]:.1f}m"
        else:
            self.state.reset()
            return "Maintaining speed according to map"

    def run(self):
        if not ACC_ENABLED:
            self.Reset(); return
            
        apiData = TruckSimAPI.run()
        if apiData['truckFloat']['speedLimit'] == 0:
            self.Reset(); return
        
        currentSpeed = apiData['truckFloat']['speed']
        
        try: self.target_speed = self.GetTargetSpeed(apiData)
        except: self.Reset(); logging.exception("something"); return
        
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
        self.globals.tags.highlights = [self.vehicle_id if time.perf_counter() - self.last_vehicle_time < 1 else None]

        if type == "traffic light":
            self.globals.tags.stopping_distance = intersectionDistance

        return None