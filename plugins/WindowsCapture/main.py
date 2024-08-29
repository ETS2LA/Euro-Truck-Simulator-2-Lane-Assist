from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="WindowsCapture", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="Will use the windows APIs to capture the screen.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="image capture", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="ScreenCapture" # Will disable the other screen capture plugins
)

from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import src.settings as settings
import src.helpers as helpers
import tkinter as tk

def CreateCamera():
    global monitor
    global capture
    global control

    x = settings.GetSettings("bettercam", "x", 0)
    y = settings.GetSettings("bettercam", "y", 0)
    width = settings.GetSettings("bettercam", "width", 1920)
    height = settings.GetSettings("bettercam", "height", 1080)
    display = settings.GetSettings("bettercam", "display", 0)

    monitor = (x, y, x + width - 1, y + height - 1)

    capture = WindowsCapture(
        cursor_capture=False,
        draw_border=False,
        monitor_index=display + 1,
        window_name=None,
    )
    global LatestFrame
    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        global LatestFrame
        LatestFrame = frame.convert_to_bgr().frame_buffer.copy()
    @capture.event
    def on_closed():
        print("Capture Session Closed")
    try:
        control.stop()
    except:
        pass
    control = capture.start_free_threaded()
CreateCamera()


def plugin(data):
    try:
        data["frameFull"] = LatestFrame
        # Crop the frame to the selected area
        frame = LatestFrame[monitor[1]:monitor[3], monitor[0]:monitor[2]]
        data["frame"] = frame
        data["frameOriginal"] = frame
    except Exception as ex:
        print(ex)
    return data

# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    CreateCamera()

def onDisable():
    control.stop()


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
            helpers.MakeLabel(self.root, "Please use the BetterCam Screen Capture settings!", 0,0, font=("Roboto", 15, "bold"), padx=30, pady=10, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def tabFocused(self): # Called when the tab is focused
            pass
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)