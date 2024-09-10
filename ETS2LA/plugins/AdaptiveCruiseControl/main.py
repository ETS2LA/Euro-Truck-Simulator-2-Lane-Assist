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

FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "distance", 3) # meters
ACC_ENABLED = False

def LoadSettings():
    global FOLLOW_TIME
    FOLLOW_TIME = settings.Get("AdaptiveCruiseControl", "distance", 3)
    
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
    
def CalculateAcceleration(targetSpeed: float, currentSpeed: float, time: float) -> float:
    # Adjust the target speed based on the distance to the vehicle ahead
    if time < FOLLOW_TIME and time > 0:
        targetSpeed = (time / FOLLOW_TIME) * targetSpeed
    # First calculate the acceleration needed to keep the speed constant
    acceleration = (targetSpeed - currentSpeed) / 3.6
    # Then add an offset based on how far we are from the target speed
    acceleration += (targetSpeed - currentSpeed) / 3.6 / 10
    return acceleration, targetSpeed

lastVehicleDistance = math.inf
vehicleSpeed = math.inf
lastVehicleTime = time.time()
lastTimeToVehicle = math.inf
def GetTimeToVehicleAhead(apiData: dict) -> float:
    global lastVehicleDistance, lastVehicleTime, vehicleSpeed, lastTimeToVehicle
    vehicles = runner.GetData(['tags.vehicles'])[0]
    if vehicles is None:
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        return math.inf
    
    vehiclesInFront = []
    
    rotation = apiData["truckPlacement"]["rotationX"] * 360
    if rotation < 0: rotation += 360
    rotation = math.radians(rotation)
    
    truckSpeed = apiData["truckFloat"]["speed"]
    
    if type(vehicles) != list:
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        return math.inf
    
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
        
        # Get the angle to work with.
        # At 50kph it should be 2 degrees
        # at 0 kph it should be 40 degrees
        truckSpeedKph = truckSpeed * 3.6
        if truckSpeedKph < 1:
            checkAngle = 15
        elif truckSpeedKph < 50:
            checkAngle = 2 + (15-2) * (1 - truckSpeedKph / 50)
        else:
            checkAngle = 2
        
        if angle < math.radians(checkAngle) and angle > -math.radians(checkAngle):
            distance = math.sqrt(averageX**2 + averageY**2)
            vehiclesInFront.append((distance, vehicle))
            lastVehicleTime = time.time()
            
    if len(vehiclesInFront) == 0:
        if time.time() - lastVehicleTime < 1:
            return lastTimeToVehicle
        return math.inf
    
    closestDistance = math.inf
    for distance, vehicle in vehiclesInFront:
        if distance < closestDistance:
            closestDistance = distance
            vehicleSpeed = vehicle.speed
            
    lastVehicleDistance = closestDistance

    if vehicleSpeed < 5:
        # Check if the vehicle is close enough to care about
        if closestDistance / (max(15/3.6, truckSpeed)) > FOLLOW_TIME:
            if time.time() - lastVehicleTime < 1:
                return lastTimeToVehicle
            return math.inf
        timeToVehicle = 0.001
    else:
        timeToVehicle = closestDistance / truckSpeed
        
    lastTimeToVehicle = timeToVehicle
    return timeToVehicle
        
    
lastTargetSpeed = 0
lastTargetSpeedTime = time.time()
def plugin():
    global lastTargetSpeed, lastTargetSpeedTime
    
    if not ACC_ENABLED:
        SDKController.aforward = float(0)
        SDKController.abackward = float(0)
        #return
    
    try:
        apiData = TruckSimAPI.run()
        
        if apiData['truckFloat']['speedLimit'] == 0:
            SDKController.aforward = float(0)
            SDKController.abackward = float(0)
            #return
        
        # if apiData["truckFloat"]["userThrottle"] > 0.05 or apiData["truckFloat"]["userBrake"] > 0.05:
        #     SDKController.aforward = float(0)
        #     SDKController.abackward = float(0)
        #     logging.warning("AdaptiveCruiseControl plugin disabled due to user input")
        #     return
        
        targetSpeed = runner.GetData(['tags.targetSpeed'])[0]
        
        currentSpeed = apiData['truckFloat']['speed']
        
        if targetSpeed is None or not isinstance(targetSpeed, float):
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
            timeToVehicle = GetTimeToVehicleAhead(apiData)
        except:
            timeToVehicle = math.inf
            logging.exception("Failed to get time to vehicle ahead")
            
        acceleration, targetSpeed = CalculateAcceleration(targetSpeed, currentSpeed, timeToVehicle)
        
        if ACC_ENABLED:
            if acceleration > 0:
                SDKController.aforward = float(acceleration * 10)
                SDKController.abackward = float(0)
            else:
                SDKController.abackward = float(-acceleration * 0.25)
                SDKController.aforward = float(0)
        
        return None, {
            "status": f"Time: {lastTimeToVehicle:.2f}s, Distance: {lastVehicleDistance*3.6:.2f}m, Other Speed: {vehicleSpeed*3.6:.2f}kph",
        } 
    
    except:
        logging.exception("AdaptiveCruiseControl plugin failed")
        SDKController.aforward = float(0)
        SDKController.abackward = float(0)