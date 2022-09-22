from doctest import debug_script
import json
import streamlit as st
import threading
import time
import sys
from PIL import ImageGrab
import gc
import webbrowser

# Open the chrome browser


# Get screen dimensions
img = ImageGrab.grab()
width, height = img.size

# Setup the page and sidebar
st.set_page_config(layout="centered")
data = None
secondThread = None

# These two functions start the lane detection
def SecondThread():
    browser = webbrowser.get("windows-default")
    browser.args = ["--app"]
    browser.open("http://localhost:8501")
    time.sleep(0.1)
    import MainFile
   
secondThread = threading.Thread(target=SecondThread)
secondThread.start()
# Function to change settings in the json file
def UpdateSettings(category, name, data):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    settings[category][name] = data
    with open("settings.json", "w") as f:
        f.truncate(0)
        json.dump(settings, f, indent=4)


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


# Update the json data
def UpdateData():
    global data
    try:
        f = open("interface.json", "r")
        data = json.load(f)
        f.close()
    except:
        pass

UpdateData()


# Close the app gracefully
def CloseApplication():
    UpdateInterface("close", True)
    time.sleep(0.5)
    UpdateInterface("close", False)
    chrome.quit()
    exit()

def AddLines(number, base):
    for i in range(number):
        base.write("")


# Main Control page
st.title("Control panel")
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
general.button("HQ Preview", on_click=ChangeBoolInInterface, args=["HQPreview"])
if data["HQPreview"]:
    general.success("High Quality Preview is enabled")
else:
    general.error("High Quality Preview is disabled")
general.info("You will also have to close the prompt, when closing the program.")
general.button("Close Application", on_click=CloseApplication)
# Video options
video.info("Screen dimensions are {}x{}".format(width, height))
desiredWidth = video.number_input("Video Width", min_value=0, max_value=width, args=["videoWidth"])
desiredHeight = video.number_input("Video Height", min_value=0, max_value=height, args=["videoHeight"])
AddLines(4, video)
video.info("Max values are {}x{}".format(width-desiredWidth, height-desiredHeight))
desiredX = video.number_input("Video X", min_value=0, max_value=width-desiredWidth, args=["videoX"])
desiredY = video.number_input("Video Y", min_value=0, max_value=height-desiredHeight, args=["videoY"])
AddLines(4, video)
video.info("DirectX is a brand new api utilizing windows specific features.\nFor compatibility reasons, I have left in MSS even though it is slower.\nFPS selector is not available for MSS.")
screenCaptureMode = video.selectbox("Screen Capture Mode", ["DirectX (Windows, higher performace)", "MSS (Linux / Mac compatible)"], args=["screenCaptureMode"])
if screenCaptureMode == "DirectX (Windows, higher performace)":
    desiredFPS = video.number_input("Desired FPS", min_value=1, max_value=60, args=["desiredFPS"])
    UpdateSettings("screenCapture", "useDirectX", True)
    UpdateSettings("screenCapture", "DXframerate", desiredFPS)
else:
    desiredFPS = video.number_input("Desired FPS", min_value=1, max_value=60, args=["desiredFPS"], disabled=True)
    UpdateSettings("screenCapture", "useDirectX", False)
video.info("You will have to restart the application after changing the screen capture mode.")
# Model options
model.title("Model")
# Controls options
controls.title("Controls")
