from ETS2LA.networking.cloud import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
from ETS2LA.utils.logging import logging
import numpy as np
import screeninfo
import pyautogui
import torch
import json
import time
import cv2
import os

runner:PluginRunner = None

class PIDController:
    def __init__(self, kp, ki, kd, setpoint, initial_output=0, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_limits = output_limits

        self._integral = 0
        self._previous_error = None
        self.output = initial_output

    def update(self, measured_value, dt):
        # Calculate error (invert the sign)
        error = measured_value - self.setpoint

        # Proportional term
        p = self.kp * error

        # Integral term
        self._integral += error * dt
        i = self.ki * self._integral

        # Derivative term
        d = 0
        if self._previous_error is not None:
            d = self.kd * (error - self._previous_error) / dt

        # Calculate output
        output = p + i + d

        # Apply output limits
        if self.output_limits[0] is not None:
            output = max(self.output_limits[0], output)
        if self.output_limits[1] is not None:
            output = min(self.output_limits[1], output)

        # Ensure output is not negative
        output = max(output, 0)

        # Save the error for the next update
        self._previous_error = error

        # Save and return the output
        self.output = output
        return output

def Initialize():
    global ShowImage, TruckSimAPI, SDKController, MapUtils
    global last_pid_update, acc_pid, dt, last_frame

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    SDKController = runner.modules.SDKController
    MapUtils = runner.modules.MapUtils

    last_pid_update = time.time()
    last_frame = None
    
    # Window for showing speed
    cv2.namedWindow('Adaptive Cruise Control', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Adaptive Cruise Control', cv2.WND_PROP_TOPMOST, 1)

    # Parameters
    kp = 1.0 # Slightly adjusted proportional gain
    ki = 0.03  # Slightly adjusted integral gain
    kd = 0.01  # Slightly adjusted derivative gain
    setpoint_distance = 6  # Desired distance from vehicle in front in meters
    output_limits = (0, 120)  # speed limits in km/h
    dt = 0.2 # Time step for PID controller

    acc_pid = PIDController(kp, ki, kd, setpoint_distance, output_limits=output_limits)

def GetVehicleLane(raycasts):
    global MapUtils
    raycast1_points = raycasts[0]['point']
    raycast2_points = raycasts[1]['point']
    x = (raycast1_points[0] + raycast2_points[0]) / 2
    y = (raycast1_points[1] + raycast2_points[1]) / 2
    z = (raycast1_points[2] + raycast2_points[2]) / 2

    map_data = MapUtils.run(x, y, z)
    print(map_data)


def plugin():
    global TruckSimAPI, ShowImage, last_pid_update, acc_pid, dt, last_frame

    data = {}
    #data["api"] = TruckSimAPI.run()
    #data["map"] = runner.GetData(["tags.map"])[0]
    data["vehicles"] = runner.GetData(["tags.vehicles"])[0]

    if data["vehicles"] is not None and len(data["vehicles"]) > 0:
        vehicles = data["vehicles"]
        for vehicle in vehicles:
            raycasts = vehicle.json()['raycasts']
            lane = GetVehicleLane(raycasts)

    '''
    if time.time() - last_pid_update > dt:
        print(data["vehicles"])
        frame = np.zeros((300, 200, 3), np.uint8)
        if data["vehicles"] is not None and len(data["vehicles"]) > 0:
            vehicle = data["vehicles"][0]
            distance = vehicle.json()['raycasts'][0]['distance']

            speed = acc_pid.update(distance, dt)
            distance_ft = distance * 3.28084  # Convert meters to feet
            speed_mph = speed * 0.621371  # Convert km/h to mph
            #print(f"Distance: {distance:.2f} m ({distance_ft:.2f} ft), Speed: {speed:.2f} km/h ({speed_mph:.2f} mph)")

            cv2.putText(frame, f"Distance: {distance:.2f} m ({distance_ft:.2f} ft)", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
            cv2.putText(frame, f"Speed: {speed:.2f} km/h ({speed_mph:.2f} mph)", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

            last_pid_update = time.time()
            last_frame = frame
        else:
            if data["vehicles"] is None:
                cv2.putText(frame, "Vehicles list is none", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
            else:
                cv2.putText(frame, "No vehicles detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    else:
        frame = last_frame
    
    if frame is None:
        frame = np.zeros((300, 200, 3), np.uint8)
        cv2.putText(frame, "No vehicles detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        last_frame = frame

    cv2.imshow('Adaptive Cruise Control', frame)
    cv2.waitKey(1)
    '''