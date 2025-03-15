# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 

# ETS2LA imports
from ETS2LA.Networking.cloud import SendCrashReport
import ETS2LA.Handlers.controls as controls
import ETS2LA.Utils.settings as settings
from ETS2LA.Utils.Console.logging import logging
import ETS2LA.variables as variables

# Python imports
from typing import cast
import math
import time


MANUALMODE = True

class Plugin(ETS2LAPlugin):
    fps_cap = 15
    
    description = PluginDescription(
        name="plugins.cruisecontrol",
        version="1.0",
        description="plugins.cruisecontrol.description",
        modules=["SDKController", "ShowImage", "TruckSimAPI"],
        tags=["Speed Control"]
    )
    
    author = [Author(
        name="MRUIAW",
        url="https://github.com/MRUIAW",
        icon="https://avatars.githubusercontent.com/u/119018519?v=4"
    ), 
    Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )]

    last_target_speed_time = 0
    last_target_speed = 0
    target_speed = 0
    

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

    def init(self):
        self.CC_ENABLED = False
        self.MANUALMODE = True
        self.targetSpeed = 0
        self.TruckSimAPI = self.modules.TruckSimAPI
        self.controller = self.modules.SDKController.SCSController()
        self.globals.tags.status = {"CruiseControl": self.CC_ENABLED}
        self.last_target_speed_time = 0

    @events.on("ToggleSteering")
    def ToggleSteering(self, state:bool, *args, **kwargs):
        self.CC_ENABLED = state
        self.globals.tags.status = {"CruiseControl": state}
    


    def DistanceFunction(self, x):
        if x < 0:
            return 0
        if x > 1:
            return 1
        return math.sin((x * math.pi) / 2)


    def CalculateAcceleration(self, targetSpeed: float, currentSpeed: float) -> tuple:

        # Base accel to stay at current speed
        acceleration = (targetSpeed - currentSpeed) / 3.6
        
        # To accelerate towards the target speed
        acceleration += (targetSpeed - currentSpeed) / 3.6 / 10
        
        return acceleration, targetSpeed



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

    def SetAccelBrake(self, accel:float) -> None:
        if accel > 0:
            self.controller.aforward = float(accel * 10)
            self.controller.abackward = float(0)
        else:
            if accel < -1:
                accel = -1
            self.controller.abackward = float(-accel)
            self.controller.aforward = float(0)

    def Reset(self) -> None:
        self.controller.aforward = float(0)
        self.controller.abackward = float(0)
    def run(self):
        apiData = self.TruckSimAPI.run()

        try: self.target_speed = self.GetTargetSpeed(apiData)
        except: self.Reset(); logging.exception("something"); return

        self.currentSpeedNative = apiData['truckFloat']['speed']
        self.currentSpeed = self.currentSpeedNative * 3.6  # convert to km/h
        self.targetSpeedNative = apiData['truckFloat']['speedLimit']
        self.targetSpeed = self.targetSpeedNative * 3.6  # convert to km/h
        self.currentCruiseControlSpeedNative = apiData['truckFloat']['cruiseControlSpeed']
        self.currentCruiseControlSpeed = self.currentCruiseControlSpeedNative * 3.6  # convert to km/h

        self.gamepaused = apiData['pause']


        acceleration, self.target_speed = self.CalculateAcceleration(self.target_speed, self.currentSpeedNative)


        if self.gamepaused == False:
            if self.CC_ENABLED:
                if self.target_speed *3.6 > 30:
                    if apiData['truckBool']['cruiseControl'] == False:
                        if self.target_speed == 0:
                            acceleration = -1
                        self.SetAccelBrake(acceleration)
                        self.controller.cruiectrl = True
                        time.sleep(0.01)
                        self.controller.cruiectrl = False
                        time.sleep(0.01)
                    else:
                        self.controller.aforward = float(0)
                else:
                    if apiData['truckBool']['cruiseControl'] == True:
                        self.controller.cruiectrl = True
                        time.sleep(0.01)
                        self.controller.cruiectrl = False
                        time.sleep(0.01)
                    if self.target_speed == 0:
                        acceleration = -1
                    self.SetAccelBrake(acceleration)
                    
                if self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed < self.targetSpeed:
                    self.controller.cruiectrlinc = True
                    time.sleep(0.01)
                    self.controller.cruiectrlinc = False
                    time.sleep(0.01)
                if self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed > self.targetSpeed:
                    self.controller.cruiectrldec = True
                    time.sleep(0.01)
                    self.controller.cruiectrldec = False
                    time.sleep(0.01)
                self.MANUALMODE = False
            else:
                if not self.MANUALMODE:
                    if apiData['truckBool']['cruiseControl'] == True:
                        self.controller.cruiectrl = True
                        time.sleep(0.05)
                        self.controller.cruiectrl = False
                        time.sleep(0.01)
                    self.MANUALMODE = True
                self.controller.aforward = float(0)


            # some useless code for debug, i dont want to delete it anyway
            # logging.warning("===========================DEBUG INFO START==========================")
            # logging.warning("self.currentCruiseControlSpeedNative == %s", self.currentCruiseControlSpeedNative)
            # logging.warning("self.currentCruiseControlSpeed == %s", self.currentCruiseControlSpeed)
            # logging.warning("self.targetSpeedNative == %s", self.targetSpeedNative)
            # logging.warning("self.targetSpeed == %s", self.targetSpeed)
            # logging.warning("self.target_speed == %s", self.target_speed)
            # logging.warning("acceleration == %s", acceleration)
            # logging.warning("self.currentCruiseControlSpeed != 0 %s", self.currentCruiseControlSpeed != 0)
            # logging.warning("self.currentCruiseControlSpeed < self.targetSpeed %s", self.currentCruiseControlSpeed < self.targetSpeed)
            # logging.warning("self.currentCruiseControlSpeed > self.targetSpeed %s", self.currentCruiseControlSpeed > self.targetSpeed)
            # logging.warning("self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed < self.targetSpeed %s", self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed < self.targetSpeed)
            # logging.warning("self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed > self.targetSpeed %s", self.currentCruiseControlSpeed != 0 and self.currentCruiseControlSpeed > self.targetSpeed)
            # logging.warning("===========================DEBUG INFO END==========================")
            


        # time.sleep(0.1) # minimum fps this will work at is 10fps with this (needs at least 1 frame in game to register)
        
