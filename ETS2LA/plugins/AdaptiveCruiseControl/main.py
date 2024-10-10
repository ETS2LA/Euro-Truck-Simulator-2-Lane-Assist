from ETS2LA.modules.SDKController.main import SCSController as Controller
from ETS2LA.plugins.ObjectDetection.classes import Vehicle
from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
from ETS2LA.utils.logging import logging
import ETS2LA.variables as variables
from typing import cast
import numpy as np
import screeninfo
import pyautogui
import torch
import math
import json
import time
import cv2
import os

runner:PluginRunner = None

FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3) # seconds
OVERSPEED_PERCENTAGE = settings.Get("AdaptiveCruiseControl", "overspeed", 0) # 0-100
BRAKING_DISTANCE = settings.Get("AdaptiveCruiseControl", "braking_distance", 60) # meters
STOPPING_DISTANCE = settings.Get("AdaptiveCruiseControl", "stopping_distance", 15) # meters
TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = settings.Get("AdaptiveCruiseControl", "traffic_light_distance_multiplier", 1.5) # times
ACC_ENABLED = False

def LoadSettings():
    global FOLLOW_TIME, OVERSPEED_PERCENTAGE, BRAKING_DISTANCE, STOPPING_DISTANCE, TRAFFIC_LIGHT_DISTANCE_MULTIPLIER
    FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3)
    OVERSPEED_PERCENTAGE = settings.Get("AdaptiveCruiseControl", "overspeed", 0)
    BRAKING_DISTANCE = settings.Get("AdaptiveCruiseControl", "braking_distance", 60)
    STOPPING_DISTANCE = settings.Get("AdaptiveCruiseControl", "stopping_distance", 15)
    TRAFFIC_LIGHT_DISTANCE_MULTIPLIER = settings.Get("AdaptiveCruiseControl", "traffic_light_distance_multiplier", 1.5)
    
# Update settings on change
settings.Listen("AdaptiveCruiseControl", LoadSettings)

def Initialize():
    global ShowImage, TruckSimAPI, SDKController, MapUtils
    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    SDKController = runner.modules.SDKController.SCSController()
    SDKController = cast(Controller, SDKController)
    MapUtils = runner.modules.MapUtils
    logging.warning("AdaptiveCruiseControl plugin initialized")
    
def ToggleSteering(state:bool, *args, **kwargs):
    global ACC_ENABLED
    ACC_ENABLED = state
    
def DistanceFunction(x):
    if x < 0:
        return 0
    if x > 1:
        return 1
    return math.sin((x * math.pi) / 2)
    
statusData = ""
def CalculateAcceleration(targetSpeed: float, currentSpeed: float, currentDistance: float, time: float, vehicleSpeed: float, falloffDistance: float = BRAKING_DISTANCE, stoppingDistance: float = STOPPING_DISTANCE) -> tuple:
    global statusData
    
    distance = currentDistance
    if distance <= 0:
        distance = 999
        
    type = "map"
    if ((time < FOLLOW_TIME and time > 0) or distance < falloffDistance) and (vehicleSpeed < 30/3.6 or vehicleSpeed < currentSpeed*1.1):
        timePercent = time / FOLLOW_TIME
        timeTargetSpeed = timePercent * targetSpeed
        
        distancePercent = DistanceFunction(distance / (falloffDistance * 2/3) - (stoppingDistance / (falloffDistance * 2/3)))
        distanceTargetSpeed = distancePercent * targetSpeed
        
        if timeTargetSpeed < distanceTargetSpeed:
            type = "time"
            targetSpeed = timeTargetSpeed
            statusData = (time, FOLLOW_TIME) # f" {time:.1f}s / {FOLLOW_TIME}s"
        else:
            type = "distance"
            targetSpeed = distanceTargetSpeed
            statusData = (distance, falloffDistance) # f" {distance:.1f}m / 40m"
        

    # Base accel to stay at current speed
    acceleration = (targetSpeed - currentSpeed) / 3.6
    
    # To accelerate towards the target speed
    acceleration += (targetSpeed - currentSpeed) / 3.6 / 10
    
    return acceleration, targetSpeed, type

def GetDistanceToPoint(point1: list, point2: list) -> float:
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

lastVehicleDistance = math.inf
vehicleSpeed = math.inf
lastVehicleTime = time.time()
lastTimeToVehicle = math.inf
vehicleId = 0
def GetTimeToVehicleAhead(apiData: dict) -> float:
    global lastVehicleDistance, lastVehicleTime, vehicleSpeed, lastTimeToVehicle, vehicleId
    vehicles = runner.GetData(['tags.vehicles'])[0]

    if vehicles is None:
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        lastVehicleDistance = math.inf
        return math.inf
    
    vehiclesInFront = []
    
    truckX = apiData["truckPlacement"]["coordinateX"]
    truckY = apiData["truckPlacement"]["coordinateZ"]
    truckSpeed = apiData["truckFloat"]["speed"]
    rotation = apiData["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    points = runner.GetData(["Map"])[0]
    
    if type(points) != list or len(points) == 0 or (type(points[0]) != list and type(points[0]) != tuple):
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        lastVehicleDistance = math.inf
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
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        lastVehicleDistance = math.inf
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
            distance = GetDistanceToPoint([averageX, averageY], point)
            if distance < closestPointDistance:
                closestPointDistance = distance
            else:
                # Make an intermediate point
                lastPoint = points[index - 1]
                intermediatePoint = [(lastPoint[0] + point[0]) / 2, (lastPoint[1] + point[1]) / 2]
                distance = GetDistanceToPoint([averageX, averageY], intermediatePoint)
                if distance < closestPointDistance:
                    closestPointDistance = distance
                break
            index += 1
                
        if closestPointDistance < 2: # Road is 4.5m wide, want to check 4m
            lastVehicleTime = time.time()
            vehiclesInFront.append((GetDistanceToPoint([averageX, averageY], [truckX, truckY]), vehicle))
            
    if len(vehiclesInFront) == 0:
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        lastVehicleDistance = math.inf
        return math.inf
    
    closestDistance = math.inf
    for distance, vehicle in vehiclesInFront:
        if distance < closestDistance:
            closestDistance = vehicle.distance
            vehicleSpeed = vehicle.speed
            vehicleId = vehicle.id
            
    lastVehicleDistance = closestDistance
    timeToVehicle = closestDistance / truckSpeed
    timeToVehicle = (closestDistance + vehicleSpeed / 2 * timeToVehicle) / truckSpeed
        
    lastTimeToVehicle = timeToVehicle
    return timeToVehicle
        
def Reset() -> None:
    SDKController.aforward = float(0)
    SDKController.abackward = float(0)

lastTargetSpeedTime = 0
lastTargetSpeed = 0
targetSpeed = 0
def GetTargetSpeed(apiData: dict) -> float:
    global lastTargetSpeed, lastTargetSpeedTime, targetSpeed
    targetSpeed = runner.GetData(['tags.targetSpeed'])[0]
    
    if targetSpeed is None or not isinstance(targetSpeed, float):
        if time.time() - lastTargetSpeedTime > 1:
            targetSpeed = apiData['truckFloat']['speedLimit']
            lastTargetSpeed = targetSpeed
            lastTargetSpeedTime = time.time()
        else: 
            targetSpeed = lastTargetSpeed
    else:
        targetSpeed = targetSpeed * (1 + OVERSPEED_PERCENTAGE / 100)
        lastTargetSpeed = targetSpeed
        lastTargetSpeedTime = time.time() 
        
    if targetSpeed != 0:
        targetSpeed += 0.5 / 3.6
            
    return targetSpeed

lastRedLightTime = 0
def RedLightExists() -> bool:
    global lastRedLightTime
    trafficLights = runner.GetData(['tags.traffic_lights'])[0]
    if trafficLights is None:
        if time.time() - lastRedLightTime < .5:
            return True
        return False
    else:
        if type(trafficLights) != list:
            if time.time() - lastRedLightTime < .5:
                return True
            return False
        for light in trafficLights:
            try:
                if type(light) != dict:
                    continue
                if light["state"] == "red":
                    lastRedLightTime = time.time()
                    return True
            except: continue
            
    if time.time() - lastRedLightTime < .5:
        return True
    
    return False

lastIntersectionDistance = math.inf
lastIntersectionDistanceTime = time.time()
def GetIntersectionDistance() -> float:
    global lastIntersectionDistance, lastIntersectionDistanceTime
    try:
        data = runner.GetData(['tags.next_intersection_distance'])[0]
    except:
        if time.time() - lastIntersectionDistanceTime < 0.5:
            return lastIntersectionDistance
        return math.inf
    
    if type(data) != str and type(data) != float:
        if time.time() - lastIntersectionDistanceTime < 0.5:
            return lastIntersectionDistance
        return math.inf
    
    lastIntersectionDistance = float(data)
    return float(data)

def SetAccelBrake(accel:float) -> None:
    if accel > 0:
        SDKController.aforward = float(accel * 10)
        SDKController.abackward = float(0)
    else:
        SDKController.abackward = float(-accel * 0.25)
        SDKController.aforward = float(0)

def GetStatus(type) -> str:
    if type == "time":
        runner.state = "Slowing dow to maintain time gap"
        runner.state_progress = 1 - statusData[0] / statusData[1]
        return "Slowing dow to maintain time gap" + f" {statusData[0]:.1f}s / {statusData[1]}s"
    elif type == "distance":
        runner.state = "Slowing down to maintain distance gap"
        runner.state_progress = 1 - statusData[0] / statusData[1]
        return "Slowing down to maintain distance gap" + f" {statusData[0]:.1f}m / {statusData[1]}m"
    elif type == "traffic light":
        runner.state = "Stopping for traffic light"
        runner.state_progress = 1 - statusData[0] / statusData[1]
        return f"Slowing down for traffic light in {statusData[0]:.1f}m"
    else:
        runner.state = "running"
        runner.state_progress = -1
        return "Maintaining speed according to map"

def plugin():
    global lastVehicleDistance
    
    if not ACC_ENABLED:
        Reset(); return
        
    apiData = TruckSimAPI.run()
    if apiData['truckFloat']['speedLimit'] == 0:
        Reset(); return
    
    currentSpeed = apiData['truckFloat']['speed']
    
    try: targetSpeed = GetTargetSpeed(apiData)
    except: Reset(); logging.exception("something"); return
    
    try: timeToVehicle = GetTimeToVehicleAhead(apiData)
    except: timeToVehicle = math.inf; logging.exception("Failed to get time to vehicle ahead")
        
    if RedLightExists(): 
        intersectionDistance = GetIntersectionDistance()
        if intersectionDistance < lastVehicleDistance:
            lastVehicleDistance = intersectionDistance
            acceleration, targetSpeed, type = CalculateAcceleration(targetSpeed, currentSpeed, lastVehicleDistance, timeToVehicle, 0, falloffDistance=BRAKING_DISTANCE * TRAFFIC_LIGHT_DISTANCE_MULTIPLIER, stoppingDistance=STOPPING_DISTANCE * TRAFFIC_LIGHT_DISTANCE_MULTIPLIER)
            type = "traffic light"
        else:
            acceleration, targetSpeed, type = CalculateAcceleration(targetSpeed, currentSpeed, lastVehicleDistance, timeToVehicle, vehicleSpeed)
    else:
        acceleration, targetSpeed, type = CalculateAcceleration(targetSpeed, currentSpeed, lastVehicleDistance, timeToVehicle, vehicleSpeed)
    
    if ACC_ENABLED:
        if targetSpeed == 0:
            acceleration = -1
        SetAccelBrake(acceleration)
        
    return None, {
        "status": GetStatus(type),
        "acc": targetSpeed,
        "highlights": [vehicleId if time.time() - lastVehicleTime < 1 else None]
    } 