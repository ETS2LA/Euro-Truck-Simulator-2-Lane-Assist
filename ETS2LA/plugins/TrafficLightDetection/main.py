from ETS2LA.backend.globalServer import SendCrashReport
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.console as console
import ETS2LA.backend.pytorch as pytorch

if variables.OS == "nt":
    from ctypes import windll, byref, sizeof, c_int
    import win32gui, win32con
import numpy as np
import threading
import traceback
import ctypes
import math
import time
import cv2
import mss
import os

runner:PluginRunner = None

try:
    from torchvision import transforms
    from bs4 import BeautifulSoup
    import requests
    import torch
    TorchAvailable = True
except:
    TorchAvailable = False
    exc = traceback.format_exc()
    SendCrashReport("TrafficLightDetection - PyTorch import error.", str(exc))
    print("\033[91m" + f"TrafficLightDetection - PyTorch import Error:\n" + "\033[0m" + str(exc))
    pytorch.CheckPyTorch()
    console.RestoreConsole()

sct = mss.mss()
monitor = sct.monitors[(settings.Get("TrafficLightDetection", ["ScreenCapture", "display"], 0) + 1)]
screen_x = monitor["left"]
screen_y = monitor["top"]
screen_width = monitor["width"]
screen_height = monitor["height"]

lower_red = np.array([200, 0, 0])
upper_red = np.array([255, 110, 110])
lower_green = np.array([0, 200, 0])
upper_green = np.array([150, 255, 230])
lower_yellow = np.array([200, 170, 50])
upper_yellow = np.array([255, 240, 170])

yolo_model = None
yolo_model_loaded = False

last_GetGamePosition = 0, screen_x, screen_y, screen_width, screen_height


def Initialize():
    global TruckSimAPI
    global ScreenCapture

    global UseAI
    global UseCUDA
    global AIDevice
    global LoadAILabel
    global LoadAIProgress

    global min_rect_size
    global max_rect_size
    global width_height_ratio
    global circlepercent
    global maxcircleoffset
    global circleplusoffset
    global circleminusoffset
    global finalwindow
    global grayscalewindow
    global positionestimationwindow
    global anywindowopen
    global detectyellowlight
    global performancemode
    global advancedmode
    global windowscale
    global posestwindowscale
    global godot_data
    global coordinates
    global trafficlights
    global windowwidth
    global windowheight
    global reset_window
    global positionestimation_default_frame
    global positionestimation_topview
    global positionestimation_sideview
    global fov
    global x1
    global y1
    global x2
    global y2

    global rectsizefilter
    global widthheightratiofilter
    global pixelpercentagefilter
    global pixelblobshapefilter
    global urr
    global urg
    global urb
    global lrr
    global lrg
    global lrb
    global uyr
    global uyg
    global uyb
    global lyr
    global lyg
    global lyb
    global ugr
    global ugg
    global ugb
    global lgr
    global lgg
    global lgb
    global lower_red_advanced
    global upper_red_advanced
    global lower_green_advanced
    global upper_green_advanced
    global lower_yellow_advanced
    global upper_yellow_advanced

    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture

    if 'UseAI' in globals():
        if UseAI == False and settings.Get("TrafficLightDetection", "UseAi", True) == True:
            if TorchAvailable == True:
                LoadAIModel()
            else:
                print("TrafficLightDetectionAI not available due to missing dependencies.")
                console.RestoreConsole()
    elif settings.Get("TrafficLightDetection", "UseAi", True) == True:
        if TorchAvailable == True:
            LoadAIModel()
        else:
            print("TrafficLightDetectionAI not available due to missing dependencies.")
            console.RestoreConsole()
    UseAI = settings.Get("TrafficLightDetection", "UseAi", True)
    UseCUDA = settings.Get("TrafficLightDetection", "UseCUDA", False)
    AIDevice = torch.device('cuda' if torch.cuda.is_available() and UseCUDA == True else 'cpu')
    LoadAILabel = "Loading..."
    LoadAIProgress = 0

    finalwindow = settings.Get("TrafficLightDetection", "FinalWindow", True)
    grayscalewindow = settings.Get("TrafficLightDetection", "GrayscaleWindow", False)
    positionestimationwindow = settings.Get("TrafficLightDetection", "PositionEstimationWindow", False)
    detectyellowlight = settings.Get("TrafficLightDetection", "YellowLightDetection", False)
    performancemode = settings.Get("TrafficLightDetection", "PerformanceMode", True)
    advancedmode = settings.Get("TrafficLightDetection", "AdvancedSettings", False)
    windowscale = float(settings.Get("TrafficLightDetection", "WindowScale", 0.5))
    posestwindowscale = float(settings.Get("TrafficLightDetection", "PositionEstimationWindowScale", 0.5))
    x1 = settings.Get("TrafficLightDetection", "x1ofsc", 0)
    y1 = settings.Get("TrafficLightDetection", "y1ofsc", 0)
    x2 = settings.Get("TrafficLightDetection", "x2ofsc", screen_width-1)
    y2 = settings.Get("TrafficLightDetection", "y2ofsc", round(screen_height/1.5)-1)

    if x1 >= x2:
        if screen_width-x1 > screen_width-x2:
            x1 = x2-1
        else:
            x2 = x1+1
    if y1 >= y2:
        if screen_height-y1 > screen_height-y2:
            y1 = y2-1
        else:
            y2 = y1+1

    ScreenCapture.CreateCam(CamSetupDisplay = (settings.Get("TrafficLightDetection", ["ScreenCapture", "display"], 0)))
    ScreenCapture.monitor_x1 = screen_x
    ScreenCapture.monitor_y1 = screen_y
    ScreenCapture.monitor_x2 = screen_x + screen_width
    ScreenCapture.monitor_y2 = screen_y + screen_height

    windowwidth = x2-x1
    windowheight = y2-y1

    rectsizefilter = settings.Get("TrafficLightDetection", "FiltersMinimalTrafficLightSize", True)
    widthheightratiofilter = settings.Get("TrafficLightDetection", "FiltersWidthHeightRatioFilter", True)
    pixelpercentagefilter = settings.Get("TrafficLightDetection", "FiltersPixelPercentageFilter", True)
    pixelblobshapefilter = settings.Get("TrafficLightDetection", "FiltersPixelBlobShapeFilter", True)

    godot_data = []
    coordinates = []
    trafficlights = []

    if positionestimationwindow == True:
        if os.path.exists(variables.PATH + "ETS2LA/assets/TrafficLightDetection/topview.png"):
            positionestimation_topview = cv2.imread(variables.PATH + "ETS2LA/assets/TrafficLightDetection/topview.png")
        if os.path.exists(variables.PATH + "ETS2LA/assets/TrafficLightDetection/sideview.png"):
            positionestimation_sideview = cv2.imread(variables.PATH + "ETS2LA/assets/TrafficLightDetection/sideview.png")
        positionestimation_default_frame = np.zeros((round(((screen_width-1)/2.5)*posestwindowscale), round((screen_width-1)*posestwindowscale), 3), np.uint8)
        pixel_per_meter = 25
        posest_zoom = (positionestimation_default_frame.shape[1] / 300) * pixel_per_meter
        temp = positionestimation_topview.copy()
        posest_x1 = 0.24 * positionestimation_default_frame.shape[1] - posest_zoom / 2
        posest_y1 = positionestimation_default_frame.shape[0] - posest_zoom * (temp.shape[0] / temp.shape[1])
        posest_x2 = 0.24 * positionestimation_default_frame.shape[1] + posest_zoom / 2
        posest_y2 = positionestimation_default_frame.shape[0]
        temp = cv2.resize(temp, ((round(posest_x2) - round(posest_x1)), (round(posest_y2) - round(posest_y1))))
        positionestimation_default_frame[round(posest_y1):round(posest_y2), round(posest_x1):round(posest_x2)] = temp
        temp = positionestimation_sideview.copy()
        posest_x1 = positionestimation_default_frame.shape[1] - posest_zoom
        posest_y1 = 0.7 * positionestimation_default_frame.shape[0] - posest_zoom * (temp.shape[0] / temp.shape[1]) * 0.5
        posest_x2 = positionestimation_default_frame.shape[1]
        posest_y2 = 0.7 * positionestimation_default_frame.shape[0] + posest_zoom * (temp.shape[0] / temp.shape[1]) * 0.5
        temp = cv2.resize(temp, ((round(posest_x2) - round(posest_x1)), (round(posest_y2) - round(posest_y1))))
        positionestimation_default_frame[round(posest_y1):round(posest_y2), round(posest_x1):round(posest_x2)] = temp
        cv2.line(positionestimation_default_frame, (round(positionestimation_default_frame.shape[1]/2), round(0.05*positionestimation_default_frame.shape[0])), (round(positionestimation_default_frame.shape[1]/2), round(0.95*positionestimation_default_frame.shape[0])), (50, 50, 50), round(positionestimation_default_frame.shape[1]/500) if round(positionestimation_default_frame.shape[1]/500) > 1 else 1)

    fov = settings.Get("TrafficLightDetection", "FOV", 80)

    reset_window = True

    if advancedmode == False:
        min_rect_size = 8
        max_rect_size = round(screen_height / 4)
    else:
        min_rect_size = settings.Get("TrafficLightDetection", "FiltersMinimalTrafficLightSize", 8)
        max_rect_size = settings.Get("TrafficLightDetection", "FiltersMaximalTrafficLightSize", round(screen_height / 4))

    width_height_ratio = 0.2
    circlepercent = 0.785
    maxcircleoffset = 0.15
    circleplusoffset = circlepercent + maxcircleoffset
    circleminusoffset = circlepercent - maxcircleoffset

    if min_rect_size < 8:
        min_rect_size = 8

    if finalwindow == True or grayscalewindow == True:
        anywindowopen = True
    else:
        anywindowopen = False

    urr = settings.Get("TrafficLightDetection", "ColorSettings_urr")
    if urr == None or not isinstance(urr, int) or not (0 <= urr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_urr", 255)
        urr = 255
    urg = settings.Get("TrafficLightDetection", "ColorSettings_urg")
    if urg == None or not isinstance(urg, int) or not (0 <= urg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_urg", 110)
        urg = 110
    urb = settings.Get("TrafficLightDetection", "ColorSettings_urb")
    if urb == None or not isinstance(urb, int) or not (0 <= urb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_urb", 110)
        urb = 110
    lrr = settings.Get("TrafficLightDetection", "ColorSettings_lrr")
    if lrr == None or not isinstance(lrr, int) or not (0 <= lrr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lrr", 200)
        lrr = 200
    lrg = settings.Get("TrafficLightDetection", "ColorSettings_lrg")
    if lrg == None or not isinstance(lrg, int) or not (0 <= lrg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lrg", 0)
        lrg = 0
    lrb = settings.Get("TrafficLightDetection", "ColorSettings_lrb")
    if lrb == None or not isinstance(lrb, int) or not (0 <= lrb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lrb", 0)
        lrb = 0
    uyr = settings.Get("TrafficLightDetection", "ColorSettings_uyr")
    if uyr == None or not isinstance(uyr, int) or not (0 <= uyr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_uyr", 255)
        uyr = 255
    uyg = settings.Get("TrafficLightDetection", "ColorSettings_uyg")
    if uyg == None or not isinstance(uyg, int) or not (0 <= uyg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_uyg", 240)
        uyg = 240
    uyb = settings.Get("TrafficLightDetection", "ColorSettings_uyb")
    if uyb == None or not isinstance(uyb, int) or not (0 <= uyb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_uyb", 170)
        uyb = 170
    lyr = settings.Get("TrafficLightDetection", "ColorSettings_lyr")
    if lyr == None or not isinstance(lyr, int) or not (0 <= lyr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lyr", 200)
        lyr = 200
    lyg = settings.Get("TrafficLightDetection", "ColorSettings_lyg")
    if lyg == None or not isinstance(lyg, int) or not (0 <= lyg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lyg", 170)
        lyg = 170
    lyb = settings.Get("TrafficLightDetection", "ColorSettings_lyb")
    if lyb == None or not isinstance(lyb, int) or not (0 <= lyb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lyb", 50)
        lyb = 50
    ugr = settings.Get("TrafficLightDetection", "ColorSettings_ugr")
    if ugr == None or not isinstance(ugr, int) or not (0 <= ugr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_ugr", 150)
        ugr = 150
    ugg = settings.Get("TrafficLightDetection", "ColorSettings_ugg")
    if ugg == None or not isinstance(ugg, int) or not (0 <= ugg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_ugg", 255)
        ugg = 255
    ugb = settings.Get("TrafficLightDetection", "ColorSettings_ugb")
    if ugb == None or not isinstance(ugb, int) or not (0 <= ugb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_ugb", 230)
        ugb = 230
    lgr = settings.Get("TrafficLightDetection", "ColorSettings_lgr")
    if lgr == None or not isinstance(lgr, int) or not (0 <= lgr <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lgr", 0)
        lgr = 0
    lgg = settings.Get("TrafficLightDetection", "ColorSettings_lgg")
    if lgg == None or not isinstance(lgg, int) or not (0 <= lgg <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lgg", 200)
        lgg = 200
    lgb = settings.Get("TrafficLightDetection", "ColorSettings_lgb")
    if lgb == None or not isinstance(lgb, int) or not (0 <= lgb <= 255):
        settings.Set("TrafficLightDetection", "ColorSettings_lgb", 0)
        lgb = 0

    upper_red_advanced = np.array([urr, urg, urb])
    lower_red_advanced = np.array([lrr, lrg, lrb])
    upper_yellow_advanced = np.array([uyr, uyg, uyb])
    lower_yellow_advanced = np.array([lyr, lyg, lyb])
    upper_green_advanced = np.array([ugr, ugg, ugb])
    lower_green_advanced = np.array([lgr, lgg, lgb])


def get_screen():
    screen_x = monitor["left"]
    screen_y = monitor["top"]
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    return screen_x, screen_y, screen_width, screen_height


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


def ClassifyImage(image):
    try:
        if AIModelUpdateThread.is_alive(): return True
        if AIModelLoadThread.is_alive(): return True
    except:
        return True

    image = np.array(image, dtype=np.float32)
    if IMG_CHANNELS == 'Grayscale' or IMG_CHANNELS == 'Binarize':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if IMG_CHANNELS == 'RG':
        image = np.stack((image[:, :, 0], image[:, :, 1]), axis=2)
    elif IMG_CHANNELS == 'GB':
        image = np.stack((image[:, :, 1], image[:, :, 2]), axis=2)
    elif IMG_CHANNELS == 'RB':
        image = np.stack((image[:, :, 0], image[:, :, 2]), axis=2)
    elif IMG_CHANNELS == 'R':
        image = image[:, :, 0]
        image = np.expand_dims(image, axis=2)
    elif IMG_CHANNELS == 'G':
        image = image[:, :, 1]
        image = np.expand_dims(image, axis=2)
    elif IMG_CHANNELS == 'B':
        image = image[:, :, 2]
        image = np.expand_dims(image, axis=2)
    image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
    image = image / 255.0
    if IMG_CHANNELS == 'Binarize':
        image = cv2.threshold(image, 0.5, 1.0, cv2.THRESH_BINARY)[1]

    image = transforms.ToTensor()(image).unsqueeze(0).to(AIDevice)
    with torch.no_grad():
        output = np.array(AIModel(image)[0].tolist())
    obj_class = np.argmax(output)
    return True if obj_class != 3 else False


def HandleCorruptedAIModel():
    DeleteAllAIModels()
    CheckForAIModelUpdates()
    while AIModelUpdateThread.is_alive(): time.sleep(0.1)
    time.sleep(0.5)
    if TorchAvailable == True:
        LoadAIModel()
    else:
        print("TrafficLightDetectionAI not available due to missing dependencies.")
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
                    AIModel = torch.jit.load(os.path.join(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel", GetAIModelName()), map_location=AIDevice)
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
                SendCrashReport("TrafficLightDetection - Loading AI Error.", str(exc))
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
        SendCrashReport("TrafficLightDetection - Error in function LoadAIModel.", str(exc))
        print(f"TrafficLightDetection - Error in function LoadAIModel: {ex}")
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

                    if settings.Get("TrafficLightDetection", "LastUpdateCheck", 0) + 600 > time.time():
                        LoadAIProgress = 100
                        LoadAILabel = "Skipping AI model update check, last check was less than 10 minutes ago."
                        print("\033[92m" + f"Skipping AI model update check, last check was less than 10 minutes ago." + "\033[0m")
                        return
                    settings.Set("TrafficLightDetection", "LastUpdateCheck", round(time.time()))

                    url = "https://huggingface.co/Glas42/TrafficLightDetectionAI/tree/main/model"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/Glas42/TrafficLightDetectionAI/blob/main/model'):
                            LatestAIModel = href.split("/")[-1]
                            break

                    CurrentAIModel = GetAIModelName()
                    if CurrentAIModel == "UNKNOWN":
                        CurrentAIModel = None

                    if str(LatestAIModel) != str(CurrentAIModel):
                        LoadAILabel = "Updating AI model..."
                        print("\033[92m" + f"Updating AI model..." + "\033[0m")
                        DeleteAllAIModels()
                        response = requests.get(f"https://huggingface.co/Glas42/TrafficLightDetectionAI/resolve/main/model/{LatestAIModel}?download=true", stream=True)
                        last_progress = 0
                        with open(os.path.join(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel", f"{LatestAIModel}"), "wb") as modelfile:
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
                SendCrashReport("TrafficLightDetection - Error in function CheckForAIModelUpdatesThread.", str(exc))
                print(f"TrafficLightDetection - Error in function CheckForAIModelUpdatesThread: {ex}")
                console.RestoreConsole()
                print("\033[91m" + f"Failed to check for AI model updates or update the AI model." + "\033[0m")
                LoadAIProgress = 0
                LoadAILabel = "Failed to check for AI model updates or update the AI model."

        global AIModelUpdateThread
        AIModelUpdateThread = threading.Thread(target=CheckForAIModelUpdatesThread)
        AIModelUpdateThread.start()

    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Error in function CheckForAIModelUpdates.", str(exc))
        print(f"TrafficLightDetection - Error in function CheckForAIModelUpdates: {ex}")
        console.RestoreConsole()
        print("\033[91m" + f"Failed to check for AI model updates or update the AI model." + "\033[0m")


def ModelFolderExists():
    try:
        if os.path.exists(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel") == False:
            os.makedirs(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel")
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Error in function ModelFolderExists.", str(exc))
        print(f"TrafficLightDetection - Error in function ModelFolderExists: {ex}")
        console.RestoreConsole()


def GetAIModelName():
    try:
        ModelFolderExists()
        for file in os.listdir(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel"):
            if file.endswith(".pt"):
                return file
        return "UNKNOWN"
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Error in function GetAIModelName.", str(exc))
        print(f"TrafficLightDetection - Error in function GetAIModelName: {ex}")
        console.RestoreConsole()
        return "UNKNOWN"


def DeleteAllAIModels():
    try:
        ModelFolderExists()
        for file in os.listdir(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel"):
            if file.endswith(".pt"):
                os.remove(os.path.join(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel", file))
    except PermissionError:
        global TorchAvailable
        TorchAvailable = False
        settings.Set("TrafficLightDetection", "UseAI", False)
        print(f"TrafficLightDetection - PermissionError in function DeleteAllAIModels: {ex}")
        print("TrafficLightDetectionAI will be automatically disabled because the code cannot delete the AI model.")
        console.RestoreConsole()
    except Exception as ex:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Error in function DeleteAllAIModels.", str(exc))
        print(f"TrafficLightDetection - Error in function DeleteAllAIModels: {ex}")
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
        if GetAIModelName() == "UNKNOWN":
            return
        torch.jit.load(os.path.join(f"{variables.PATH}ETS2LA/plugins/TrafficLightDetection/AIModel", GetAIModelName()), _extra_files=MODEL_METADATA, map_location=AIDevice)
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
        SendCrashReport("TrafficLightDetection - Error in function GetAIModelProperties.", str(exc))
        print(f"TrafficLightDetection - Error in function GetAIModelProperties: {ex}")
        console.RestoreConsole()


def GetGamePosition():
    global last_GetGamePosition
    if variables.OS == "nt":
        if last_GetGamePosition[0] + 3 < time.time():
            hwnd = None
            top_windows = []
            window = last_GetGamePosition[1], last_GetGamePosition[2], last_GetGamePosition[3], last_GetGamePosition[4]
            win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
            for hwnd, window_text in top_windows:
                if "Truck Simulator" in window_text and "Discord" not in window_text:
                    rect = win32gui.GetClientRect(hwnd)
                    tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                    br = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
                    window = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
                    break
            last_GetGamePosition = time.time(), window[0], window[1], window[2], window[3]
            return window[0], window[1], window[2], window[3]
        else:
            return last_GetGamePosition[1], last_GetGamePosition[2], last_GetGamePosition[3], last_GetGamePosition[4]
    else:
        return screen_x, screen_y, screen_x + screen_width, screen_y + screen_height

def ConvertToAngle(x, y):
    _, _, window_width, window_height = GetGamePosition()
    fov_rad = math.radians(fov)
    window_distance = (window_height * (4 / 3) / 2) / math.tan(fov_rad / 2)
    angle_x = math.atan2(x - window_width / 2, window_distance) * (180 / math.pi)
    angle_y = math.atan2(y - window_height / 2, window_distance) * (180 / math.pi)
    return angle_x, angle_y


def plugin():
    global godot_data
    global coordinates
    global trafficlights
    global reset_window

    data = {}
    data["api"] = TruckSimAPI.run()
    data["frameFull"] = ScreenCapture.run(imgtype="full")

    frameFull = data["frameFull"]
    if frameFull is None: return (next((state for _, _, _, approved in trafficlights if approved and state in ("Red", "Yellow", "Green")), None), trafficlights), {"TrafficLights": godot_data}
    frame = frameFull[y1:y1+(y2-y1), x1:x1+(x2-x1)]

    try:
        truck_x = data["api"]["truckPlacement"]["coordinateX"]
        truck_y = data["api"]["truckPlacement"]["coordinateY"]
        truck_z = data["api"]["truckPlacement"]["coordinateZ"]
        truck_rotation_x = data["api"]["truckPlacement"]["rotationX"]
        truck_rotation_y = data["api"]["truckPlacement"]["rotationY"]
        truck_rotation_z = data["api"]["truckPlacement"]["rotationZ"]

        cabin_offset_x = data["api"]["headPlacement"]["cabinOffsetX"] + data["api"]["configVector"]["cabinPositionX"]
        cabin_offset_y = data["api"]["headPlacement"]["cabinOffsetY"] + data["api"]["configVector"]["cabinPositionY"]
        cabin_offset_z = data["api"]["headPlacement"]["cabinOffsetZ"] + data["api"]["configVector"]["cabinPositionZ"]
        cabin_offset_rotation_x = data["api"]["headPlacement"]["cabinOffsetrotationX"]
        cabin_offset_rotation_y = data["api"]["headPlacement"]["cabinOffsetrotationY"]
        cabin_offset_rotation_z = data["api"]["headPlacement"]["cabinOffsetrotationZ"]

        head_offset_x = data["api"]["headPlacement"]["headOffsetX"] + data["api"]["configVector"]["headPositionX"] + cabin_offset_x
        head_offset_y = data["api"]["headPlacement"]["headOffsetY"] + data["api"]["configVector"]["headPositionY"] + cabin_offset_y
        head_offset_z = data["api"]["headPlacement"]["headOffsetZ"] + data["api"]["configVector"]["headPositionZ"] + cabin_offset_z
        head_offset_rotation_x = data["api"]["headPlacement"]["headOffsetrotationX"]
        head_offset_rotation_y = data["api"]["headPlacement"]["headOffsetrotationY"]
        head_offset_rotation_z = data["api"]["headPlacement"]["headOffsetrotationZ"]
        
        truck_rotation_degrees_x = truck_rotation_x * 360
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

        head_rotation_degrees_x = (truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360
        while head_rotation_degrees_x > 360:
            head_rotation_degrees_x = head_rotation_degrees_x - 360

        head_rotation_degrees_y = (truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360

        head_rotation_degrees_z = (truck_rotation_z + cabin_offset_rotation_z + head_offset_rotation_z) * 360

        point_x = head_offset_x
        point_y = head_offset_y
        point_z = head_offset_z
        head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
        head_y = point_y * math.cos(math.radians(head_rotation_degrees_y)) - point_z * math.sin(math.radians(head_rotation_degrees_y)) + truck_y
        head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z
    except:
        truck_x = 0
        truck_y = 0
        truck_z = 0
        truck_rotation_x = 0
        truck_rotation_y = 0
        truck_rotation_z = 0

        cabin_offset_x = 0
        cabin_offset_y = 0
        cabin_offset_z = 0
        cabin_offset_rotation_x = 0
        cabin_offset_rotation_y = 0
        cabin_offset_rotation_z = 0

        head_offset_x = 0
        head_offset_y = 0
        head_offset_z = 0
        head_offset_rotation_x = 0
        head_offset_rotation_y = 0
        head_offset_rotation_z = 0

        truck_rotation_degrees_x = 0
        truck_rotation_radians_x = 0

        head_rotation_degrees_x = 0
        head_rotation_degrees_y = 0
        head_rotation_degrees_z = 0

        head_x = 0
        head_y = 0
        head_z = 0


    # ALL CASES:

    # True: --- False: advancedmode, performancemode, detectyellowlight
    # True: detectyellowlight --- False: advancedmode, performancemode
    # True: performancemode --- False: advancedmode
    # True: advancedmode --- False: performancemode, detectyellowlight
    # True: advancedmode, detectyellowlight --- False: performancemode
    # True: advancedmode, performancemode --- False: 


    last_coordinates = coordinates.copy()
    coordinates = []
    if advancedmode == False:
        if performancemode == False:
            if detectyellowlight == False:
                # True: --- False: advancedmode, performancemode, detectyellowlight
                mask_red = cv2.inRange(frame, lower_red, upper_red)
                mask_green = cv2.inRange(frame, lower_green, upper_green)
                filtered_frame_colored = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            if green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 or red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1:
                                if red_ratio > green_ratio:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                elif green_ratio > red_ratio:
                                    colorstr = "Green"
                                    offset = y - h
                                else:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                point_mask = []
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                                point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                                as_expected = True
                                for i in range(len(point_mask)):
                                    point_x, point_y, expected = point_mask[i]
                                    color = filtered_frame_bw[point_y, point_x]
                                    color = True if color != 0 else False
                                    if color != 0 == expected:
                                        as_expected = False
                                        break
                                if as_expected:
                                    coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))

            else:

                # True: detectyellowlight --- False: advancedmode, performancemode
                mask_red = cv2.inRange(frame, lower_red, upper_red)
                mask_green = cv2.inRange(frame, lower_green, upper_green)
                mask_yellow = cv2.inRange(frame, lower_yellow, upper_yellow)
                combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                filtered_frame_colored = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            yellow_pixel_count = cv2.countNonZero(mask_yellow[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            yellow_ratio = yellow_pixel_count / total_pixels
                            if (green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 and yellow_ratio < 0.1 or 
                                red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1 and yellow_ratio < 0.1 or 
                                yellow_ratio < circleplusoffset and yellow_ratio > circleminusoffset and green_ratio < 0.1 and red_ratio < 0.1):
                                if red_ratio > green_ratio and red_ratio > yellow_ratio:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                elif yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                    colorstr = "Yellow"
                                    offset = y + h * 0.5
                                elif green_ratio > red_ratio and green_ratio > yellow_ratio:
                                    colorstr = "Green"
                                    offset = y - h
                                else:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                point_mask = []
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                                point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                                as_expected = True
                                for i in range(len(point_mask)):
                                    point_x, point_y, expected = point_mask[i]
                                    color = filtered_frame_bw[point_y, point_x]
                                    color = True if color != 0 else False
                                    if color != 0 == expected:
                                        as_expected = False
                                        break
                                if as_expected:
                                    coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))
        else:

            # True: performancemode --- False: advancedmode
            mask_red = cv2.inRange(frame, lower_red, upper_red)
            filtered_frame_bw = mask_red.copy()
            final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                    if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                        red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                        total_pixels = w * h
                        red_ratio = red_pixel_count / total_pixels
                        if red_ratio < circleplusoffset and red_ratio > circleminusoffset:
                            colorstr = "Red"
                            offset = y + h * 2
                            point_mask = []
                            point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                            point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                            point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                            point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                            point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                            point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                            point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                            point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                            point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                            as_expected = True
                            for i in range(len(point_mask)):
                                point_x, point_y, expected = point_mask[i]
                                color = filtered_frame_bw[point_y, point_x]
                                color = True if color != 0 else False
                                if color != 0 == expected:
                                    as_expected = False
                                    break
                            if as_expected:
                                coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))

    else:

        if performancemode == False:
            if detectyellowlight == False:
                # True: advancedmode --- False: performancemode, detectyellowlight
                mask_red = cv2.inRange(frame, lower_red_advanced, upper_red_advanced)
                mask_green = cv2.inRange(frame, lower_green_advanced, upper_green_advanced)
                filtered_frame_colored = cv2.bitwise_or(cv2.bitwise_and(frame, frame, mask=mask_red), cv2.bitwise_and(frame, frame, mask=mask_green))
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    istrue = False
                    if rectsizefilter == True:
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        istrue = False
                        if widthheightratiofilter == True:
                            if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            istrue = False
                            if pixelpercentagefilter == True:
                                if green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 or red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1:
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                if red_ratio > green_ratio:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                elif green_ratio > red_ratio:
                                    colorstr = "Green"
                                    offset = y - h
                                else:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                istrue = False
                                if pixelblobshapefilter == True:
                                    point_mask = []
                                    point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                                    point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                                    point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                                    point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                                    point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                                    point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                                    as_expected = True
                                    for i in range(len(point_mask)):
                                        point_x, point_y, expected = point_mask[i]
                                        color = filtered_frame_bw[point_y, point_x]
                                        color = True if color != 0 else False
                                        if color != 0 == expected:
                                            as_expected = False
                                            break
                                    if as_expected:
                                        istrue = True
                                else:
                                    istrue = True
                                if istrue == True:
                                    coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))

            else:

                # True: advancedmode, detectyellowlight --- False: performancemode
                mask_red = cv2.inRange(frame, lower_red_advanced, upper_red_advanced)
                mask_green = cv2.inRange(frame, lower_green_advanced, upper_green_advanced)
                mask_yellow = cv2.inRange(frame, lower_yellow_advanced, upper_yellow_advanced)
                combined_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_green, mask_yellow))
                filtered_frame_colored = cv2.bitwise_and(frame, frame, mask=combined_mask)
                filtered_frame_bw = cv2.cvtColor(filtered_frame_colored, cv2.COLOR_BGR2GRAY)
                final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                contours, _ = cv2.findContours(filtered_frame_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    istrue = False
                    if rectsizefilter == True:
                        if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        istrue = False
                        if widthheightratiofilter == True:
                            if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                            green_pixel_count = cv2.countNonZero(mask_green[y:y+h, x:x+w])
                            yellow_pixel_count = cv2.countNonZero(mask_yellow[y:y+h, x:x+w])
                            total_pixels = w * h
                            red_ratio = red_pixel_count / total_pixels
                            green_ratio = green_pixel_count / total_pixels
                            yellow_ratio = yellow_pixel_count / total_pixels
                            istrue = False
                            if pixelpercentagefilter == True:
                                if (green_ratio < circleplusoffset and green_ratio > circleminusoffset and red_ratio < 0.1 and yellow_ratio < 0.1 or 
                                    red_ratio < circleplusoffset and red_ratio > circleminusoffset and green_ratio < 0.1 and yellow_ratio < 0.1 or 
                                    yellow_ratio < circleplusoffset and yellow_ratio > circleminusoffset and green_ratio < 0.1 and red_ratio < 0.1):
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                if red_ratio > green_ratio and red_ratio > yellow_ratio:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                elif yellow_ratio > red_ratio and yellow_ratio > green_ratio:
                                    colorstr = "Yellow"
                                    offset = y + h * 0.5
                                elif green_ratio > red_ratio and green_ratio > yellow_ratio:
                                    colorstr = "Green"
                                    offset = y - h
                                else:
                                    colorstr = "Red"
                                    offset = y + h * 2
                                istrue = False
                                if pixelblobshapefilter == True:
                                    point_mask = []
                                    point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                                    point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                                    point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                                    point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                                    point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                                    point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                                    point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                                    as_expected = True
                                    for i in range(len(point_mask)):
                                        point_x, point_y, expected = point_mask[i]
                                        color = filtered_frame_bw[point_y, point_x]
                                        color = True if color != 0 else False
                                        if color != 0 == expected:
                                            as_expected = False
                                            break
                                    if as_expected:
                                        istrue = True
                                else:
                                    istrue = True
                                if istrue == True:
                                    coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))

        else:

            # True: advancedmode, performancemode --- False:     
            mask_red = cv2.inRange(frame, lower_red_advanced, upper_red_advanced)
            filtered_frame_bw = mask_red.copy()
            final_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                istrue = False
                if rectsizefilter == True:
                    if min_rect_size < w and max_rect_size > w and min_rect_size < h and max_rect_size > h:
                        istrue = True
                else:
                    istrue = True
                if istrue == True:
                    istrue = False
                    if widthheightratiofilter == True:
                        if w / h - 1 < width_height_ratio * 2 and w / h - 1 > -width_height_ratio:
                            istrue = True
                    else:
                        istrue = True
                    if istrue == True:
                        red_pixel_count = cv2.countNonZero(mask_red[y:y+h, x:x+w])
                        total_pixels = w * h
                        red_ratio = red_pixel_count / total_pixels
                        istrue = False
                        if pixelpercentagefilter == True:
                            if red_ratio < circleplusoffset and red_ratio > circleminusoffset:
                                istrue = True
                        else:
                            istrue = True
                        if istrue == True:
                            colorstr = "Red"
                            offset = y + h * 2
                            istrue = False
                            if pixelblobshapefilter == True:
                                point_mask = []
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.2), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.05), False))
                                point_mask.append((round(x + w * 0.3), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.5), True))
                                point_mask.append((round(x + w * 0.7), round(y + h * 0.6), True))
                                point_mask.append((round(x + w * 0.05), round(y + h * 0.95), False))
                                point_mask.append((round(x + w * 0.5), round(y + h * 0.8), True))
                                point_mask.append((round(x + w * 0.95), round(y + h * 0.95), False))
                                as_expected = True
                                for i in range(len(point_mask)):
                                    point_x, point_y, expected = point_mask[i]
                                    color = filtered_frame_bw[point_y, point_x]
                                    color = True if color != 0 else False
                                    if color != 0 == expected:
                                        as_expected = False
                                        break
                                if as_expected:
                                    istrue = True
                            else:
                                istrue = True
                            if istrue == True:
                                coordinates.append((round(x + w * 0.5), round(offset), w, h, colorstr))


    try:
        # Tracking with IDs:
        def generate_new_id():
            used_ids = set(id for _, _, id, _ in trafficlights)
            new_id = 1
            while new_id in used_ids:
                new_id += 1
            return new_id

        if last_coordinates:
            for i in range(len(last_coordinates)):
                last_x, last_y, w, h, state = last_coordinates[i]
                closest = screen_width
                nearestpoint = None
                exists_in_trafficlights = False
                saved_position = None
                saved_id = None
                saved_approved = None
                for j in range(len(coordinates)):
                    x, y, w, h, state = coordinates[j]
                    distance = math.sqrt((x - last_x)**2 + (y - last_y)**2)
                    if distance < closest:
                        closest = distance
                        nearestpoint = x, y, w, h, state

                # Remove missing points from traffic lights and update list
                if nearestpoint:
                    for k, (coord, position, id, approved) in enumerate(trafficlights):
                        if coord == last_coordinates[i]:
                            exists_in_trafficlights = True
                            angle = ConvertToAngle(nearestpoint[0], nearestpoint[1])[0]
                            saved_position = (position[0], (head_x, head_z, angle, head_rotation_degrees_x), position[2])
                            saved_id = id
                            saved_approved = approved
                            del trafficlights[k]
                            break
                    if exists_in_trafficlights:
                        trafficlights.append((nearestpoint, saved_position, saved_id, saved_approved))
                    else:
                        new_id = generate_new_id()
                        angle = ConvertToAngle(nearestpoint[0], nearestpoint[1])[0]
                        if UseAI == True:
                            x, y, w, h, state = nearestpoint
                            y1_classification = round(y1+y-h*4)
                            if y1_classification < 0:
                                y1_classification = 0
                            elif y1_classification > frameFull.shape[0]:
                                y1_classification = frameFull.shape[0]
                            y2_classification = round(y1+y+h*4)
                            if y2_classification < 0:
                                y2_classification = 0
                            elif y2_classification > frameFull.shape[0]:
                                y2_classification = frameFull.shape[0]
                            x1_classification = round(x1+x-w*2.5)
                            if x1_classification < 0:
                                x1_classification = 0
                            elif x1_classification > frameFull.shape[1]:
                                x1_classification = frameFull.shape[1]
                            x2_classification = round(x1+x+w*2.5)
                            if x2_classification < 0:
                                x2_classification = 0
                            elif x2_classification > frameFull.shape[1]:
                                x2_classification = frameFull.shape[1]
                            image_classification = frameFull[y1_classification:y2_classification, x1_classification:x2_classification]
                            approved = ClassifyImage(image_classification)
                        else:
                            approved = True
                        trafficlights.append((nearestpoint, ((None, None, None), (head_x, head_z, angle, head_rotation_degrees_x), (head_x, head_z, angle, head_rotation_degrees_x)), new_id, approved))

        # Remove lost traffic lights from the list, the traffic light which has the highest distance to the nearest traffic light in the current frame gets removed
        exists = []
        for coord_x, coord_y, _, _, _ in coordinates:
            for (x, y, _, _, _), _, id, _ in trafficlights:
                if x == coord_x and y == coord_y:
                    exists.append(id)
                    break
        for i, (_, _, id, _) in enumerate(trafficlights):
            if id not in exists:
                del trafficlights[i]
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Tracking/YOLO Error.", str(exc))
        print("TrafficLightDetection - Tracking/YOLO Error: " + str(exc))


    try:
        for i, (coord, ((previous_trafficlight_x, previous_trafficlight_y, previous_trafficlight_z), (head_x, head_z, head_angle, head_rotation), (first_head_x, first_head_z, first_head_angle, first_head_rotation)), id, approved) in enumerate(trafficlights):
            x, y, w, h, state = coord

            angle_offset = first_head_rotation - head_rotation

            angle_A = 180 - head_angle - angle_offset
            angle_B = first_head_angle
            if angle_B < 0:
                angle_B = 360 + angle_B

            position_A = head_x, head_z
            position_B = first_head_x, first_head_z

            if math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2) > 0.01:
                angle_A_rad = math.radians(angle_A)
                angle_B_rad = math.radians(angle_B)
                angle_C_rad = math.pi - angle_A_rad - angle_B_rad
                distance_AB = math.sqrt((position_B[0] - position_A[0]) ** 2 + (position_B[1] - position_A[1]) ** 2)
                if math.sin(angle_C_rad) != 0:
                    length_A = distance_AB * math.sin(angle_A_rad) / math.sin(angle_C_rad)
                    length_B = distance_AB * math.sin(angle_B_rad) / math.sin(angle_C_rad)
                else:
                    length_A = distance_AB
                    length_B = distance_AB
                position_C_x = length_B * math.cos(angle_A_rad)
                position_C_y = length_B * math.sin(angle_A_rad)
                direction_AB = (position_B[0] - position_A[0], position_B[1] - position_A[1])
                length_AB = math.sqrt(direction_AB[0] ** 2 + direction_AB[1] ** 2)
                if length_AB == 0:
                    length_AB = 0.0001
                direction_unit_AB = (direction_AB[0] / length_AB, direction_AB[1] / length_AB)
                direction_unit_perpendicular_ab = (-direction_unit_AB[1], direction_unit_AB[0])
                position_C = (position_A[0] + position_C_x * direction_unit_AB[0] - position_C_y * direction_unit_perpendicular_ab[0], position_A[1] + position_C_x * direction_unit_AB[1] - position_C_y * direction_unit_perpendicular_ab[1])

                trafficlight_x, trafficlight_z = position_C

                angle = ConvertToAngle(x, y)[1]
                distance = math.sqrt((trafficlight_x - head_x)**2 + (trafficlight_z - head_z)**2)
                trafficlight_y = head_y + (math.sin(angle) / distance if distance != 0 else 0.0001)

                if previous_trafficlight_x != None and previous_trafficlight_y != None and previous_trafficlight_z != None:
                    trafficlight_x = previous_trafficlight_x + (trafficlight_x - previous_trafficlight_x) / 5
                    trafficlight_y = previous_trafficlight_y + (trafficlight_y - previous_trafficlight_y) / 5
                    trafficlight_z = previous_trafficlight_z + (trafficlight_z - previous_trafficlight_z) / 5
                
                trafficlights[i] = (coord, ((trafficlight_x, trafficlight_y, trafficlight_z), (head_x, head_z, head_angle, head_rotation), (first_head_x, first_head_z, first_head_angle, first_head_rotation)), id, approved)

    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Position Estimation Error.", str(exc))
        print("TrafficLightDetection - Position Estimation Error: " + str(e))


    try:
        if anywindowopen == True:
            if grayscalewindow == True and len(trafficlights) > 0:
                text, text_fontscale, text_thickness, text_width, text_height = get_text_size(text="Objects in Tracker:", text_width=0.2 * filtered_frame_bw.shape[1], max_text_height=filtered_frame_bw.shape[0])
                cv2.putText(filtered_frame_bw, text, (round(0.01 * filtered_frame_bw.shape[0]), round(0.01 * filtered_frame_bw.shape[0] + text_height)), cv2.FONT_HERSHEY_SIMPLEX, text_fontscale, (255, 255, 255), text_thickness)
            for i in range(len(trafficlights)):
                coord, position, id, approved = trafficlights[i]
                x, y, w, h, state = coord
                if grayscalewindow == True:
                    if approved == True:
                        cv2.putText(filtered_frame_bw, f"ID: {id}, {state}", (round(0.01 * filtered_frame_bw.shape[0]), round(0.01 * filtered_frame_bw.shape[0] + text_height * (i+2) * 1.5)), cv2.FONT_HERSHEY_SIMPLEX, text_fontscale, (255, 255, 255), text_thickness)
                        cv2.line(filtered_frame_bw, (round(0.01 * filtered_frame_bw.shape[0] + cv2.getTextSize(f"ID: {id}, {state}", cv2.FONT_HERSHEY_SIMPLEX, text_fontscale, 1)[0][0]) + 10, round(0.01 * filtered_frame_bw.shape[0] + text_height * (i + 2) * 1.5 - text_height / 2)), ((x, round(y - h * 1.5)) if state == "Red" else (x, round(y + h * 1.5)) if state == "Green" else (x, y)), (150, 150, 150), text_thickness)
                    else:
                        cv2.putText(filtered_frame_bw, f"ID: {id}, Ignored by AI", (round(0.01 * filtered_frame_bw.shape[0]), round(0.01 * filtered_frame_bw.shape[0] + text_height * (i+2) * 1.5)), cv2.FONT_HERSHEY_SIMPLEX, text_fontscale, (255, 255, 255), text_thickness)
                        cv2.line(filtered_frame_bw, (round(0.01 * filtered_frame_bw.shape[0] + cv2.getTextSize(f"ID: {id}, Ignored by AI", cv2.FONT_HERSHEY_SIMPLEX, text_fontscale, 1)[0][0]) + 10, round(0.01 * filtered_frame_bw.shape[0] + text_height * (i + 2) * 1.5 - text_height / 2)), ((x, round(y - h * 1.5)) if state == "Red" else (x, round(y + h * 1.5)) if state == "Green" else (x, y)), (150, 150, 150), text_thickness)
                radius = round((w + h) / 4)
                thickness = round((w + h) / 30)
                if thickness < 1:
                    thickness = 1
                if approved == True:
                    if state == "Red":
                        color = (0, 0, 255)
                        cv2.rectangle(final_frame, (round(x - w * 1.1), round(y - h * 2.5)), (round(x + w * 1.1), round(y + h * 2.5)), color, radius)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 2)), (round(x + w * 0.5), round(y - h)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 0.5)), (round(x + w * 0.5), round(y + h * 0.5)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x + w * 0.5), round(y + h * 2)), (round(x - w * 0.5), round(y + h)), (150, 150, 150), thickness)
                    if state == "Yellow":
                        color = (0, 255, 255)
                        cv2.rectangle(final_frame, (round(x - w * 1.1), round(y - h * 2.5)), (round(x + w * 1.1), round(y + h * 2.5)), color, radius)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 2)), (round(x + w * 0.5), round(y - h)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 0.5)), (round(x + w * 0.5), round(y + h * 0.5)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x + w * 0.5), round(y + h * 2)), (round(x - w * 0.5), round(y + h)), (150, 150, 150), thickness)
                    if state == "Green":
                        color = (0, 255, 0)
                        cv2.rectangle(final_frame, (round(x - w * 1.1), round(y - h * 2.5)), (round(x + w * 1.1), round(y + h * 2.5)), color, radius)
                        if finalwindow == True:
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 2)), (round(x + w * 0.5), round(y - h)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x - w * 0.5), round(y - h * 0.5)), (round(x + w * 0.5), round(y + h * 0.5)), (150, 150, 150), thickness)
                            cv2.rectangle(final_frame, (round(x + w * 0.5), round(y + h * 2)), (round(x - w * 0.5), round(y + h)), (150, 150, 150), thickness)
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("TrafficLightDetection - Draw Output Error.", str(exc))
        print("TrafficLightDetection - Draw Output Error: " + str(e))


    if positionestimationwindow == True:
        try:
            positionestimation_frame = positionestimation_default_frame.copy()
            positionestimation_frame_width = positionestimation_frame.shape[1]
            positionestimation_frame_height = positionestimation_frame.shape[0]

            for i, ((_, _, _, _, state), ((trafficlight_x, trafficlight_y, trafficlight_z), _, _), _, _) in enumerate(trafficlights):
                if trafficlight_x != None and trafficlight_y != None and trafficlight_z != None:
                    ppm = 0.1
                    x = (trafficlight_x - truck_x) * (1/ppm)
                    y = (trafficlight_z - truck_z) * (1/ppm)

                    point_x = x
                    point_y = y
                    x = round(positionestimation_frame_width/4 + (point_x * math.cos(truck_rotation_radians_x) + point_y * math.sin(truck_rotation_radians_x)))
                    y = round(positionestimation_frame_height - (point_x * math.sin(truck_rotation_radians_x) - point_y * math.cos(truck_rotation_radians_x)))

                    if state == "Red":
                        color = (0, 0, 255)
                    elif state == "Yellow":
                        color = (0, 255, 255)
                    elif state == "Green":
                        color = (0, 255, 0)
                    if -5 < int(x) < positionestimation_frame_width + 5 and -5 < int(y - round(positionestimation_frame_height * 0.179)) < positionestimation_frame_height + 5:
                        cv2.circle(positionestimation_frame, (int(x), int(y - round(positionestimation_frame_height * 0.179))), round(positionestimation_frame_height/100), color, -1)

        except Exception as e:
            exc = traceback.format_exc()
            SendCrashReport("TrafficLightDetection - Position Estimation Drawing Error.", str(exc))
            print("TrafficLightDetection - Position Estimation Drawing Error: " + str(e))


    if reset_window == True:
        if finalwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Final')
            except:
                pass
        if grayscalewindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - B/W')
            except:
                pass
        if positionestimationwindow == False:
            try:
                cv2.destroyWindow('Traffic Light Detection - Position Estimation')
            except:
                pass

    if finalwindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Final')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - Final', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - Final', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - Final', cv2.WND_PROP_TOPMOST, 1)
            if os.name == 'nt':
                hwnd = win32gui.FindWindow(None, 'Traffic Light Detection - Final')
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x2F2F2F)), sizeof(c_int))
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(None, f"{variables.PATH}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
        cv2.imshow('Traffic Light Detection - Final', final_frame)
    if grayscalewindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - B/W')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - B/W', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - B/W', round(windowwidth*windowscale), round(windowheight*windowscale))
            cv2.setWindowProperty('Traffic Light Detection - B/W', cv2.WND_PROP_TOPMOST, 1)
            if variables.OS == "nt":
                hwnd = win32gui.FindWindow(None, 'Traffic Light Detection - B/W')
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(None, f"{variables.PATH}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
        cv2.imshow('Traffic Light Detection - B/W', filtered_frame_bw)
    if positionestimationwindow == True:
        window_handle = ctypes.windll.user32.FindWindowW(None, 'Traffic Light Detection - Position Estimation')
        if window_handle == 0 or reset_window == True:
            cv2.namedWindow('Traffic Light Detection - Position Estimation', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Light Detection - Position Estimation', positionestimation_frame.shape[1], positionestimation_frame.shape[0])
            cv2.setWindowProperty('Traffic Light Detection - Position Estimation', cv2.WND_PROP_TOPMOST, 1)
            if variables.OS == "nt":
                hwnd = win32gui.FindWindow(None, 'Traffic Light Detection - Position Estimation')
                windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(None, f"{variables.PATH}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
                win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
        cv2.imshow('Traffic Light Detection - Position Estimation', positionestimation_frame)
    if anywindowopen == True:
        cv2.waitKey(1)
    if reset_window == True:
        reset_window = False

    godot_data = []
    for i, ((_, _, _, _, state), ((trafficlight_x, trafficlight_y, trafficlight_z), _, _), _, approved) in enumerate(trafficlights):
        if approved == True and trafficlight_x != None and trafficlight_y != None and trafficlight_z != None:
            godot_data.append((state, trafficlight_x, trafficlight_y, trafficlight_z))

    return (next((state for _, _, _, approved in trafficlights if approved and state in ("Red", "Yellow", "Green")), None), trafficlights), {"TrafficLights": godot_data}