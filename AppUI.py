import tkinter as tk
from tkinter import Toplevel, ttk, messagebox
import sv_ttk
import os
import settingsInterface as settings
from ttkwidgets import color
import MainFile
import time

def OnClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        MainFile.close = True
        root.destroy()


modelPath = "models"
models = []
def LoadModels():
    global models

    for file in os.listdir(modelPath):
        if file.endswith(".pth"):
            models.append(file.replace(".pth", "").replace("_", " ").capitalize())

LoadModels()

def MakeButton(parent, text, command, row, column, style="TButton", width=15):
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width)
    button.grid(row=row, column=column, padx=5, pady=5)
    return button
    
def MakeCheckButton(parent, text, category, setting, row, column, width=17):
    variable = tk.BooleanVar()
    variable.set(settings.GetSettings(category, setting))
    button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.UpdateSettings(category, setting, variable.get()), width=width)
    button.grid(row=row, column=column, padx=0, pady=7, sticky="w")
    return variable

def MakeComboEntry(parent, text, category, setting, row, column, width=10, isFloat=False):
    if not isFloat:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.IntVar()
        var.set(int(settings.GetSettings(category, setting)))
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.UpdateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var
    else:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.DoubleVar()
        var.set(float(settings.GetSettings(category, setting)))
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.UpdateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var

def UpdateModelSettings():
    # Model
    settings.UpdateSettings("modelSettings", "modelType", "tusimple" if "tusimple" in model.get().lower() else "culane")
    settings.UpdateSettings("modelSettings", "modelPath", modelPath + "/" + model.get().lower().replace(" ", "_") + ".pth")
    settings.UpdateSettings("modelSettings", "modelDepth", ''.join(filter(str.isdigit, model.get().lower())))
    settings.UpdateSettings("modelSettings", "useGPU", useGPU.get())
    print("New model : " + model.get().lower())


def UpdateAllSettings():
    SaveSettings("somethingsomething")
    UpdateModelSettings()
    MainFile.LoadSettings()
    MainFile.ChangeControllerSettingsFromFile()

def ChangeWindowSize(): # Between full, and minimized state
    if(f"{fullWidth}x{fullHeight}" in root.geometry()):
        root.geometry(f"{miniWidth}x{miniHeight}")
        sizeButton.config(text="Maximize")
    else:
        root.geometry(f"{fullWidth}x{fullHeight}")
        sizeButton.config(text="Minimize")

def ToggleEnabled():
    if not MainFile.enabled:
        toggleButton.config(text="Starting...")
        root.update()
        MainFile.ToggleEnable()
        toggleButton.config(text="Disable")
    else:
        MainFile.ToggleEnable()
        toggleButton.config(text="Enable")

# Main window size
fullWidth = 785
fullHeight = 750

miniWidth = 217
miniHeight = 350

# This initializes the Main UI tkinter window
root = tk.Tk() # The main window
root.geometry(str(fullWidth) + "x" + str(fullHeight))
big_frame = ttk.Frame(root) # A frame in that window
big_frame.pack(fill="both", expand=True, padx=20, pady=10)
# Set grid paddings
big_frame.grid_columnconfigure(0, pad=20)
big_frame.grid_columnconfigure(1, pad=20)
big_frame.grid_rowconfigure(0, pad=20)
big_frame.grid_rowconfigure(1, pad=20)

# Main control frame
top_left = ttk.LabelFrame(big_frame, height=400, padding=15, text="Controls")
top_left.grid(row=0, column=0, sticky="nw")

# Add 5 buttons to the top left window
toggleButton = MakeButton(top_left, "Enable", lambda: ToggleEnabled(), 0, 0, style="Accent.TButton")
MakeButton(top_left, "Toggle Preview", lambda: MainFile.TogglePreview(), 1, 0)
sizeButton = MakeButton(top_left, "Minimize", lambda: ChangeWindowSize(), 2, 0)
MakeButton(top_left, "Update Settings", UpdateAllSettings, 3, 0)
MakeButton(top_left, "Color Picker", lambda: color.ColorPicker(root, color=settings.GetSettings("generalSettings", "laneColor")), 4, 0)

# Bottom left model selector
bottom_left = ttk.LabelFrame(big_frame, height=390, padding=15, text="Model Selector")
bottom_left.grid(row=1, column=0, sticky="nw")

MakeButton(bottom_left, "Load Model", UpdateModelSettings, 0, 0, style="Accent.TButton")
MakeButton(bottom_left, "Refresh Models", LoadModels, 1, 0)

model = ttk.Combobox(bottom_left, width=14, values=models)
model.set(settings.GetSettings("modelSettings", "modelPath").replace(".pth", "").replace("_", " ").replace("models/", "").capitalize())
model.grid(row=2, column=0, sticky="w", padx=7, pady=7)

useGPU = tk.BooleanVar()
useGPU.set(bool(settings.GetSettings("modelSettings", "useGPU")))
ttk.Checkbutton(bottom_left, text="Use GPU", variable=useGPU, onvalue=True, offvalue=False).grid(row=3, column=0, sticky="w", padx=7, pady=7)

# Preview customizations (top center)
top_center = ttk.LabelFrame(big_frame, height=400, padding=15, text="Preview Customizations")
top_center.grid(row=0, column=1, sticky="nw")

ttk.Label(top_center, text="* Impact on performance", width=25).grid(row=0, column=0, sticky="w")
previewOnTop = MakeCheckButton(top_center, "Preview on Top", "generalSettings", "previewOnTop", 1, 0)
computeGreenDots = MakeCheckButton(top_center, "Green Dots *", "generalSettings", "computeGreenDots", 2, 0)
drawSteeringLine = MakeCheckButton(top_center, "Draw Steering Line", "generalSettings", "drawSteeringLine", 3, 0)
showLanePoints = MakeCheckButton(top_center, "Show Lane Points *", "generalSettings", "showLanePoints", 4, 0)
fillLane = MakeCheckButton(top_center, "Fill Lane *", "generalSettings", "fillLane", 5, 0)


ttk.Label(top_center, text="Lane Color HTML (Color Picker)").grid(row=6, column=0, sticky="w", padx=7, pady=7)
laneColor = tk.StringVar()
laneColor.set(settings.GetSettings("generalSettings", "laneColor"))
ttk.Entry(top_center, textvariable=laneColor, width=29).grid(row=7, column=0, sticky="w", padx=7, pady=7)

# Screen Capture Settings (bottom center)
bottom_center = ttk.LabelFrame(big_frame, height=390, padding=15, text="Screen Capture Settings")
bottom_center.grid(row=1, column=1, sticky="nw")

width = MakeComboEntry(bottom_center, "Width", "screenCapture", "width", 0, 0)
height = MakeComboEntry(bottom_center, "Height", "screenCapture", "height", 1, 0)
x = MakeComboEntry(bottom_center, "X", "screenCapture", "x", 2, 0)
y = MakeComboEntry(bottom_center, "Y", "screenCapture", "y", 3, 0)
useDirectX = MakeCheckButton(bottom_center, "Use DX (win)", "screenCapture", "useDirectX", 4, 0, width=11)
DXframerate = MakeComboEntry(bottom_center, "DX Framerate", "screenCapture", "DXframerate", 5, 0)

# Controller settings (top right)
top_right = ttk.LabelFrame(big_frame, height=100, padding=15, text="Controller Settings")
top_right.grid(row=0, column=2, sticky="nw")

experimentalLogitechSupport = MakeCheckButton(top_right, "Exp. Logitech Support", "controlSettings", "experimentalLogitechSupport", 0, 0, width=20)

ttk.Label(top_right, text="Controller: ").grid(row=1, column=0, sticky="w", pady=7)

controller = ttk.Combobox(top_right, width=6, values=MainFile.joystickNames)
controller.set(MainFile.joystickNames[settings.GetSettings("controlSettings", "defaultControllerIndex")])
controller.grid(row=1, column=1, sticky="w", padx=7, pady=7)

steeringAxis = MakeComboEntry(top_right, "Steering Axis", "controlSettings", "steeringAxis", 4, 0)
enableDisableButton = MakeComboEntry(top_right, "Toggle Button", "controlSettings", "enableDisableButton", 5, 0)
rightIndicator = MakeComboEntry(top_right, "Right Indicator", "controlSettings", "rightIndicator", 6, 0)
leftIndicator = MakeComboEntry(top_right, "Left Indicator", "controlSettings", "leftIndicator", 7, 0)
wheelAngle = ttk.Scale(top_right, from_=-100, to=100, orient=tk.HORIZONTAL, length=150).grid(row=8, column=0, sticky="w", padx=7, pady=7)
ttk.Label(top_right, text="Wheel angle").grid(row=8, column=1, sticky="w", padx=7 , pady=7)

# Control settings (bottom right)
bottom_right = ttk.LabelFrame(big_frame, height=390, padding=15, text="Control Settings")
bottom_right.grid(row=1, column=2, sticky="nw")

disableLaneAssistWhenIndicating = MakeCheckButton(bottom_right, "Disable When Indi...", "controlSettings", "disableLaneAssistWhenIndicating", 0, 0)
steeringOffset = MakeComboEntry(bottom_right, "Steering Offset", "controlSettings", "steeringOffset", 1, 0)
sensitivity = MakeComboEntry(bottom_right, "Sensitivity", "controlSettings", "sensitivity", 2, 0)
maximumControl = MakeComboEntry(bottom_right, "Maximum Control", "controlSettings", "maximumControl", 3, 0, isFloat=True)
controlSmoothness = MakeComboEntry(bottom_right, "Control Smooth...", "controlSettings", "controlSmoothness", 4, 0)


# Set themes and closing callback
sv_ttk.set_theme("dark")
root.protocol("WM_DELETE_WINDOW", OnClosing)
root.title("ETS2 Lane Assist")

def SaveSettings(something):
    settings.UpdateSettings("generalSettings", "laneColor", laneColor.get())
    settings.UpdateSettings("screenCapture", "width", width.get())
    settings.UpdateSettings("screenCapture", "height", height.get())
    settings.UpdateSettings("screenCapture", "x", x.get())
    settings.UpdateSettings("screenCapture", "y", y.get())
    settings.UpdateSettings("screenCapture", "DXframerate", DXframerate.get())
    settings.UpdateSettings("controlSettings", "defaultControllerIndex", MainFile.joystickNames.index(controller.get()))
    settings.UpdateSettings("controlSettings", "steeringAxis", steeringAxis.get())
    settings.UpdateSettings("controlSettings", "enableDisableButton", enableDisableButton.get())
    settings.UpdateSettings("controlSettings", "rightIndicator", rightIndicator.get())
    settings.UpdateSettings("controlSettings", "leftIndicator", leftIndicator.get())
    settings.UpdateSettings("controlSettings", "steeringOffset", steeringOffset.get())
    settings.UpdateSettings("controlSettings", "sensitivity", sensitivity.get())
    settings.UpdateSettings("controlSettings", "maximumControl", maximumControl.get())
    settings.UpdateSettings("controlSettings", "controlSmoothness", controlSmoothness.get())
    print("\033[92mSuccessfully saved settings \033[00m")

# Bind the enter key to save settings
root.bind('<Return>', SaveSettings)

while True:
    MainFile.mainFileLoop()
    wheelAngle = MainFile.desiredControl
    root.update()
