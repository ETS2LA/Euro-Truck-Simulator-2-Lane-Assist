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

FOLLOW_DISTANCE = settings.Get("AdaptiveCruiseControl", "distance", 30) # meters

def LoadSettings():
    global FOLLOW_DISTANCE
    FOLLOW_DISTANCE = settings.Get("AdaptiveCruiseControl", "distance", 30)
    
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
    
def CalculateAcceleration(targetSpeed: float, currentSpeed: float, distance: float) -> float:
    # Adjust the target speed based on the distance to the vehicle ahead
    if distance < FOLLOW_DISTANCE and vehicleSpeed < currentSpeed:
        targetSpeed = (distance / FOLLOW_DISTANCE) * targetSpeed
    # First calculate the acceleration needed to keep the speed constant
    acceleration = (targetSpeed - currentSpeed) / 3.6
    # Then add an offset based on how far we are from the target speed
    acceleration += (targetSpeed - currentSpeed) / 3.6 / 10
    return acceleration

lastVehicleDistance = math.inf
vehicleSpeed = math.inf
lastVehicleTime = time.time()
def GetDistanceToVehicleAhead(apiData: dict) -> float:
    global lastVehicleDistance, lastVehicleTime, vehicleSpeed
    vehicles = runner.GetData(['tags.vehicles'])[0]
    if vehicles is None:
        return math.inf
    
    vehiclesInFront = []
    
    rotation = apiData["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    for vehicle in vehicles:
        if isinstance(vehicle, dict):
            vehicle = Vehicle(None, None, None, None, None).fromJson(vehicle)
        if not isinstance(vehicle, Vehicle):
            continue
        
        # Create a line from the two relative points on the vehicle
        x1 = vehicle.raycasts[0].relativePoint[0]
        y1 = vehicle.raycasts[0].relativePoint[2]
        x2 = vehicle.raycasts[1].relativePoint[0]
        y2 = vehicle.raycasts[1].relativePoint[2]
        
        averageX = (x1 + x2) / 2
        averageY = (y1 + y2) / 2
        
        truckForwardVector = np.array([-math.sin(rotation), -math.cos(rotation)])
        pointVector = np.array([averageX, averageY])
        normalizedPointVector = pointVector / np.linalg.norm(pointVector)
        normalizedTruckForwardVector = truckForwardVector / np.linalg.norm(truckForwardVector)

        angle = math.acos(np.dot(normalizedPointVector, normalizedTruckForwardVector))
        
        if angle < math.radians(2) and angle > -math.radians(2):
            distance = math.sqrt(averageX**2 + averageY**2)
            vehiclesInFront.append((distance, vehicle))
            lastVehicleDistance = distance
            lastVehicleTime = time.time()
            vehcileSpeed = vehicle.speed
        
            
    if len(vehiclesInFront) == 0:
        if time.time() - lastVehicleTime < 1:
            return lastVehicleDistance
        return math.inf
    
    closestDistance = math.inf
    for distance, vehicle in vehiclesInFront:
        if distance < closestDistance:
            closestDistance = distance
            
    return closestDistance
        
    
lastTargetSpeed = 0
lastTargetSpeedTime = time.time()
def plugin():
    global lastTargetSpeed, lastTargetSpeedTime
    try:
        apiData = TruckSimAPI.run()
        
        
        # if apiData["truckFloat"]["userThrottle"] > 0.05 or apiData["truckFloat"]["userBrake"] > 0.05:
        #     SDKController.aforward = float(0)
        #     SDKController.abackward = float(0)
        #     logging.warning("AdaptiveCruiseControl plugin disabled due to user input")
        #     return
        
        targetSpeed = runner.GetData(['tags.targetSpeed'])[0]
        
        currentSpeed = apiData['truckFloat']['speed']
        
        if targetSpeed is None or isinstance(targetSpeed, list):
            if time.time() - lastTargetSpeedTime > 1:
                targetSpeed = apiData['truckFloat']['speedLimit']
                lastTargetSpeed = targetSpeed
                lastTargetSpeedTime = time.time()
            else: 
                targetSpeed = lastTargetSpeed
        else:
            lastTargetSpeed = targetSpeed
            lastTargetSpeedTime = time.time()                
            
        if targetSpeed != 0:
            targetSpeed += 0.5 / 3.6 # Add a small offset to the target speed to avoid oscillations
        
        try:
            distance = GetDistanceToVehicleAhead(apiData)
        except:
            distance = math.inf
            
        acceleration = CalculateAcceleration(targetSpeed, currentSpeed, distance)
        
        if acceleration > 0:
            SDKController.aforward = float(acceleration * 10)
            SDKController.abackward = float(0)
        else:
            SDKController.abackward = float(-acceleration * 1)
            SDKController.aforward = float(0)
        
        # return None, {
        #     "status": " Normal" if distance > FOLLOW_DISTANCE else " Slowing",
        # }    
        
    except:
        logging.exception("AdaptiveCruiseControl plugin failed")
        SDKController.aforward = float(0)