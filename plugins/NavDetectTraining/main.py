
from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="NavDetectTraining",
    description="Will collect data for the navigation detection AI.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic",
    dynamicOrder="lane detection"
)

import numpy as np
import cv2
import src.controls as controls
import time
import os

lower_red = np.array([0, 0, 160])
upper_red = np.array([110, 110, 255])
data_folder = "plugins/NavDetectTraining/data"
enabled = False

lastChangeTime = time.time()
def EnableDisable():
    if lastChangeTime + 0.5 > time.time():
        return
    global enabled
    enabled = not enabled
    
def GetFolderSize(folder):
    total_size = 0
    for path, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    return total_size

controls.RegisterKeybind("Start / Stop Data Capture", callback=EnableDisable, defaultButtonIndex="N")

def onEnable():
    pass

def onDisable():
    pass

# Get the amount of data already in the folder (divide the amount by 2 because there are two files per image)
count = len(os.listdir(data_folder))//2
last = 0
lastCaptureTime = time.time()
size = GetFolderSize(data_folder)/1024/1024 # MB
def plugin(data):
    global last
    global lastCaptureTime
    global count
    global size
    if not enabled:
        return data
    
    try:
        frame = data["frame"]
    except:
        return data
    if type(frame) == type(None):
        return data

    cv2.rectangle(frame, (0,0), (round(frame.shape[1]/6),round(frame.shape[0]/3)),(0,0,0),-1)
    cv2.rectangle(frame, (frame.shape[1],0), (round(frame.shape[1]-frame.shape[1]/6),round(frame.shape[0]/3)),(0,0,0),-1)
    frame = cv2.inRange(frame, lower_red, upper_red)
    userSteering = data["api"]["truckFloat"]["gameSteer"]
    leftBlinker = data["api"]["truckBool"]["blinkerLeftActive"]
    rightBlinker = data["api"]["truckBool"]["blinkerRightActive"]
    throttle = data["api"]["truckFloat"]["gameThrottle"]
    brake = data["api"]["truckFloat"]["gameBrake"]
    speedLimit = data["api"]["truckFloat"]["speedLimit"]
    speed = data["api"]["truckFloat"]["speed"]
    inclination = data["api"]["truckPlacement"]["rotationY"]
    
    
    timestamp = time.time()
    
    # Save the img and steering angles
    if time.time() - lastCaptureTime > 0.5:
        # Check if the image is full of black
        if not np.all(frame == 0):
            cv2.imwrite(f"{data_folder}/{timestamp}.png", frame)
            # Get the filesize
            addSize = os.path.getsize(f"{data_folder}/{timestamp}.png")/1024/1024
            with open(f"{data_folder}/{timestamp}.txt", "w") as f:
                f.write(f"{userSteering},{last},{leftBlinker},{rightBlinker},{throttle},{brake},{speedLimit},{speed},{inclination}")
            # Get the filesize
            addSize += os.path.getsize(f"{data_folder}/{timestamp}.txt")/1024/1024
            last = userSteering
            lastCaptureTime = time.time()
            count += 1
            size += addSize
            
        
    
    # Write information on the frame
    cv2.putText(frame, f"User steering: {userSteering}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Count: {count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Next capture in: {round(0.5 - (time.time() - lastCaptureTime), 2)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Size: {round(size, 2)} MB", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    data["frame"] = frame
    return data