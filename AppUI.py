import json
import streamlit as st
import threading
import time
import sys


# Setup the page and sidebar
st.set_page_config(layout="wide")
mode = st.sidebar.selectbox("Select mode", ["Information", "App Control Panel", "Show JSON", "Show UI Source code"])
data = None
image = None
secondThread = None

# These two functions start the lane detection
def SecondThread():
    global image
    import MainFile
    

secondThread = threading.Thread(target=SecondThread)
secondThread.daemon = True
secondThread.start()

# Function to change settings in the json file
def UpdateSettings(name, data, category):
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

def ChangeBoolInInterface(name):
    if data[name] == True:
        UpdateInterface(name, False)
    else:
        UpdateInterface(name, True)

# Update the json data
def UpdateData():
    global data
    with open("interface.json", "r") as f:
        data = json.load(f)

UpdateData()

# Close the app gracefully
def CloseApplication():
    UpdateInterface("close", True)
    time.sleep(0.5)
    UpdateInterface("close", False)
    exception = st.exception(RuntimeError("You must close the command prompt to close the app."))
    raise exception

# Information page
if mode == "Information":
    col1, col2 = st.columns(2)
    col2.image("LaneAssistLogoWide.jpg")
    col1.title("Information")
    col1.write("You can find the github source code for the app here https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist")

# Main Page
elif mode == "App Control Panel":
    st.title("Control panel")
    sideBar, preview = st.columns([1, 3])
    general, video, model, controls = sideBar.tabs(["General", "Video", "Model", "Controls"])
    
    try:
        with open("interface.json", "r") as f:
            if json.load(f)["preview"] == False:
                preview.error("Preview is disabled")
            else:
                preview.image("temp.png")
    except Exception as e:
        pass

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

    general.button("Close Application", on_click=CloseApplication)

    # Video options
    video.title("Video")

    # Model options
    model.title("Model")

    # Controls options
    controls.title("Controls")

# JSON page
elif mode == "Show JSON":
    st.title("Settings.json")
    st.write("You cannot edit the file here, edit the file directly in a text editor.")
    st.json(json.load(open("settings.json")))

# UI Source code page
elif mode == "Show UI Source code":
    st.title("Show UI Source code")
    st.write("This is a Streamlit app")

# Main Loop
while True:
    time.sleep(0.5)
    UpdateData()
    st.experimental_rerun()