from plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="NavigationDetection",
    description="Uses the navigation line in the minimap.",
    version="3.1",
    author="Glas42",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic",
    dynamicOrder="lane detection",
    exclusive="LaneDetection",
    requires=["DefaultSteering", "bettercamScreenCapture", "TruckSimAPI", "SDKController"]
)

from src.mainUI import switchSelectedPlugin
from src.server import SendCrashReport
from src.translator import Translate
from src.mainUI import resizeWindow
import src.variables as variables
import src.settings as settings
import src.controls as controls
import src.console as console
import src.helpers as helpers
import src.pytorch as pytorch
from src.logger import print
import src.sounds as sounds
from tkinter import ttk
import tkinter as tk

import plugins.DefaultSteering.main as DefaultSteering
import subprocess
import threading
import traceback
import ctypes
import time
import cv2
import os

try:
    from torchvision import transforms
    from bs4 import BeautifulSoup
    import requests
    import torch
    TorchAvailable = True
except:
    TorchAvailable = False
    exc = traceback.format_exc()
    #SendCrashReport("NavigationDetection - PyTorch import error.", str(exc))
    print("\033[91m" + f"NavigationDetection - PyTorch import Error:\n" + "\033[0m" + str(exc))
    pytorch.CheckPyTorch()
    console.RestoreConsole()
    
try:
    import numpy as np
    # Check if numpy is under V2.0.0
    if int(np.__version__.split(".")[0]) >= 2:
        raise Exception("Numpy version is too high.")
except:
    console.RestoreConsole()
    exc = traceback.format_exc()
    print("\033[91m" + f"NavigationDetection - Numpy import Error:\n" + "\033[0m" + str(exc))
    
    # Download numpy 1.26.4
    try:
        path = os.path.dirname(os.path.dirname(variables.PATH)) + "/"
        subprocess.run("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip uninstall numpy", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install numpy==1.26.4 --force-reinstall", shell=True, stdout=subprocess.DEVNULL)
        print("\033[92m" + "Numpy has been updated." + "\033[0m")
    except Exception as ex:
        SendCrashReport("NavigationDetection - Numpy update error.", str(exc))
        print("\033[91m" + "Failed to update numpy: " + "\033[0m" + str(ex))
    
    import numpy as np
    


controls.RegisterKeybind("Lane change to the left",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")

controls.RegisterKeybind("Lane change to the right",
                         notBoundInfo="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.",
                         description="Bind this if you dont want to use the indicators\nto change lanes with the NavigationDetection.")


############################################################################################################################    
# Settings
############################################################################################################################
def LoadSettings():
    global UseAI
    global UseCUDA
    global AIDevice
    global LoadAILabel
    global LoadAIProgress

    global map_topleft
    global map_bottomright
    global arrow_topleft
    global arrow_bottomright

    global arrow_percentage

    global navigationsymbol_x
    global navigationsymbol_y

    global offset

    global trafficlightdetection_is_enabled
    global lefthand_traffic

    global fuel_update_timer
    global fuel_total
    global fuel_current
    global fuel_percentage

    global check_map_timer
    global do_zoom
    global do_blocked
    global mod_enabled
    global allow_playsound
    global allow_playsound_timer

    global controls_last_left
    global controls_last_right

    global left_x_lane
    global right_x_lane
    global left_x_turn
    global right_x_turn
    global left_x_turndrive
    global right_x_turndrive
    global approve_upper_y_left
    global approve_lower_y_left
    global approve_upper_y_right
    global approve_lower_y_right
    
    global detection_offset_lane_y

    global turnincoming_detected
    global turnincoming_direction
    global turnincoming_last_detected

    global indicator_last_left
    global indicator_last_right
    global indicator_left_wait_for_response
    global indicator_right_wait_for_response
    global indicator_left_response_timer
    global indicator_right_response_timer
    global indicator_enable_left
    global indicator_enable_right
    global indicator_changed_by_code

    global lanechanging_do_lane_changing
    global lanechanging_speed
    global lanechanging_width
    global lanechanging_autolanezero
    global lanechanging_current_lane
    global lanechanging_final_offset

    if 'UseAI' in globals():
        if UseAI == False and settings.GetSettings("NavigationDetection", "UseAI", False) == True:
            if TorchAvailable == True:
                helpers.RunInMainThread(LoadAIModel)
            else:
                print("NavigationDetectionAI not available due to missing dependencies.")
                console.RestoreConsole()
    UseAI = settings.GetSettings("NavigationDetection", "UseAI", False)
    UseCUDA = settings.GetSettings("NavigationDetection", "UseCUDA", False)
    AIDevice = torch.device('cuda' if torch.cuda.is_available() and UseCUDA == True else 'cpu') if TorchAvailable else None
    LoadAILabel = "Loading..."
    LoadAIProgress = 0

    map_topleft = settings.GetSettings("NavigationDetection", "map_topleft", "unset")
    map_bottomright = settings.GetSettings("NavigationDetection", "map_bottomright", "unset")
    arrow_topleft = settings.GetSettings("NavigationDetection", "arrow_topleft", "unset")
    arrow_bottomright = settings.GetSettings("NavigationDetection", "arrow_bottomright", "unset")
    arrow_percentage = settings.GetSettings("NavigationDetection", "arrow_percentage", "unset")

    if map_topleft == "unset":
        map_topleft = None
    if map_bottomright == "unset":
        map_bottomright = None
    if arrow_topleft == "unset":
        arrow_topleft = None
    if arrow_bottomright == "unset":
        arrow_bottomright = None
    if arrow_percentage == "unset":
        arrow_percentage = None
    
    if arrow_topleft != None and arrow_bottomright != None and map_topleft != None and map_bottomright != None:
        navigationsymbol_x = round((arrow_topleft[0] + arrow_bottomright[0]) / 2 - map_topleft[0])
        navigationsymbol_y = round((arrow_topleft[1] + arrow_bottomright[1]) / 2 - map_topleft[1])
    else:
        navigationsymbol_x = 0
        navigationsymbol_y = 0

    offset = settings.GetSettings("NavigationDetection", "offset", 0)

    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled", []):
        trafficlightdetection_is_enabled = True
    else:
        trafficlightdetection_is_enabled = False

    lefthand_traffic = settings.GetSettings("NavigationDetection", "lefthand_traffic", False)

    fuel_update_timer = 0
    fuel_total = 0
    fuel_current = 0
    fuel_percentage = 100

    check_map_timer = 0
    do_zoom = False
    do_blocked = False
    mod_enabled = False
    allow_playsound = False
    allow_playsound_timer = time.time()

    controls_last_left = False
    controls_last_right = False

    left_x_lane = 0
    right_x_lane = 0
    left_x_turn = 0
    right_x_turn = 0
    left_x_turndrive = 0
    right_x_turndrive = 0
    approve_upper_y_left = 0
    approve_lower_y_left = 0
    approve_upper_y_right = 0
    approve_lower_y_right = 0

    detection_offset_lane_y = 0

    turnincoming_detected = False
    turnincoming_direction = None
    turnincoming_last_detected = 0

    indicator_last_left = False
    indicator_last_right = False
    indicator_left_wait_for_response = False
    indicator_right_wait_for_response = False
    indicator_left_response_timer = 0
    indicator_right_response_timer = 0
    indicator_enable_left = False
    indicator_enable_right = False
    indicator_changed_by_code = True

    lanechanging_do_lane_changing = settings.GetSettings("NavigationDetection", "lanechanging_do_lane_changing", True)
    lanechanging_speed = settings.GetSettings("NavigationDetection", "lanechanging_speed", 1)
    lanechanging_width = settings.GetSettings("NavigationDetection", "lanechanging_width", 10)
    lanechanging_autolanezero = settings.GetSettings("NavigationDetection", "lanechanging_autolanezero", True)
    lanechanging_current_lane = 0
    lanechanging_final_offset = 0
LoadSettings()


def get_text_size(text="NONE", text_width=100, max_text_height=100):
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


def preprocess_image(image):
    image = np.array(image)
    image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
    image = np.array(image, dtype=np.float32) / 255.0
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    return transform(image).unsqueeze(0).to(AIDevice)


def HandleCorruptedAIModel():
    DeleteAllAIModels()
    CheckForAIModelUpdates()
    while AIModelUpdateThread.is_alive(): time.sleep(0.1)
    time.sleep(0.5)
    if TorchAvailable == True:
        helpers.RunInMainThread(LoadAIModel)
    else:
        print("NavigationDetectionAI not available due to missing dependencies.")
        console.RestoreConsole()


def LoadAIModel():
    try:
        def LoadAIModelThread():
            try:
                global LoadAILabel
                global LoadAIProgress
                global AIModel
                global AIModelLoaded

                CheckForAIModelUpdates()
                while AIModelUpdateThread.is_alive(): time.sleep(0.1)

                if GetAIModelName() == "UNKNOWN":
                    return

                LoadAIProgress = 0
                LoadAILabel = "Loading the AI model..."

                print("\033[92m" + f"Loading the AI model..." + "\033[0m")

                GetAIModelProperties()

                ModelFileCorrupted = False

                try:
                    AIModel = torch.jit.load(os.path.join(f"{variables.PATH}plugins/NavigationDetection/AIModel", GetAIModelName()), map_location=AIDevice)
                    AIModel.eval()
                except:
                    ModelFileCorrupted = True

                if ModelFileCorrupted == False:
                    print("\033[92m" + f"Successfully loaded the AI model!" + "\033[0m")
                    AIModelLoaded = True
                    LoadAIProgress = 100
                    LoadAILabel = "Successfully loaded the AI model!"
                else:
                    print("\033[91m" + f"Failed to load the AI model because the model file is corrupted." + "\033[0m")
                    AIModelLoaded = False
                    LoadAIProgress = 0
                    LoadAILabel = "ERROR! Your AI model file is corrupted!"
                    time.sleep(3)
                    HandleCorruptedAIModel()
            except Exception as e:
                exc = traceback.format_exc()
                SendCrashReport("NavigationDetection - Loading AI Error.", str(exc))
                console.RestoreConsole()
                print("\033[91m" + f"Failed to load the AI model." + "\033[0m")
                AIModelLoaded = False
                LoadAIProgress = 0
                LoadAILabel = "Failed to load the AI model!"

        global AIModelLoadThread
        AIModelLoadThread = threading.Thread(target=LoadAIModelThread)
        AIModelLoadThread.start()

    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function LoadAIModel.", str(exc))
        print(f"NavigationDetection - Error in function LoadAIModel: {ex}")
        console.RestoreConsole()
        print("\033[91m" + f"Failed to load the AI model." + "\033[0m")


def CheckForAIModelUpdates():
    try:
        def CheckForAIModelUpdatesThread():
            try:
                global LoadAILabel
                global LoadAIProgress

                try:
                    response = requests.get("https://huggingface.co/", timeout=3)
                    response = response.status_code
                except requests.exceptions.RequestException as ex:
                    response = None

                if response == 200:
                    LoadAIProgress = 0
                    LoadAILabel = "Checking for AI model updates..."

                    print("\033[92m" + f"Checking for AI model updates..." + "\033[0m")

                    url = "https://huggingface.co/Glas42/NavigationDetectionAI/tree/main/model"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/Glas42/NavigationDetectionAI/blob/main/model'):
                            LatestAIModel = href.split("/")[-1]
                            break

                    CurrentAIModel = GetAIModelName()
                    if CurrentAIModel == "UNKNOWN":
                        CurrentAIModel = None

                    if str(LatestAIModel) != str(CurrentAIModel):
                        LoadAILabel = "Updating AI model..."
                        print("\033[92m" + f"Updating AI model..." + "\033[0m")
                        DeleteAllAIModels()
                        response = requests.get(f"https://huggingface.co/Glas42/NavigationDetectionAI/resolve/main/model/{LatestAIModel}?download=true", stream=True)
                        last_progress = 0
                        with open(os.path.join(f"{variables.PATH}plugins/NavigationDetection/AIModel", f"{LatestAIModel}"), "wb") as modelfile:
                            total_size = int(response.headers.get('content-length', 0))
                            downloaded_size = 0
                            chunk_size = 1024
                            for data in response.iter_content(chunk_size=chunk_size):
                                downloaded_size += len(data)
                                modelfile.write(data)
                                progress = (downloaded_size / total_size) * 100
                                if round(last_progress) < round(progress):
                                    progress_mb = downloaded_size / (1024 * 1024)
                                    total_size_mb = total_size / (1024 * 1024)
                                    LoadAIProgress = progress
                                    LoadAILabel = f"Downloading AI model: {round(progress)}%"
                                    last_progress = progress
                        LoadAIProgress = 100
                        LoadAILabel = "Successfully updated AI model!"
                        print("\033[92m" + f"Successfully updated AI model!" + "\033[0m")
                    else:
                        LoadAIProgress = 100
                        LoadAILabel = "No AI model updates available!"
                        print("\033[92m" + f"No AI model updates available!" + "\033[0m")

                else:

                    console.RestoreConsole()
                    print("\033[91m" + f"Connection to https://huggingface.co/ is most likely not available in your country. Unable to check for AI model updates." + "\033[0m")
                    LoadAIProgress = 0
                    LoadAILabel = "Connection to https://huggingface.co/ is\nmost likely not available in your country.\nUnable to check for AI model updates."

            except Exception as ex:
                exc = traceback.format_exc()
                SendCrashReport("NavigationDetection - Error in function CheckForAIModelUpdatesThread.", str(exc))
                print(f"NavigationDetection - Error in function CheckForAIModelUpdatesThread: {ex}")
                console.RestoreConsole()
                print("\033[91m" + f"Failed to check for AI model updates or update the AI model." + "\033[0m")
                LoadAIProgress = 0
                LoadAILabel = "Failed to check for AI model updates or update the AI model."

        global AIModelUpdateThread
        AIModelUpdateThread = threading.Thread(target=CheckForAIModelUpdatesThread)
        AIModelUpdateThread.start()

    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function CheckForAIModelUpdates.", str(exc))
        print(f"NavigationDetection - Error in function CheckForAIModelUpdates: {ex}")
        console.RestoreConsole()
        print("\033[91m" + f"Failed to check for AI model updates or update the AI model." + "\033[0m")


def ModelFolderExists():
    try:
        if os.path.exists(f"{variables.PATH}plugins/NavigationDetection/AIModel") == False:
            os.makedirs(f"{variables.PATH}plugins/NavigationDetection/AIModel")
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function ModelFolderExists.", str(exc))
        print(f"NavigationDetection - Error in function ModelFolderExists: {ex}")
        console.RestoreConsole()


def GetAIModelName():
    try:
        ModelFolderExists()
        for file in os.listdir(f"{variables.PATH}plugins/NavigationDetection/AIModel"):
            if file.endswith(".pt"):
                return file
        return "UNKNOWN"
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function GetAIModelName.", str(exc))
        print(f"NavigationDetection - Error in function GetAIModelName: {ex}")
        console.RestoreConsole()
        return "UNKNOWN"


def DeleteAllAIModels():
    try:
        ModelFolderExists()
        for file in os.listdir(f"{variables.PATH}plugins/NavigationDetection/AIModel"):
            if file.endswith(".pt"):
                os.remove(os.path.join(f"{variables.PATH}plugins/NavigationDetection/AIModel", file))
    except PermissionError as ex:
        global TorchAvailable
        TorchAvailable = False
        settings.CreateSettings("NavigationDetection", "UseAI", False)
        print(f"NavigationDetection - PermissionError in function DeleteAllAIModels: {ex}")
        print("NavigationDetectionAI will be automatically disabled because the code cannot delete the AI model.")
        console.RestoreConsole()
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function DeleteAllAIModels.", str(exc))
        print(f"NavigationDetection - Error in function DeleteAllAIModels: {ex}")
        console.RestoreConsole()


def GetAIModelProperties():
    global MODEL_METADATA
    global IMG_WIDTH
    global IMG_HEIGHT
    global IMG_CHANNELS
    global MODEL_EPOCHS
    global MODEL_BATCH_SIZE
    global MODEL_IMAGE_COUNT
    global MODEL_TRAINING_TIME
    global MODEL_TRAINING_DATE
    try:
        ModelFolderExists()
        MODEL_METADATA = {"data": []}
        IMG_WIDTH = "UNKNOWN"
        IMG_HEIGHT = "UNKNOWN"
        IMG_CHANNELS = "UNKNOWN"
        MODEL_EPOCHS = "UNKNOWN"
        MODEL_BATCH_SIZE = "UNKNOWN"
        MODEL_IMAGE_COUNT = "UNKNOWN"
        MODEL_TRAINING_TIME = "UNKNOWN"
        MODEL_TRAINING_DATE = "UNKNOWN"
        if GetAIModelName() == "UNKNOWN" or TorchAvailable == False:
            return
        torch.jit.load(os.path.join(f"{variables.PATH}plugins/NavigationDetection/AIModel", GetAIModelName()), _extra_files=MODEL_METADATA, map_location=AIDevice)
        MODEL_METADATA = str(MODEL_METADATA["data"]).replace('b"(', '').replace(')"', '').replace("'", "").split(", ")
        for var in MODEL_METADATA:
            if "image_width" in var:
                IMG_WIDTH = int(var.split("#")[1])
            if "image_height" in var:
                IMG_HEIGHT = int(var.split("#")[1])
            if "image_channels" in var:
                IMG_CHANNELS = str(var.split("#")[1])
            if "epochs" in var:
                MODEL_EPOCHS = int(var.split("#")[1])
            if "batch" in var:
                MODEL_BATCH_SIZE = int(var.split("#")[1])
            if "image_count" in var:
                MODEL_IMAGE_COUNT = int(var.split("#")[1])
            if "training_time" in var:
                MODEL_TRAINING_TIME = var.split("#")[1]
            if "training_date" in var:
                MODEL_TRAINING_DATE = var.split("#")[1]
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("NavigationDetection - Error in function GetAIModelProperties.", str(exc))
        print(f"NavigationDetection - Error in function GetAIModelProperties: {ex}")
        console.RestoreConsole()


if UseAI:
    if TorchAvailable == True and settings.GetSettings("NavigationDetection", "UseAI", False) == True:
        helpers.RunInMainThread(LoadAIModel)
    else:
        print("NavigationDetectionAI not available due to missing dependencies.")
        console.RestoreConsole()


############################################################################################################################
# Code
############################################################################################################################
def plugin(data):
    global indicator_last_left
    global indicator_last_right
    global indicator_left_wait_for_response
    global indicator_right_wait_for_response
    global indicator_left_response_timer
    global indicator_right_response_timer

    current_time = time.time()

    if UseAI == False or TorchAvailable == False:
        global map_topleft
        global map_bottomright
        global arrow_topleft
        global arrow_bottomright

        global arrow_percentage

        global navigationsymbol_x
        global navigationsymbol_y

        global offset

        global trafficlightdetection_is_enabled
        global lefthand_traffic

        global fuel_update_timer
        global fuel_total
        global fuel_current
        global fuel_percentage

        global check_map_timer
        global do_zoom
        global do_blocked
        global mod_enabled
        global allow_playsound
        global allow_playsound_timer

        global controls_last_left
        global controls_last_right

        global left_x_lane
        global right_x_lane
        global left_x_turn
        global right_x_turn
        global left_x_turndrive
        global right_x_turndrive
        global approve_upper_y_left
        global approve_lower_y_left
        global approve_upper_y_right
        global approve_lower_y_right
        
        global detection_offset_lane_y

        global turnincoming_detected
        global turnincoming_direction
        global turnincoming_last_detected

        global indicator_enable_left
        global indicator_enable_right
        global indicator_changed_by_code

        global lanechanging_do_lane_changing
        global lanechanging_speed
        global lanechanging_width
        global lanechanging_autolanezero
        global lanechanging_current_lane
        global lanechanging_final_offset

        try:
            frame = data["frame"]
            width = frame.shape[1]
            height = frame.shape[0]
        except:
            return data

        if frame is None: return data
        if width == 0 or width == None: return data
        if height == 0 or height == None: return data
        
        if isinstance(frame, np.ndarray) and frame.ndim == 3 and frame.size > 0:
            valid_frame = True
        else:
            valid_frame = False
            return data

        if map_topleft != None and map_bottomright != None and arrow_topleft != None and arrow_bottomright != None:
            if (0 <= map_topleft[0] < arrow_topleft[0] < arrow_bottomright[0] < map_bottomright[0] < data["frameFull"].shape[1]) and (0 <= map_topleft[1] < arrow_topleft[1] < arrow_bottomright[1] < map_bottomright[1] < data["frameFull"].shape[0]):
                valid_setup = True
            else:
                valid_setup = False
        else:
            valid_setup = False
        
        if valid_setup == False:
            print("NavigationDetection: Invalid frame or setup. Possible fix: Set the screen capture to your main monitor in your Screen Capture Plugin.")
            console.RestoreConsole()

        try:
            gamepaused = data["api"]["pause"]
            if gamepaused == True:
                speed = 0
            else:
                speed = round(data["api"]["truckFloat"]["speed"]*3.6, 2)
        except:
            gamepaused = False
            speed = 0

        if current_time > fuel_update_timer + 5:
            fuel_update_timer = current_time
            try:
                fuel_total = data["api"]["configFloat"]["fuelCapacity"]
                fuel_current = data["api"]["truckFloat"]["fuel"]
                if fuel_total != 0:
                    fuel_percentage = (fuel_current/fuel_total)*100
                else:
                    fuel_percentage = 100
            except:
                fuel_total = 0
                fuel_current = 0
                fuel_percentage = 100

        try:
            indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
            indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
        except:
            indicator_left = False
            indicator_right = False

        if trafficlightdetection_is_enabled == True:
            try:
                trafficlight = data["TrafficLightDetection"]["simple"]
            except:
                trafficlight = None
                if "TrafficLightDetection" not in settings.GetSettings("Plugins", "Enabled", []):
                    trafficlightdetection_is_enabled = False
                    trafficlight = "Off"
        else:
            trafficlight = "Off"

        f5_key_state = ctypes.windll.user32.GetAsyncKeyState(0x74)
        f5_pressed = f5_key_state & 0x8000 != 0
        
        if f5_pressed == True or do_blocked == True or do_zoom == True:
            check_map_timer = current_time
        
        if current_time - 1 < check_map_timer or check_map_timer == 0:
            check_map = True
        else:
            check_map = False

        if check_map == True:
            if map_topleft != None and map_bottomright != None and arrow_topleft != None and arrow_bottomright != None and map_topleft[0] < map_bottomright[0] and map_topleft[1] < map_bottomright[1] and arrow_topleft[0] < arrow_bottomright[0] and arrow_topleft[1] < arrow_bottomright[1]:
                lower_blue = np.array([120, 65, 0])
                upper_blue = np.array([255, 200, 110])
                mask_blue = cv2.inRange(frame[arrow_topleft[1] - map_topleft[1]:arrow_bottomright[1] - map_bottomright[1], arrow_topleft[0] - map_topleft[0]:arrow_bottomright[0] - map_bottomright[0]], lower_blue, upper_blue)
                arrow_height, arrow_width = mask_blue.shape[:2]
                pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)
            else:
                pixel_ratio = 0

            if arrow_percentage != None:
                if pixel_ratio > arrow_percentage * 0.85 and pixel_ratio < arrow_percentage * 1.15:
                    do_zoom = False
                else:
                    do_zoom = True
                if pixel_ratio < 0.01:
                    do_blocked = True
                else:
                    do_blocked = False
            else:
                do_zoom = False
                do_blocked = False
            if check_map_timer == 0:
                check_map_timer = current_time
            
            lower_green = np.array([0, 200, 0])
            upper_green = np.array([230, 255, 150])
            mask_green = cv2.inRange(frame, lower_green, upper_green)
            if cv2.countNonZero(mask_green) > 0:
                mod_enabled = False
            else:
                mod_enabled = True

        if mod_enabled == False:
            lower_red = np.array([0, 0, 160])
            upper_red = np.array([110, 110, 255])
            lower_green = np.array([0, 200, 0])
            upper_green = np.array([230, 255, 150])
            white_limit = 1

            mask_red = cv2.inRange(frame, lower_red, upper_red)
            mask_green = cv2.inRange(frame, lower_green, upper_green)

            frame_with_mask = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
        else:
            lower_red = np.array([0, 0, 160])
            upper_red = np.array([110, 110, 255])
            white_limit = 1

            mask_red = cv2.inRange(frame, lower_red, upper_red)

            frame_with_mask = cv2.bitwise_and(frame, frame, mask=mask_red)

        cv2.rectangle(frame_with_mask, (0,0), (round(width/6),round(height/3)),(0,0,0),-1)
        cv2.rectangle(frame_with_mask, (width,0), (round(width-width/6),round(height/3)),(0,0,0),-1)

        frame_gray = cv2.cvtColor(frame_with_mask, cv2.COLOR_BGR2GRAY)
        frame_gray_unblurred = frame_gray.copy()

        frame_gray = cv2.GaussianBlur(frame_gray,(3,3),0)

        frame = cv2.cvtColor(frame_gray_unblurred, cv2.COLOR_BGR2RGB)
        
        y_coordinate_of_lane = round(navigationsymbol_y / 1.3)
        y_coordinate_of_turn = round(navigationsymbol_y / 4) 
        automatic_x_offset = round(width/2-navigationsymbol_y)

        def GetArrayOfLaneEdges(y_coordinate_of_detection, tilt, x_offset, y_offset):
            detectingLane = False
            laneEdges = []

            for x in range(0, int(width)):
                
                y = round(y_coordinate_of_detection + y_offset + (navigationsymbol_x - x + x_offset) * tilt)
                if y < 0:
                    y = 0
                if y > height - 1:
                    y = height - 1

                pixel = frame_gray[y, x]
                if (white_limit <= pixel):
                    
                    if not detectingLane:
                        detectingLane = True
                        laneEdges.append(x - x_offset)
                else:
                    if detectingLane:
                        detectingLane = False
                        laneEdges.append(x - x_offset)

            if len(laneEdges) < 2:
                laneEdges.append(width)

            return laneEdges
        
        
        if turnincoming_direction != None:
            if turnincoming_direction == "Left":
                tilt = 0.25
            else:
                tilt = -0.25
        else:
            tilt = 0
        x_offset = lanechanging_final_offset - offset
        y_offset = detection_offset_lane_y
        lanes = GetArrayOfLaneEdges(y_coordinate_of_lane, tilt, x_offset, y_offset)
        try:
            closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
            left_x_lane, right_x_lane = closest_x_pair
        except:
            if lefthand_traffic == False:
                left_x_lane = lanes[len(lanes)-2]
                right_x_lane = lanes[len(lanes)-1]
            else:
                try:
                    left_x_lane = lanes[len(lanes)-4]
                    right_x_lane = lanes[len(lanes)-3]
                except:
                    left_x_lane = lanes[len(lanes)-2]
                    right_x_lane = lanes[len(lanes)-1]
        
        left_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - left_x_lane - x_offset) * tilt)
        right_y_lane = round(y_coordinate_of_lane + detection_offset_lane_y + (navigationsymbol_x - right_x_lane - x_offset) * tilt)

        tilt = 0
        x_offset = lanechanging_final_offset - offset
        y_offset = 0
        lanes = GetArrayOfLaneEdges(y_coordinate_of_turn, tilt, x_offset, y_offset)
        try:
            closest_x_pair = min([(left_x, right_x) for left_x, right_x in zip(lanes[::2], lanes[1::2])], key=lambda pair: abs((pair[0] + pair[1]) / 2 - navigationsymbol_x))
            left_x_turn, right_x_turn = closest_x_pair
        except:
            if lefthand_traffic == False:
                left_x_turn = lanes[len(lanes)-2]
                right_x_turn = lanes[len(lanes)-1]
            else:
                try:
                    left_x_turn = lanes[len(lanes)-4]
                    right_x_turn = lanes[len(lanes)-3]
                except:
                    left_x_turn = lanes[len(lanes)-2]
                    right_x_turn = lanes[len(lanes)-1]

        if left_x_lane + lanechanging_final_offset == width:
            left_x_lane = 0
            left_y_lane = 0
            right_x_lane = 0
            right_y_lane = 0
        if left_x_turn + lanechanging_final_offset == width:
            left_x_turn = 0
            right_x_turn = 0

        width_lane = right_x_lane - left_x_lane
        width_turn = right_x_turn - left_x_turn

        center_x_lane = (left_x_lane + right_x_lane) / 2
        center_x_turn = (left_x_turn + right_x_turn) / 2

        approve_x_left = round(navigationsymbol_x - width/4)
        if approve_x_left >= width:
            approve_x_left = width - 1
        if approve_x_left < 0:
            approve_x_left = 0
        approve_upper_y_left = 0
        approve_lower_y_left = 0
        for y in range(height-1, -1, -1):
            pixel = frame_gray[y, approve_x_left]
            if (white_limit <= pixel):
                if approve_upper_y_left == 0:
                    approve_upper_y_left = y
                    approve_lower_y_left = y
                else:
                    approve_lower_y_left = y
            else:
                if approve_upper_y_left != 0:
                    break

        approve_x_right = round(navigationsymbol_x + width/4)
        if approve_x_right >= width:
            approve_x_right = width - 1
        if approve_x_right < 0:
            approve_x_right = 0
        approve_upper_y_right = 0
        approve_lower_y_right = 0
        for y in range(height-1, -1, -1):
            pixel = frame_gray[y, approve_x_right]
            if (white_limit <= pixel):
                if approve_upper_y_right == 0:
                    approve_upper_y_right = y
                    approve_lower_y_right = y
                else:
                    approve_lower_y_right = y
            else:
                if approve_upper_y_right != 0:
                    break
        
        if approve_lower_y_left != 0 and approve_lower_y_right != 0:
            current_color = (0, 0, 255)
        else:
            current_color = (0, 255, 0)
        if approve_lower_y_left != 0:
            cv2.line(frame, (approve_x_left, approve_upper_y_left), (approve_x_left, approve_lower_y_left), current_color, 2)
        if approve_lower_y_right != 0:
            cv2.line(frame, (approve_x_right, approve_upper_y_right), (approve_x_right, approve_lower_y_right), current_color, 2)

        if approve_upper_y_left != 0 and approve_upper_y_right != 0:
            if approve_lower_y_left + round((approve_lower_y_left - approve_upper_y_left) / 2) <= y_coordinate_of_lane <= approve_upper_y_left - round((approve_lower_y_left - approve_upper_y_left) / 2) or approve_lower_y_right + round((approve_lower_y_right - approve_upper_y_right) / 2) <= y_coordinate_of_lane <= approve_upper_y_right - round((approve_lower_y_right - approve_upper_y_right) / 2):
                if approve_lower_y_left < approve_lower_y_right:
                    distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_left - approve_upper_y_left) / 2) - y_coordinate_of_lane
                else:
                    distance = round((approve_lower_y_left + approve_lower_y_right) / 2 + (approve_lower_y_right - approve_upper_y_right) / 2) - y_coordinate_of_lane
                if distance < 0:
                    detection_offset_lane_y = distance
                else:
                    detection_offset_lane_y = 0
            else:
                detection_offset_lane_y = 0
        else:
            detection_offset_lane_y = 0

        if width_turn == 0:
            if approve_upper_y_left != 0:
                turnincoming_detected = True
                turnincoming_direction = "Left"
            if approve_upper_y_right != 0:
                turnincoming_detected = True
                turnincoming_direction = "Right"
        else:
            turnincoming_detected = False
            turnincoming_direction = None

        if approve_upper_y_left != 0 and approve_upper_y_right != 0:
            turnincoming_detected = False
            turnincoming_direction = None

        if approve_upper_y_left == 0 and approve_upper_y_right == 0:
            turnincoming_detected = False
            turnincoming_direction = None

        if turnincoming_detected == True:
            turnincoming_last_detected = current_time
            if lanechanging_autolanezero == True:
                lanechanging_current_lane = 0
        
        if DefaultSteering.enabled == True:
            enabled = True
        else:
            enabled = False
        try:
            data["sdk"]
        except:
            data["sdk"] = {}
        indicator_changed_by_code = False
        if indicator_left != indicator_last_left:
            indicator_left_wait_for_response = False
        if indicator_right != indicator_last_right:
            indicator_right_wait_for_response = False
        if current_time - 1 > indicator_left_response_timer:
            indicator_left_wait_for_response = False
        if current_time - 1 > indicator_right_response_timer:
            indicator_right_wait_for_response = False
        if turnincoming_direction == "Left" and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
            data["sdk"]["LeftBlinker"] = True
            indicator_left_wait_for_response = True
            indicator_left_response_timer = current_time
        if turnincoming_direction == "Right" and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
            data["sdk"]["RightBlinker"] = True
            indicator_right_wait_for_response = True
            indicator_right_response_timer = current_time
        if turnincoming_direction == None and indicator_left == True and indicator_left_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
            data["sdk"]["LeftBlinker"] = True
            indicator_left_wait_for_response = True
            indicator_left_response_timer = current_time
        if turnincoming_direction == None and indicator_right == True and indicator_right_wait_for_response == False and current_time - 2 > turnincoming_last_detected and indicator_changed_by_code == True and enabled == True:
            data["sdk"]["RightBlinker"] = True
            indicator_right_wait_for_response = True
            indicator_right_response_timer = current_time
        if turnincoming_detected == True:
            indicator_changed_by_code = True
        else:
            indicator_changed_by_code = False
        
        try:
            if controls.GetKeybindFromName("Lane change to the left")['buttonIndex'] != -1:
                controls_left_set = True
                controls_left = controls.GetKeybindValue("Lane change to the left")
            else:
                controls_left_set = False
                controls_left = False
        except:
            controls_left_set = False
            controls_left = False
        try:
            if controls.GetKeybindFromName("Lane change to the right")['buttonIndex'] != -1:
                controls_right_set = True
                controls_right = controls.GetKeybindValue("Lane change to the right")
            else:
                controls_right_set = False
                controls_right = False
        except:
            controls_right_set = False
            controls_right = False

        if enabled == True:
            if controls_left_set == False:
                if indicator_left != indicator_last_left and indicator_left == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    lanechanging_current_lane += 1
            else:
                if controls_left == True and controls_last_left == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    if indicator_left == True:
                        lanechanging_current_lane += 1
                    elif indicator_left == False and indicator_right_wait_for_response == False:
                        lanechanging_current_lane += 1
                        indicator_enable_left = True
            if controls_right_set == False:
                if indicator_right != indicator_last_right and indicator_right == True and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    lanechanging_current_lane -= 1
            else:
                if controls_right == True and controls_last_right == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and current_time - 1 > turnincoming_last_detected:
                    if indicator_right == True:
                        lanechanging_current_lane -= 1
                    elif indicator_right == False and indicator_left_wait_for_response == False:
                        lanechanging_current_lane -= 1
                        indicator_enable_right = True

        if indicator_enable_left == True and indicator_left == False and indicator_left_wait_for_response == False and enabled == True:
            data["sdk"]["LeftBlinker"] = True
            indicator_changed_by_code = True
            indicator_left_wait_for_response = True
            indicator_left_response_timer = current_time
        elif indicator_left == True and indicator_left_wait_for_response == False:
            indicator_enable_left = False
        if indicator_enable_right == True and indicator_right == False and indicator_right_wait_for_response == False and enabled == True:
            data["sdk"]["RightBlinker"] = True
            indicator_changed_by_code = True
            indicator_right_wait_for_response = True
            indicator_right_response_timer = current_time
        elif indicator_right == True and indicator_right_wait_for_response == False:
            indicator_enable_right = False

        lanechanging_target_offset = lanechanging_width * lanechanging_current_lane
        lanechanging_current_correction = lanechanging_target_offset - lanechanging_final_offset
        if abs(lanechanging_current_correction) > lanechanging_speed/10:
            if lanechanging_current_correction > 0:
                lanechanging_current_correction = lanechanging_speed/10
            else:
                lanechanging_current_correction = -lanechanging_speed/10
        lanechanging_final_offset += lanechanging_current_correction
        lanechanging_progress = lanechanging_final_offset/lanechanging_width
        
        if lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == False:
            data["sdk"]["LeftBlinker"] = True
            indicator_left_wait_for_response = True
            indicator_left_response_timer = current_time
        elif lanechanging_progress == lanechanging_current_lane and indicator_left == True and indicator_left_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_left_set == True:
            data["sdk"]["LeftBlinker"] = True
            indicator_left_wait_for_response = True
            indicator_left_response_timer = current_time

        if lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == False:
            data["sdk"]["RightBlinker"] = True
            indicator_right_wait_for_response = True
            indicator_right_response_timer = current_time
        elif lanechanging_progress == lanechanging_current_lane and indicator_right == True and indicator_right_wait_for_response == False and indicator_changed_by_code == False and lanechanging_do_lane_changing == True and enabled == True and controls_right_set == True:
            data["sdk"]["RightBlinker"] = True
            indicator_right_wait_for_response = True
            indicator_right_response_timer = current_time

        if width_lane != 0:
            if turnincoming_detected == False:
                correction = navigationsymbol_x - center_x_lane
            else:
                if turnincoming_direction == "Left":
                    correction = navigationsymbol_x - center_x_lane - width_lane/40
                else:
                    correction = navigationsymbol_x - center_x_lane + width_lane/40
        else:
            correction = 0
            if turnincoming_direction == "Left" and enabled == True:
                data["sdk"]["LeftBlinker"] = False
            if turnincoming_direction == "Right" and enabled == True:
                data["sdk"]["RightBlinker"] = False
            turnincoming_detected = False
            turnincoming_direction = None

        map_detected = True
        showing_traffic_light_symbol = False

        if valid_setup == False:
            if allow_playsound == True:
                sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                allow_playsound = False
                allow_playsound_timer = current_time
            frame = cv2.GaussianBlur(frame, (9, 9), 0)
            frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

            cv2.circle(frame, (width//2, int(height/3.5)), height//4, (0, 128, 255), height//50, cv2.LINE_AA)
            cv2.line(frame, (width//2, int(height/3.5)), (width//2, int(height//3.5 + height/8)), (0, 128, 255), height//35, cv2.LINE_AA)
            cv2.circle(frame, (width//2, int(height/3.5 - height/8)), height//50, (0, 128, 255), -1, cv2.LINE_AA)

            text, fontscale, thickness, text_width, text_height = get_text_size(text="Do the Setup", text_width=width/1.1, max_text_height=height/10)
            cv2.putText(frame, text, (int(width/2-text_width/2), int(height/1.45+text_height/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 128, 255), thickness, cv2.LINE_AA)

            correction = 0
            map_detected = False

        elif do_blocked == True:
            if allow_playsound == True:
                sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                allow_playsound = False
                allow_playsound_timer = current_time
            frame = cv2.GaussianBlur(frame, (9, 9), 0)
            frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

            cv2.circle(frame, (width//2, int(height/3.5)), height//4, (0, 128, 255), height//50, cv2.LINE_AA)
            cv2.line(frame, (width//2, int(height/3.5)), (width//2, int(height//3.5 + height/8)), (0, 128, 255), height//35, cv2.LINE_AA)
            cv2.circle(frame, (width//2, int(height/3.5 - height/8)), height//50, (0, 128, 255), -1, cv2.LINE_AA)

            text, fontscale, thickness, text_width, text_height = get_text_size(text="Minimap covered", text_width=width/1.1, max_text_height=height/10)
            cv2.putText(frame, text, (int(width/2-text_width/2), int(height/1.45+text_height/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 128, 255), thickness, cv2.LINE_AA)

            correction = 0
            map_detected = False

        elif do_zoom == True:
            if allow_playsound == True:
                sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                allow_playsound = False
                allow_playsound_timer = current_time
            frame = cv2.GaussianBlur(frame, (9, 9), 0)
            frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

            cv2.circle(frame, (width//2, int(height/3.5)), height//4, (0, 128, 255), height//50, cv2.LINE_AA)
            cv2.line(frame, (width//2, int(height/3.5)), (width//2, int(height//3.5 + height/8)), (0, 128, 255), height//35, cv2.LINE_AA)
            cv2.circle(frame, (width//2, int(height/3.5 - height/8)), height//50, (0, 128, 255), -1, cv2.LINE_AA)

            text, fontscale, thickness, text_width, text_height = get_text_size(text="Zoom Minimap in", text_width=width/1.1, max_text_height=height/10)
            cv2.putText(frame, text, (int(width/2-text_width/2), int(height/1.45+text_height/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 128, 255), thickness, cv2.LINE_AA)

            correction = 0
            map_detected = False

        elif width_lane == 0:
            if allow_playsound == True:
                sounds.PlaysoundFromLocalPath("assets/sounds/info.mp3")
                allow_playsound = False
                allow_playsound_timer = current_time
            frame = cv2.GaussianBlur(frame, (9, 9), 0)
            frame = cv2.addWeighted(frame, 0.5, frame, 0, 0)

            cv2.circle(frame, (width//2, int(height/3.5)), height//4, (0, 128, 255), height//50, cv2.LINE_AA)
            cv2.line(frame, (width//2, int(height/3.5)), (width//2, int(height//3.5 + height/8)), (0, 128, 255), height//35, cv2.LINE_AA)
            cv2.circle(frame, (width//2, int(height/3.5 - height/8)), height//50, (0, 128, 255), -1, cv2.LINE_AA)

            text, fontscale, thickness, text_width, text_height = get_text_size(text="No Lane Detected", text_width=width/1.1, max_text_height=height/10)
            cv2.putText(frame, text, (int(width/2-text_width/2), int(height/1.45+text_height/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 128, 255), thickness, cv2.LINE_AA)

            correction = 0
            map_detected = False

        else:

            if current_time - 1 > allow_playsound_timer:
                allow_playsound = True

            if trafficlightdetection_is_enabled == True:
                if trafficlight == "Red":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] - traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 0, 255), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 255), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True
                if trafficlight == "Yellow":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1]), traffic_light_symbol[2], (0, 255, 255), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 255), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True
                if trafficlight == "Green":
                    traffic_light_symbol = round(width/2), round(height/5), round(width/75)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 0, 0), -1)
                    cv2.circle(frame, (traffic_light_symbol[0], traffic_light_symbol[1] + traffic_light_symbol[2] * 2), traffic_light_symbol[2], (0, 255, 0), -1, cv2.LINE_AA)
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2]), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2]), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2], traffic_light_symbol[1] - traffic_light_symbol[2] * 3), (traffic_light_symbol[0] + traffic_light_symbol[2], traffic_light_symbol[1] + traffic_light_symbol[2] * 3), (150, 150, 150), round(traffic_light_symbol[2]/10))
                    cv2.rectangle(frame, (traffic_light_symbol[0] - traffic_light_symbol[2] * 2, traffic_light_symbol[1] - traffic_light_symbol[2] * 4), (traffic_light_symbol[0] + traffic_light_symbol[2] * 2, traffic_light_symbol[1] + traffic_light_symbol[2] * 4), (0, 255, 0), traffic_light_symbol[2])
                    showing_traffic_light_symbol = True

            if width_lane != 0:
                cv2.line(frame, (round(left_x_lane + lanechanging_final_offset - offset), left_y_lane), (round(right_x_lane + lanechanging_final_offset - offset), right_y_lane),  (255, 255, 255), 2)
            if width_turn != 0 and showing_traffic_light_symbol == False:
                cv2.line(frame, (round(left_x_turn + lanechanging_final_offset - offset), y_coordinate_of_turn), (round(right_x_turn + lanechanging_final_offset - offset), y_coordinate_of_turn), (255, 255, 255), 2)
        
        if lanechanging_do_lane_changing == True or fuel_percentage < 15:
            current_text = "Enabled"
            width_target_current_text = width/4
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text:
                fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            width_enabled_text, height_enabled_text = width_current_text, height_current_text

        if lanechanging_do_lane_changing == True:
            current_text = f"Lane: {lanechanging_current_lane}"
            width_target_current_text = width/4
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text:
                fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            width_lane_text, height_lane_text = width_current_text, height_current_text
            thickness_current_text = round(fontscale_current_text*2)
            if thickness_current_text <= 0:
                thickness_current_text = 1
            if turnincoming_detected == True:
                current_color = (150, 150, 150)
            else:
                current_color = (200, 200, 200)
            cv2.putText(frame, f"Lane: {lanechanging_current_lane}", (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, current_color, thickness_current_text)
        
        if fuel_percentage < 15:
            current_text = "Refuel!"
            width_target_current_text = width/4
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text:
                fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            thickness_current_text = round(fontscale_current_text*2)
            if thickness_current_text <= 0:
                thickness_current_text = 1
            if lanechanging_do_lane_changing == True:
                cv2.putText(frame, current_text, (round(0.01*width), round(0.10*height+height_current_text+height_enabled_text+height_lane_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)
            else:
                cv2.putText(frame, current_text, (round(0.01*width), round(0.07*height+height_current_text+height_enabled_text)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (0, 0, 255), thickness_current_text)

        indicator_last_left = indicator_left
        indicator_last_right = indicator_right
        controls_last_left = controls_left
        controls_last_right = controls_right

        if speed > 63:
            correction *= 63/speed

        if turnincoming_detected == False and width_turn != 0 and width_turn < width_lane:
            curve = (center_x_lane - center_x_turn)/30
        else:
            curve = correction/10
        if gamepaused == True:
            curve = 0

        if width_lane == 0:
            lane_detected = False
            check_map_timer = current_time
        else:
            lane_detected = True

        if speed > -0.5:
            data["LaneDetection"] = {}
            data["LaneDetection"]["difference"] = -correction/30
        else:
            data["LaneDetection"] = {}
            data["LaneDetection"]["difference"] = correction/30
        data["NavigationDetection"] = {}
        data["NavigationDetection"]["lanedetected"] = lane_detected
        data["NavigationDetection"]["mapdetected"] = map_detected
        data["NavigationDetection"]["turnincoming"] = turnincoming_detected
        data["NavigationDetection"]["curve"] = curve
        data["NavigationDetection"]["lane"] = lanechanging_current_lane
        data["NavigationDetection"]["laneoffsetpercent"] = lanechanging_progress
        
        data["frame"] = frame

    else:
        try:
            global IMG_WIDTH
            global IMG_HEIGHT

            try:
                while AIModelUpdateThread.is_alive(): return data
                while AIModelLoadThread.is_alive(): return data
            except:
                return data

            try:
                frame = data["frame"]
                width = frame.shape[1]
                height = frame.shape[0]
            except:
                return data

            if frame is None: return data
            if width == 0 or width == None: return data
            if height == 0 or height == None: return data

            if isinstance(frame, np.ndarray) and frame.ndim == 3 and frame.size > 0:
                valid_frame = True
            else:
                valid_frame = False
                return data

            try:
                gamepaused = data["api"]["pause"]
                if gamepaused == True:
                    speed = 0
                else:
                    speed = round(data["api"]["truckFloat"]["speed"]*3.6, 2)
            except:
                gamepaused = False
                speed = 0

            cv2.rectangle(frame, (0, 0), (round(frame.shape[1]/6), round(frame.shape[0]/3)), (0, 0, 0), -1)
            cv2.rectangle(frame, (frame.shape[1] ,0), (round(frame.shape[1]-frame.shape[1]/6), round(frame.shape[0]/3)), (0, 0, 0), -1)
            lower_red = np.array([0, 0, 160])
            upper_red = np.array([110, 110, 255])
            mask = cv2.inRange(frame, lower_red, upper_red)
            frame_with_mask = cv2.bitwise_and(frame, frame, mask=mask)
            frame = cv2.cvtColor(frame_with_mask, cv2.COLOR_BGR2GRAY)

            if cv2.countNonZero(frame) / (frame.shape[0] * frame.shape[1]) > 0.03:
                lane_detected = True
            else:
                lane_detected = False

            try:
                AIFrame = preprocess_image(mask)
            except:
                GetAIModelProperties()
                if IMG_WIDTH == "UNKNOWN" or IMG_HEIGHT == "UNKNOWN":
                    print(f"NavigationDetection - Unable to read the AI model image size. Make sure you didn't change the model file name. The code wont run the NavigationDetectionAI.")
                    console.RestoreConsole()
                    return data
                AIFrame = preprocess_image(mask)

            output = [[0, 0, 0, 0, 0, 0, 0, 0]]

            if DefaultSteering.enabled == True and gamepaused == False:
                if AIModelLoaded == True:
                    with torch.no_grad():
                        output = AIModel(AIFrame)
                        output = output.tolist()

            steering = float(output[0][0]) / -30
            left_indicator = bool(float(output[0][1]) > 0.15)
            right_indicator = bool(float(output[0][2]) > 0.15)

            if lane_detected == False:
                steering = 0
                left_indicator = False
                right_indicator = False

            try:
                indicator_left = data["api"]["truckBool"]["blinkerLeftActive"]
                indicator_right = data["api"]["truckBool"]["blinkerRightActive"]
            except:
                indicator_left = False
                indicator_right = False

            if DefaultSteering.enabled == True and gamepaused == False:
                try:
                    data["sdk"]
                except:
                    data["sdk"] = {}

                if left_indicator != indicator_left:
                    data["sdk"]["LeftBlinker"] = True
                    indicator_left_wait_for_response = True
                    indicator_left_response_timer = current_time
                if right_indicator != indicator_right:
                    data["sdk"]["RightBlinker"] = True
                    indicator_right_wait_for_response = True
                    indicator_right_response_timer = current_time

                if indicator_left != indicator_last_left:
                    indicator_left_wait_for_response = False
                if indicator_right != indicator_last_right:
                    indicator_right_wait_for_response = False
                if current_time - 1 > indicator_left_response_timer:
                    indicator_left_wait_for_response = False
                if current_time - 1 > indicator_right_response_timer:
                    indicator_right_wait_for_response = False
            indicator_last_left = left_indicator
            indicator_last_right = right_indicator

            data["LaneDetection"] = {}
            if speed > -0.5:
                data["LaneDetection"] = {}
                data["LaneDetection"]["difference"] = steering
            else:
                data["LaneDetection"] = {}
                data["LaneDetection"]["difference"] = -steering

            data["NavigationDetection"] = {}
            data["NavigationDetection"]["lanedetected"] = lane_detected
            data["NavigationDetection"]["mapdetected"] = lane_detected
            data["NavigationDetection"]["turnincoming"] = True if left_indicator == True or right_indicator == True else False

            data["frame"] = frame

        except Exception as e:
            exc = traceback.format_exc()
            SendCrashReport("NavigationDetection - Running AI Error.", str(exc))
            console.RestoreConsole()
            print("\033[91m" + f"NavigationDetection - Running AI Error: " + "\033[0m" + str(e))

    return data


def onEnable():
    pass

def onDisable():
    pass


class UI():
    try:
        def __init__(self, master) -> None:
            self.master = master
            self.exampleFunction()
            resizeWindow(950,600)        

        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def tabFocused(self):
            resizeWindow(950,600)

        def UpdateSettings(self):

            self.UI_offset.set(self.UI_offsetSlider.get())
            self.UI_lanechanging_speed.set(self.UI_lanechanging_speedSlider.get())
            self.UI_lanechanging_width.set(self.UI_lanechanging_widthSlider.get())

            settings.CreateSettings("NavigationDetection", "offset", self.UI_offsetSlider.get())
            settings.CreateSettings("NavigationDetection", "lanechanging_speed", self.UI_lanechanging_speedSlider.get())
            settings.CreateSettings("NavigationDetection", "lanechanging_width", self.UI_lanechanging_widthSlider.get())

            LoadSettings()

        def exampleFunction(self):

            try:
                self.root.destroy()
            except: pass

            self.root = tk.Canvas(self.master, width=950, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(1)
            self.root.pack_propagate(0)

            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)

            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            setupFrame = ttk.Frame(notebook)
            setupFrame.pack()
            advancedFrame = ttk.Frame(notebook)
            advancedFrame.pack()
            navigationdetectionaiFrame = ttk.Frame(notebook)
            navigationdetectionaiFrame.pack()

            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(setupFrame, text=Translate("Setup"))
            notebook.add(advancedFrame, text=Translate("Advanced"))
            notebook.add(navigationdetectionaiFrame, text=Translate("NavigationDetectionAI"))

            self.root.pack(anchor="center", expand=False)
            self.root.update()

            ############################################################################################################################
            # UI
            ############################################################################################################################

            self.UI_offsetSlider = tk.Scale(generalFrame, from_=-20, to=20, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_offsetSlider.set(settings.GetSettings("NavigationDetection", "offset"))
            self.UI_offsetSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.UI_offset = helpers.MakeComboEntry(generalFrame, "Lane Offset", "NavigationDetection", "offset", 2, 0, labelwidth=10, width=8, isFloat=True, sticky="ne")

            helpers.MakeEmptyLine(generalFrame, 3, 0)

            helpers.MakeCheckButton(generalFrame, "Left-hand traffic\n----------------------\nEnable this if you are driving in a country with left-hand traffic.", "NavigationDetection", "lefthand_traffic", 4, 0, width=80, callback=lambda: LoadSettings())

            helpers.MakeEmptyLine(generalFrame, 5, 0)

            helpers.MakeCheckButton(generalFrame, "Lane Changing\n---------------------\nIf enabled, you can change the lane you are driving on using the games indicators\nor the buttons you set in the Controls menu.", "NavigationDetection", "lanechanging_do_lane_changing", 6, 0, width=80, callback=lambda: LoadSettings())

            self.UI_lanechanging_speedSlider = tk.Scale(generalFrame, from_=0.1, to=3, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_lanechanging_speedSlider.set(settings.GetSettings("NavigationDetection", "lanechanging_speed"))
            self.UI_lanechanging_speedSlider.grid(row=7, column=0, padx=10, pady=0, columnspan=2)
            self.UI_lanechanging_speed = helpers.MakeComboEntry(generalFrame, "Lane Changing Speed", "NavigationDetection", "lanechanging_speed", 7, 0, labelwidth=18, width=8, isFloat=True, sticky="ne")

            helpers.MakeLabel(generalFrame, "╚> This slider sets the speed of the lane changing.", 8, 0, sticky="nw")

            self.UI_lanechanging_widthSlider = tk.Scale(generalFrame, from_=1, to=30, resolution=0.1, orient=tk.HORIZONTAL, length=500, command=lambda x: self.UpdateSettings())
            self.UI_lanechanging_widthSlider.set(settings.GetSettings("NavigationDetection", "lanechanging_width"))
            self.UI_lanechanging_widthSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.UI_lanechanging_width = helpers.MakeComboEntry(generalFrame, "Lane Width", "NavigationDetection", "lanechanging_width", 9, 0, labelwidth=18, width=8, isFloat=True, sticky="ne")

            helpers.MakeLabel(generalFrame, "╚> This slider sets how much the truck needs to go left or right to change the lane.", 10, 0, sticky="nw")

            helpers.MakeEmptyLine(generalFrame, 11, 0)

            helpers.MakeButton(generalFrame, "Give feedback, report a bug or suggest a new feature", lambda: switchSelectedPlugin("plugins.Feedback.main"), 12, 0, width=80, sticky="nw")

            helpers.MakeButton(generalFrame, "Open Wiki", lambda: OpenWiki(), 12, 1, width=23, sticky="nw")

            def OpenWiki():
                browser = helpers.Dialog("Wiki","In which brower should the wiki be opened?", ["In-app browser", "External browser"], "In-app browser", "External Browser")
                if browser == "In-app browser":
                    from src.mainUI import closeTabName
                    from plugins.Wiki.main import LoadURL
                    closeTabName("Wiki")
                    LoadURL("https://wiki.ets2la.com/plugins/navigationdetection")
                else:
                    helpers.OpenInBrowser("https://wiki.ets2la.com/plugins/navigationdetection")


            helpers.MakeLabel(setupFrame, "Choose a setup method:", 1, 0, font=("Robot", 12, "bold"), sticky="nw")

            helpers.MakeButton(setupFrame, "Automatic Setup", self.automatic_setup, 2, 0, sticky="nw")

            helpers.MakeLabel(setupFrame, "The automatic setup will search for the minimap on your screen using AI (YOLOv5), it needs to download some\nfiles the first time you run it. Make sure that the minimap is always visible and not blocked by other applications.", 3, 0, sticky="nw")

            helpers.MakeEmptyLine(setupFrame, 4, 0)

            helpers.MakeButton(setupFrame, "Manual Setup", self.manual_setup, 5, 0, sticky="nw")

            helpers.MakeLabel(setupFrame, "The manual setup will take a screenshot of your screen and then ask you to select the minimap and arrow positions.\nYou can take a look at the example image when you don't know what to do. The example image will open in another window.", 6, 0, sticky="nw")


            helpers.MakeCheckButton(advancedFrame, "Automatically change to lane 0 if a turn got detected and lane changing is enabled.\nNote: If disabled, you will be unable to change lanes when detecting a turn.", "NavigationDetection", "lanechanging_autolanezero", 2, 0, width=97, callback=lambda: LoadSettings())

            helpers.MakeLabel(navigationdetectionaiFrame, "NavigationDetectionAI", 1, 0, font=("Robot", 14, "bold"), sticky="nw")

            helpers.MakeLabel(navigationdetectionaiFrame, "A PyTorch AI which drives the truck using images of the route advisor.", 2, 0, sticky="nw")

            helpers.MakeCheckButton(navigationdetectionaiFrame, "Use NavigationDetectionAI instead of NavigationDetection.", "NavigationDetection", "UseAI", 3, 0, width=97, callback=lambda: {LoadSettings(), self.exampleFunction()})

            if UseAI:

                helpers.MakeCheckButton(navigationdetectionaiFrame, f"Try to use your GPU with CUDA instead of your CPU to run the AI.\n(Currently using {str(AIDevice).upper()})", "NavigationDetection", "UseCUDA", 4, 0, width=97, callback=lambda: {LoadSettings(), self.exampleFunction()})

                def InstallCUDAPopup():
                    helpers.Dialog("Warning: CUDA is only available for NVIDIA GPUs!", f"1. Check on https://wikipedia.org/wiki/CUDA#GPUs_supported which CUDA version your GPU supports.\n2. Go to https://pytorch.org/ and copy the download command for the corresponding CUDA version which is compatible with your GPU.\n    (Select Stable, Windows, Pip, Python and the CUDA version you need)\n3. Open your file explorer and go to {os.path.dirname(os.path.dirname(variables.PATH))} and run the activate.bat\n4. Run this command in the terminal which opened after running the activate.bat: 'pip uninstall torch torchvision torchaudio'\n5. After the previous command finished, run the command you copied from the PyTorch website and wait for the installation to finish.\n6. Restart the app and the app should automatically detect CUDA as available and use your GPU for the AI.", ["Exit"], "Exit")

                helpers.MakeButton(navigationdetectionaiFrame, "Install CUDA for GPU support", InstallCUDAPopup, 5, 0, width=30, sticky="nw")

                helpers.MakeLabel(navigationdetectionaiFrame, "Model properties:", 6, 0, font=("Robot", 12, "bold"), sticky="nw")

                GetAIModelProperties()

                helpers.MakeLabel(navigationdetectionaiFrame, f"Epochs: {MODEL_EPOCHS}\nBatch Size: {MODEL_BATCH_SIZE}\nImage Width: {IMG_WIDTH}\nImage Height: {IMG_HEIGHT}\nImages/Data Points: {MODEL_IMAGE_COUNT}\nTraining Time: {MODEL_TRAINING_TIME}\nTraining Date: {MODEL_TRAINING_DATE}", 7, 0, sticky="nw")

                self.progresslabel = helpers.MakeLabel(navigationdetectionaiFrame, "", 9, 0, sticky="nw")

                self.progress = ttk.Progressbar(navigationdetectionaiFrame, orient="horizontal", length=238, mode="determinate")
                self.progress.grid(row=10, column=0, sticky="nw", padx=5, pady=0)

                def UIButtonCheckForModelUpdates():
                    CheckForAIModelUpdates()
                    while AIModelUpdateThread.is_alive(): time.sleep(0.1)
                    if TorchAvailable == True:
                        LoadAIModel()
                    else:
                        print("NavigationDetectionAI not available due to missing dependencies.")
                        console.RestoreConsole()

                helpers.MakeButton(navigationdetectionaiFrame, "Check for AI model updates", UIButtonCheckForModelUpdates, 11, 0, width=30, sticky="nw")

        def save(self):
            LoadSettings()

        def manual_setup(self):
            found_venv = True
            if os.path.exists(f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe") == False:
                print("\033[91m" + "Your installation is missing the venv. This is probably because you didn't install the app using the installer." + "\033[0m")
                found_venv = False
            if os.path.exists(f"{variables.PATH}plugins/NavigationDetection/manual_setup.py") == True:
                if found_venv == True:
                    subprocess.Popen([f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe", os.path.join(variables.PATH, "plugins/NavigationDetection", "manual_setup.py")], shell=True)
                else:
                    print("\033[91m" + "Running the code outside of the venv. You may need to install the requirements manually using this command in a terminal: " + "\033[0m" + "pip install tk numpy mouse opencv-python mss" + "\033[0m")
                    subprocess.Popen(["python", os.path.join(variables.PATH, "plugins", "NavigationDetection", "manual_setup.py")])
            else:
                print("\033[91m" + f"Your installation is missing the manual_setup.py. Download it manually from the GitHub and place it in this path: {variables.PATH}plugins\\NavigationDetection\\manual_setup.py" + "\033[0m")

        def automatic_setup(self):
            found_venv = True
            if os.path.exists(f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe") == False:
                print("\033[91m" + "Your installation is missing the venv. This is probably because you didn't install the app using the installer." + "\033[0m")
                found_venv = False
            if os.path.exists(f"{variables.PATH}plugins/NavigationDetection/automatic_setup.py") == True:
                if found_venv == True:
                    subprocess.Popen([f"{os.path.dirname(os.path.dirname(variables.PATH))}/venv/Scripts/python.exe", os.path.join(variables.PATH, "plugins/NavigationDetection", "automatic_setup.py")], shell=True)
                else:
                    print("\033[91m" + "Running the code outside of the venv. You may need to install the requirements manually using this command in a terminal: " + "\033[0m" + "pip install tk numpy requests mouse opencv-python mss torch" + "\033[0m")
                    subprocess.Popen(["python", os.path.join(variables.PATH, "plugins", "NavigationDetection", "automatic_setup.py")])
            else:
                print("\033[91m" + f"Your installation is missing the automatic_setup.py. Download it manually from the GitHub and place it in this path: {variables.PATH}plugins\\NavigationDetection\\automatic_setup.py" + "\033[0m")

        def update(self, data):
            if UseAI:
                self.progresslabel.set(LoadAILabel)
                self.progress["value"] = LoadAIProgress
            self.root.update()

    except Exception as ex:
        print(ex.args)

# this comment is used to reload the app after finishing the setup - 0