"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print


PluginInfo = PluginInformation(
    name="DXCamScreenCapture", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="The default way to capture the screen.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before lane detection", # Will run the plugin before anything else in the mainloop (data will be empty)
    exclusive="ScreenCapture" # Will disable the other screen capture plugins
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import dxcam

def onEnable():
    CreateCamera()
    pass

def onDisable():
    pass

def CreateCamera():
    global camera
    
    width = settings.GetSettings("dxcam", "width")
    if width == None:
        settings.CreateSettings("dxcam", "width", 1280)
        width = 1280

    height = settings.GetSettings("dxcam", "height")
    if height == None:
        settings.CreateSettings("dxcam", "height", 720)
        height = 720
        
    x = settings.GetSettings("dxcam", "x")
    if x == None:
        settings.CreateSettings("dxcam", "x", 0)
        x = 0

    y = settings.GetSettings("dxcam", "y")
    if y == None:
        settings.CreateSettings("dxcam", "y", 0)
        y = 0

    display = settings.GetSettings("dxcam", "display")
    if display == None:
        settings.CreateSettings("dxcam", "display", 0)
        display = 0

    device = settings.GetSettings("dxcam", "device")
    if device == None:
        settings.CreateSettings("dxcam", "device", 0)
        device = 0

    left, top = x, y
    right, bottom = left + width, top + height

    from tkinter import messagebox
    import screeninfo
    try:
        screen = screeninfo.get_monitors()[settings.GetSettings("dxcam", "display")]
    except:
        screen = screeninfo.get_monitors()[0]
        
    screenWidth = int(screen.width)
    screenHeight = int(screen.height)
    
    # Check if these values would go over the screen edges
    if right > screenWidth:
        right = screenWidth
        messagebox.showwarning("Warning", "The width value is too high, it has been lowered to {}".format(right))
    
    if bottom > screenHeight:
        bottom = screenHeight
        messagebox.showwarning("Warning", "The height value is too high, it has been lowered to {}".format(bottom))
    
    if left < 0:
        left = 0
        
    if top < 0:
        top = 0
        
    monitor = (left,top,right,bottom)
        
    
    try:
        del camera
    except: pass
    
    camera = dxcam.create(region=monitor, output_color="BGR", output_idx=display, device_idx=device)
        



# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
def plugin(data):
    
    try:
        if camera != None:
            pass
    except:
        CreateCamera()
    
    try:
        frame = camera.grab()
        data["frame"] = frame
        return data
    except Exception as ex:
        print(ex)
        return data
    


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
            
            self.root = tk.Canvas(self.master, width=600, height=520)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            import screeninfo
            
            try:
                screen = screeninfo.get_monitors()[settings.GetSettings("dxcam", "display")]
            except:
                screen = screeninfo.get_monitors()[0]
                
            self.screenHeight = int(screen.height)
            self.screenWidth = int(screen.width)
            
            def updateWidth(value):
                self.width.set(value)
                self.xSlider.config(to=self.screenWidth - int(value))
                
            def updateHeight(value):
                self.height.set(value)
                self.ySlider.config(to=self.screenHeight - int(value))
            
            def updateX(value):
                self.x.set(value)
                
            def updateY(value):
                self.y.set(value)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            self.widthSlider = tk.Scale(self.root, from_=0, to=self.screenWidth, orient=tk.HORIZONTAL, length=500, command=lambda x: updateWidth(self.widthSlider.get()))
            self.widthSlider.set(settings.GetSettings("dxcam", "width"))
            self.widthSlider.grid(row=0, column=0, padx=10, pady=0, columnspan=2)
            self.width = helpers.MakeComboEntry(self.root, "Width", "dxcam", "width", 1,0)
            
            self.heightSlider = tk.Scale(self.root, from_=0, to=self.screenHeight, orient=tk.HORIZONTAL, length=500, command=lambda x: updateHeight(self.heightSlider.get()))
            self.heightSlider.set(settings.GetSettings("dxcam", "height"))
            self.heightSlider.grid(row=2, column=0, padx=10, pady=0, columnspan=2)
            self.height = helpers.MakeComboEntry(self.root, "Height", "dxcam", "height", 3,0)
            
            self.xSlider = tk.Scale(self.root, from_=0, to=self.screenWidth - self.width.get(), orient=tk.HORIZONTAL, length=500, command=lambda x: updateX(self.xSlider.get()))
            self.xSlider.set(settings.GetSettings("dxcam", "x"))
            self.xSlider.grid(row=4, column=0, padx=10, pady=0, columnspan=2)
            self.x = helpers.MakeComboEntry(self.root, "X", "dxcam", "x", 5,0)
            
            self.ySlider = tk.Scale(self.root, from_=0, to=self.screenHeight - self.height.get(), orient=tk.HORIZONTAL, length=500, command=lambda x: updateY(self.ySlider.get()))
            self.ySlider.set(settings.GetSettings("dxcam", "y"))
            self.ySlider.grid(row=6, column=0, padx=10, pady=0, columnspan=2)
            self.y = helpers.MakeComboEntry(self.root, "Y", "dxcam", "y", 7,0)
            self.display = helpers.MakeComboEntry(self.root, "Display", "dxcam", "display", 8,0, value=0)
            
            self.device = helpers.MakeComboEntry(self.root, "Device", "dxcam", "device", 9,0, value=0)
            
            helpers.MakeButton(self.root, "Apply", lambda: self.updateSettings(), 10,0)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def updateSettings(self):
            settings.CreateSettings("dxcam", "width", self.width.get())
            settings.CreateSettings("dxcam", "height", self.height.get())
            settings.CreateSettings("dxcam", "x", self.x.get())
            settings.CreateSettings("dxcam", "y", self.y.get())
            settings.CreateSettings("dxcam", "display", self.display.get())
            settings.CreateSettings("dxcam", "device", self.device.get())
            CreateCamera()
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)