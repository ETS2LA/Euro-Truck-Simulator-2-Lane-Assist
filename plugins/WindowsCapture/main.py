from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="WindowsCapture", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will use the windows APIs to capture the screen.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="ScreenCapture" # Will disable the other screen capture plugins
)

from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import src.settings as settings
import src.helpers as helpers
from tkinter import ttk
import tkinter as tk
import time
import cv2
import sys

# Every Error From on_closed and on_frame_arrived Will End Up Here
index = settings.GetSettings("bettercam", "display", 0)
if index == None:
    settings.CreateSettings("bettercam", "display", 0)
    index = 0
    
capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    monitor_index=index+1, # Starts from 1
    window_name=None,
)

monitor = (0, 0, 1920, 1080)
def LoadSettings():
    global monitor
    
    width = settings.GetSettings("bettercam", "width")
    if width == None:
        settings.CreateSettings("bettercam", "width", 1920)
        width = 1920

    height = settings.GetSettings("bettercam", "height")
    if height == None:
        settings.CreateSettings("bettercam", "height", 1080)
        height = 1080
        
    x = settings.GetSettings("bettercam", "x")
    if x == None:
        settings.CreateSettings("bettercam", "x", 0)
        x = 0

    y = settings.GetSettings("bettercam", "y")
    if y == None:
        settings.CreateSettings("bettercam", "y", 0)
        y = 0
        
    monitor = (x, y, x + width, y + height)

# Called Every Time A New Frame Is Available
lastFrameTime = time.time()
lastFrame = None
currentFrame = None
usingFrame = False
fpsValues = []
@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global lastFrameTime, lastFrame, usingFrame, currentFrame
    
    if not usingFrame:
        currentFrame = frame
        lastFrame = frame.convert_to_bgr().frame_buffer
        fpsValues.append(1 / (time.time() - lastFrameTime))
        while len(fpsValues) > 100:
            fpsValues.pop(0)
        sys.stdout.write(f"FPS: {round(sum(fpsValues) / len(fpsValues), 2)}            \r")
        lastFrameTime = time.time()

# Called When The Capture Item Closes Usually When The Window Closes, Capture
# Session Will End After This Function Ends
@capture.event
def on_closed():
    print("Capture Session Closed")

def plugin(data):
    global usingFrame
    LoadSettings()
    try:
        usingFrame = True
        data["frameFull"] = lastFrame
        # Crop the frame to the selected area
        frame = lastFrame[monitor[1]:monitor[3], monitor[0]:monitor[2]]
        data["frame"] = frame
        data["frameOriginal"] = frame
        usingFrame = False
    except Exception as ex:
        print(ex)
    
    return data

# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    global control
    control = capture.start_free_threaded()
    pass

def onDisable():
    control.stop()
    pass

# Plugins can also have UIs, this works the same as the panel example
class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            helpers.MakeLabel(self.root, "Please use the BetterCam Screen Capture settings!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def tabFocused(self): # Called when the tab is focused
            pass
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)