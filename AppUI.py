from doctest import debug_script
import json
from turtle import onclick
import streamlit as st
import threading
import time
from PIL import ImageGrab, ImageColor
import os


# Get screen dimensions
img = ImageGrab.grab()
width, height = img.size

# Setup the page and sidebar
st.set_page_config(layout="centered")
data = None
settings = None
secondThread = None
browser = None
availableModels = []
modelFolderPath = "models"

# These two functions start the lane detection
def MainFileThread():
    time.sleep(0.1)
    import MainFile



with open("interface.json", "r") as f:
    data = json.load(f)

if data["uiRefreshes"] < 1:
    mainFileThread = threading.Thread(target=MainFileThread)
    mainFileThread.start()

with open("interface.json", "w") as f:
    data["uiRefreshes"] = data["uiRefreshes"] + 1
    f.truncate(0)
    json.dump(data, f, indent=4)



# Function to change settings in the json file
def UpdateSettings(category, name, data):
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings[category][name] = data
    with open("settings.json", "w") as f:
        f.truncate(0)
        json.dump(settings, f, indent=6)


# Function to edit the interface values
def UpdateInterface(name, value):
    with open("interface.json", "r") as f:
        interface = json.load(f)
    interface[name] = value
    with open("interface.json", "w") as f:
        f.truncate(0)
        json.dump(interface, f, indent=4)


def GetSettings(category, name):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    return settings[category][name]

# Helper function
def ChangeBoolInInterface(name):
    if data[name] == True:
        UpdateInterface(name, False)
    else:
        UpdateInterface(name, True)

time.sleep(1)

# Update the json data
def UpdateData():
    global data
    global settings
    global timesRun
    try:
        f = open("interface.json", "r")
        data = json.load(f)
        f.close()
    except:
        pass

    try:
        f = open("settings.json", "r")
        settings = json.load(f)
        f.close()
    except:
        pass

UpdateData()

def UpdateAvailableModels():
    global availableModels
    availableModels = []
    for file in os.listdir(modelFolderPath):
        if file.endswith(".pth"):
            availableModels.append(file)
    
UpdateAvailableModels()

# Close the app gracefully
def CloseApplication():
    UpdateInterface("close", True)
    time.sleep(0.5)
    UpdateInterface("close", False)
    
    with open("interface.json", "w") as f:
        data["uiRefreshes"] = 0
        f.truncate(0)
        json.dump(data, f, indent=4)

    exit()

def AddLines(number, base):
    for i in range(number):
        base.write("")


# Main Control page
st.title("Control panel")
col1, col2 = st.columns([1, 4])
col1.button("Refresh UI")
col1.button("Reset App", on_click=UpdateInterface, args=("uiRefreshes", 0))
col2.info("The UI sometimes needs to be refreshed manually, this is a limitation of streamlit. The UI has had {} refreshes.".format(data["uiRefreshes"]))
general, video, model, controls = st.tabs(["General", "Video", "Model", "Controls"])


# General options
general.button("Toggle Lane Assist", on_click=ChangeBoolInInterface, args=["enabled"])
if data["enabled"]:
    general.success("Lane Assist is enabled")
else:
    general.error("Lane Assist is disabled")
general.button("Toggle Preview", on_click=ChangeBoolInInterface, args=["preview"])
if data["preview"]:
    general.success("Preview is enabled")
else:
    general.error("Preview is disabled")

general.info("You will also have to close the prompt, when closing the program.")
general.button("Close Application", on_click=CloseApplication)


# Video options
video.info("Screen dimensions are {}x{}".format(width, height))
dimensionsCol1, dimensionsCol2 = video.columns(2)
desiredWidth = dimensionsCol1.number_input("Video Width", min_value=0, max_value=width, value=settings["screenCapture"]["width"])
desiredHeight = dimensionsCol2.number_input("Video Height", min_value=0, max_value=height, value=settings["screenCapture"]["height"])

AddLines(4, video)

video.info("Max values are {}x{}".format(width-desiredWidth, height-desiredHeight))
sizeCol1, sizeCol2 = video.columns(2)
desiredX = sizeCol1.number_input("Video X", min_value=0, max_value=width-desiredWidth, value=settings["screenCapture"]["x"])
desiredY = sizeCol2.number_input("Video Y", min_value=0, max_value=height-desiredHeight, value=settings["screenCapture"]["y"])

UpdateSettings("screenCapture", "width", desiredWidth)
UpdateSettings("screenCapture", "height", desiredHeight)
UpdateSettings("screenCapture", "x", desiredX)
UpdateSettings("screenCapture", "y", desiredY)

video.button("Update video settings", on_click=ChangeBoolInInterface, args=["updateCameraSettings"])
AddLines(4, video)

video.info("DirectX is a brand new api utilizing windows specific features.\nFor compatibility reasons, I have left in MSS even though it is slower.\nFPS selector is not available for MSS.")
screenSettingsCol1, screenSettingsCol2 = video.columns(2)
screenCaptureMode = screenSettingsCol1.selectbox("Screen Capture Mode", ["DirectX (Windows, higher performace)", "MSS (Linux / Mac compatible)"], args=["screenCaptureMode"])

if screenCaptureMode == "DirectX (Windows, higher performace)":
    desiredFPS = screenSettingsCol2.number_input("Desired FPS", min_value=1, max_value=60, value=settings["screenCapture"]["DXframerate"])
    UpdateSettings("screenCapture", "useDirectX", True)
    UpdateSettings("screenCapture", "DXframerate", desiredFPS)
else:
    desiredFPS = screenSettingsCol2.number_input("Desired FPS", min_value=1, max_value=60, value=settings["screenCapture"]["DXframerate"],disabled=True)
    UpdateSettings("screenCapture", "useDirectX", False)

video.info("You will have to restart the application after changing the screen capture mode.")


# Model options
model.info("You can find download links for models in the github page. After changing any settings, click the button at the bottom of this page.")
modelToUse = model.selectbox("Select model", availableModels)
useGPU = model.checkbox("Use GPU", value=settings["modelSettings"]["useGPU"])

model.button("Update available models", on_click=UpdateAvailableModels)
model.button("Load model", on_click=ChangeBoolInInterface, args=["loadModel"])

AddLines(4, model)
model.info("These might affect performance depending on your hardware. (Specifically CPU)")
laneOptionsCol1, laneOptionsCol2, laneOptionsCol3, laneOptionsCol4 = model.columns(4)
greenDots = laneOptionsCol1.checkbox("Show green dots", value=settings["generalSettings"]["computeGreenDots"])
steeringLine = laneOptionsCol2.checkbox("Show steering line", value=settings["generalSettings"]["drawSteeringLine"])
showLanePoints = laneOptionsCol3.checkbox("Show lane points", value=settings["generalSettings"]["showLanePoints"])
showLanes = laneOptionsCol4.checkbox("Fill lane", value=settings["generalSettings"]["showLanePoints"])
color = model.color_picker("Lane Color", value=settings["generalSettings"]["laneColor"])
model.button("Update lane assist settings", on_click=ChangeBoolInInterface, args=["updateGeneralSettings"])

UpdateSettings("modelSettings", "modelPath", modelToUse)
UpdateSettings("modelSettings", "useGPU", useGPU)
UpdateSettings("generalSettings", "computeGreenDots", greenDots)
UpdateSettings("generalSettings", "drawSteeringLine", steeringLine)
UpdateSettings("generalSettings", "showLanePoints", showLanePoints)
UpdateSettings("generalSettings", "fillLane", showLanes)
UpdateSettings("generalSettings", "laneColor", color)

# Controls options
controls.info("Press the button below after making any changes.")
controls.button("Update controls", on_click=ChangeBoolInInterface, args=["updateControls"])
controller = controls.selectbox("Controller", data["controllers"], index=settings["controlSettings"]["defaultControllerIndex"])
AddLines(4, controls)
controls.info("These are general control settings, they affect how the virtual controller behaves.")
sensCol1, sensCol2 = controls.columns(2)
steeringOffset = sensCol1.number_input("Steering Offset", min_value=-1000, max_value=1000, value=settings["controlSettings"]["steeringOffset"])
sensitivity = sensCol2.number_input("Sensitivity", min_value=0, max_value=1000, value=settings["controlSettings"]["sensitivity"])
sliderCol1, sliderCol2 = controls.columns(2)
controlSmoothness = sliderCol1.slider("Control Smoothness", min_value=0, max_value=10, value=settings["controlSettings"]["controlSmoothness"])
maximumControl = sliderCol2.slider("Maximum Control", min_value=0.0, max_value=1.0, value=settings["controlSettings"]["maximumControl"], step=0.01)
disableLaneAssistWhenIndicating = controls.checkbox("Disable Lane Assist When Indicating", value=settings["controlSettings"]["disableLaneAssistWhenIndicating"])
AddLines(4, controls)
controls.info("Your current controller has {} buttons and {} axes.".format(data["currentControllerButtons"], data["currentControllerAxes"]))
buttonCol1, buttonCol2, buttonCol3, buttonCol4 = controls.columns(4)
steeringAxis = buttonCol1.number_input("Steering Axis", min_value=0, max_value=100, value=settings["controlSettings"]["steeringAxis"])
enableDisableButton = buttonCol2.number_input("Enable / Disable Button", min_value=0, max_value=100, value=settings["controlSettings"]["enableDisableButton"])
rightIndicatorButton = buttonCol3.number_input("Right Indicator Button", min_value=0, max_value=100, value=settings["controlSettings"]["rightIndicator"])
leftIndicatorButton = buttonCol4.number_input("Left Indicator Button", min_value=0, max_value=100, value=settings["controlSettings"]["leftIndicator"])




UpdateSettings("controlSettings", "defaultControllerIndex", data["controllers"].index(controller))
UpdateSettings("controlSettings", "steeringOffset", steeringOffset)
UpdateSettings("controlSettings", "sensitivity", sensitivity)
UpdateSettings("controlSettings", "steeringAxis", steeringAxis)
UpdateSettings("controlSettings", "enableDisableButton", enableDisableButton)
UpdateSettings("controlSettings", "rightIndicator", rightIndicatorButton)
UpdateSettings("controlSettings", "leftIndicator", leftIndicatorButton)
UpdateSettings("controlSettings", "maximumControl", maximumControl)
UpdateSettings("controlSettings", "controlSmoothness", controlSmoothness)
UpdateSettings("controlSettings", "disableLaneAssistWhenIndicating", disableLaneAssistWhenIndicating)