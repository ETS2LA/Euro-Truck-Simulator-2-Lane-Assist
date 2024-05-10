import numpy as np
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import cv2
import time
import logging

runner:PluginRunner = None

SMOOTH_TIME = 0.1 # seconds
"""How many seconds to smooth the steering over."""
OFFSET = 0
"""Offset to add to the steering angle."""
SENSITIVITY = 1
"""Overall sensitivity"""
MAX_ANGLE = 1
"""Maximum absolute angle"""
IGNORE_SMOOTH = True
"""USE THIS WHEN USING GAMEPAD MODE"""


class SteeringValue:
    def __init__(self, value:float, timestamp:float):
        self.value = value
        self.timestamp = timestamp
        
    def IsOlderThan(self, timestamp:float):
        return self.timestamp < timestamp

steeringValues = []

def Initialize():
    global SDK
    global API
    # Check if the SDK module is available
    try:
        SDK = runner.modules.SDKController.SCSController()
    except:
        SDK = None
        logging.warning("SDK module not available, please add it to the plugin.json file.")
    # Check if the API module is available
    try:
        API = runner.modules.TruckSimAPI
    except:
        API = None
        logging.warning("TruckSimAPI module not available, please add it to the plugin.json file.")

def get_text_size(text="NONE", width=100, height=100, text_width=100, max_text_height=100):
    fontscale = 1
    textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
    width_current_text, height_current_text = textsize
    max_count_current_text = 3
    while width_current_text != text_width or height_current_text > max_text_height:
        fontscale *= min(text_width / textsize[0], max_text_height / textsize[1])
        textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    thickness = round(fontscale * 2)
    if thickness <= 0:
        thickness = 1
    return text, fontscale, thickness, textsize[0], textsize[1]

def CalculateSteeringAngle():
    global steeringValues
    
    if not IGNORE_SMOOTH:
        weights = np.arange(len(steeringValues)) + 1
        average = np.average([value.value for value in steeringValues], weights=weights)
        
        # Calculate the angle
        angle = average * SENSITIVITY + OFFSET + (gameDifference if API is not None else 0)
        angle = np.clip(angle, -MAX_ANGLE, MAX_ANGLE)
    else:
        angle = steeringValues[-1].value + OFFSET + (gameDifference if API is not None else 0)
        angle = np.clip(angle, -MAX_ANGLE, MAX_ANGLE)
    
    return angle

def DrawSteeringLine(ShowImage, value, angle, drawText:bool = True):
    output_img = np.zeros((ShowImage.LAST_HEIGHT, ShowImage.LAST_WIDTH, 3), np.uint8)
    
    w = output_img.shape[1]
    h = output_img.shape[0]
    
    currentDesired = value * (1/MAX_ANGLE)
    actualSteering = angle

    divider = 5
    # First draw a gray line to indicate the background
    cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
    # Then draw a light green line to indicate the actual steering
    cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + actualSteering * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)
    # Then draw a light red line to indicate the desired steering
    cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + (currentDesired if abs(currentDesired) < 1 else (1 if currentDesired > 0 else -1)) * (w/2 - w/divider)), int(h - h/10)), (0, 100, 255), 2, cv2.LINE_AA)
    
    if drawText:
        # Draw the current value as text at the end of the green line
        text, fontscale, thickness, text_width, text_height = get_text_size(f"{actualSteering:.2f}", width=w, height=h, text_width=w, max_text_height=h/20)
        cv2.putText(output_img, f"{text}", (int(w/2 + actualSteering * (w/2 - w/divider) - text_width/2), int(h - h/10 - text_height * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 178, 70), thickness, cv2.LINE_AA)
        # Draw the desired value as text at the end of the red line
        text, fontscale, thickness, text_width, text_height = get_text_size(f"{currentDesired:.2f}", width=w, height=h, text_width=w, max_text_height=h/20)
        cv2.putText(output_img, f"{text}", (int(w/2 + (currentDesired if abs(currentDesired) < 1 else (1 if currentDesired > 0 else -1)) * (w/2 - w/divider) - text_width/2), int(h - h/10 + text_height * 1.7)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 70, 178), thickness, cv2.LINE_AA)

    ShowImage.overlays["SteeringLine"] = output_img

def run(value:float = None, sendToGame:bool = True, drawLine:bool = True, drawText:bool = True):
    global SDK
    global gameDifference
    global gameSteering
    # Add the newest value to the list
    if value is not None:
        steeringValues.append(SteeringValue(value, time.time()))
    else:
        steeringValues.append(SteeringValue(0, time.time())) # Slowly return to 0 naturally
    
    if API is not None:
        data = API.run()
        if data != "not connected" and data != "error checking API status":
            gameSteering = -data["truckFloat"]["gameSteer"]
            gameDifference = value - gameSteering
            gameDifference = gameDifference * 10
        else:
            gameDifference = 0
    else:    
        gameDifference = 0
    
    # Remove all values that are older than SMOOTH_TIME
    while steeringValues[0].IsOlderThan(time.time() - SMOOTH_TIME):
        steeringValues.pop(0)
        
    # Calculate the steering angle
    angle = CalculateSteeringAngle()
    
    # Send the angle to the game
    if sendToGame and SDK is not None:
        # Check that angle is not None
        SDK.steering = float(angle)
    if not sendToGame and SDK is not None:
        SDK.steering = float(0)
        
    # Draw the steering line
    if drawLine:
        try: 
            SI = runner.modules.ShowImage
        except:
            logging.warning("DefaultSteering: ShowImage module not available, please add it to the plugin.json file or disable the drawLine parameter.")
            return "ShowImage module not available, please add it to the plugin.json file or disable the drawLine parameter."
        DrawSteeringLine(SI, value, angle, drawText)
    
    return angle
    