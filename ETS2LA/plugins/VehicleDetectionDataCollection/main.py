from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.modules as modules
import time
import requests
import threading
import base64
import cv2

def Initialize():
    global x1, y1, x2, y2, cooldown, last_capture, server_available, last_server_check, ScreenCapture

    runner:PluginRunner = None
    ScreenCapture = runner.modules.ScreenCapture

    x1 = 1
    y1 = 1
    x2 = 1
    y2 = 1

    cooldown = 5
    last_capture = time.time()
    last_server_check = time.time() + 180
    server_available = "unknown"

Initialize()

def CheckServer():
    try:
        headers = {
            "Content-Type": "application/json"
        }
        r = requests.get("https://api.tumppi066.fi/heartbeat", headers=headers)
        return True
    except:
        return False
    
def SendImage(image):
    global server_available
    global last_server_check
    if last_server_check + 180 < time.time():
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == "unknown":
        server_available = CheckServer()
        last_server_check = time.time()
    if server_available == True:
        try:
            encoded_string = base64.b64encode(cv2.imencode('.png', image)[1]).decode()
            url = "https://api.tumppi066.fi/image/save"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "image": encoded_string,
                "category": "vehicle_detection_images"
            }
            response = requests.post(url, headers=headers, json=data)
            print("Vehicle Detection Data Collection - Image Saved!")
        except:
            server_available = CheckServer()
            last_server_check = time.time()

def plugin():
    global x1, y1, x2, y2, cooldown, last_capture, ScreenCapture
    if last_capture + cooldown < time.time():
        ScreenCapture.monitor_x1 = x1
        ScreenCapture.monitor_y1 = y1
        ScreenCapture.monitor_x2 = x2
        ScreenCapture.monitor_y2 = y2

        frame = ScreenCapture.run(imgtype="cropped")

        threading.Thread(target=SendImage, args=(frame,), daemon=True).start()
        last_capture = time.time()