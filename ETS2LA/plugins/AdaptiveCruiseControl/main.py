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
ACC_ENABLED = False

def LoadSettings():
    global FOLLOW_TIME, OVERSPEED_PERCENTAGE
    FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "time", 3)
    OVERSPEED_PERCENTAGE = settings.Get("AdaptiveCruiseControl", "overspeed", 0)
    
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
    
def CalculateAcceleration(targetSpeed: float, currentSpeed: float, currentDistance: float, time: float, vehicleSpeed: float) -> float:
    distance = currentDistance
    if distance <= 0:
        distance = 999
        
    type = "map"
    if ((time < FOLLOW_TIME and time > 0) or distance < 40) and (vehicleSpeed < 30 or vehicleSpeed < currentSpeed*1.1):
        timeTargetSpeed = (time / (FOLLOW_TIME)) * targetSpeed
        distanceTargetSpeed = ((distance) / 30 - 1/3) * targetSpeed
        print(f"timeTargetSpeed: {timeTargetSpeed}, distanceTargetSpeed: {distanceTargetSpeed}               ", end="\r")
        type = "time" if timeTargetSpeed < distanceTargetSpeed else "distance"
        targetSpeed = min(timeTargetSpeed, distanceTargetSpeed) 

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
        x1, y1 = points[0]
        x2, y2 = points[1]
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

def SetAccelBrake(accel:float) -> None:
    if accel > 0:
        SDKController.aforward = float(accel * 10)
        SDKController.abackward = float(0)
    else:
        SDKController.abackward = float(-accel * 0.25)
        SDKController.aforward = float(0)

def GetStatus(type) -> str:
    if type == "time":
        return "Slowing dow to maintain time gap"
    elif type == "distance":
        return "Slowing down to maintain distance gap"
    else:
        return "Maintaining speed according to map"

def plugin():
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
        
    acceleration, targetSpeed, type = CalculateAcceleration(targetSpeed, currentSpeed, lastVehicleDistance, timeToVehicle, vehicleSpeed)
    
    if ACC_ENABLED:
        SetAccelBrake(acceleration)
        
    return None, {
        "status": GetStatus(type),
        "acc": targetSpeed,
        "highlights": [vehicleId if time.time() - lastVehicleTime < 1 else None]
    } 