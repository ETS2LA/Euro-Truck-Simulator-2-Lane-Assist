from plugins.plugin import PluginInformation

PluginInfo = PluginInformation(
    name="FirstTimeSetup",
    description="Will help you get the app up and running!",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static",
    image="image.png",
    disablePlugins=True
)


import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
from src.mainUI import quit
from PIL import Image, ImageTk
import src.variables as variables
import os
import pygame
import src.settings as settings
import cv2
import plugins.TruckSimAPI.main as api
import webview

try:
    import dxcam
except:
    dxcam = None

pygame.display.init()
pygame.joystick.init()


class UI():
    
    def destroy(self):
        self.done = True
        self.root.destroy()
        del self
    
    try:
        
        def __init__(self, master) -> None:
            self.done = False
            self.master = master
            self.waitForAPI = False
            self.page0()
        
        def page0(self):
            
            try:
                self.root.destroy()
            except: pass
            
            self.root = tk.Canvas(self.master)
            
            settings.CreateSettings("Plugins", "Enabled", ["TruckersMPLock"])
            
            helpers.MakeLabel(self.root, "Welcome", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "This setup will automatically configure the OFFICIAL plugins. ", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "If you have any other plugins installed, please configure them manually.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)

            helpers.MakeButton(self.root, "Quit", lambda: quit(), 3,0)
            # REMEMBER TO CHANGE BACK TO PAGE1
            helpers.MakeButton(self.root, "Next", lambda: self.detectionselection(), 3,1)
            
            helpers.MakeButton(self.root, "Tutorial Video", lambda: helpers.OpenWebView("Tutorial","plugins/FirstTimeSetup/tutorialEmbed.html", width=1290, height=730), 3,2)

            # Load the logo
            self.logo = Image.open(os.path.join(variables.PATH, "assets", "firstTimeSetup", "logo.jpg"))
            height = 320
            width = round(height * 1.665)
            self.logo = self.logo.resize((width, height), resample=Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.logo)
            self.logoLabel = tk.Label(self.root, image=self.logo)
            self.logoLabel.grid(row=4, column=0, columnspan=3, pady=10, padx=30)

            self.root.pack(anchor="center")
            
            self.root.update()
        

        def detectionselection(self):
            def openwiki():
                    webview.create_window("Lane Assist Wiki", "https://wiki.tumppi066.fi/en/LaneAssist/DetectionTypes")
                    webview.start()
            self.root.destroy()
            del self.root
            self.root = tk.Canvas(self.master)
            helpers.MakeLabel(self.root, "Select which type of lane detection you want to use", 0,0, font=("Roboto", 15, "bold"), padx=30, pady=10, columnspan=3,)
            helpers.MakeLabel(self.root, "TLDR: LSTR is the reccomeneded model for most people.", 1,0, font=("Segoe UI", 12), padx=30, pady=0, columnspan=3)
            ttk.Label(self.root, text="").grid(columnspan=3, row=2, column=0, ipadx=0, ipady=0, pady=0)
            helpers.MakeLabel(self.root, "If you want to see all the options, it is reccomended to check the Wiki", 3,0, font=("Segoe UI", 10), padx=30, pady=2, columnspan=3)
            helpers.MakeLabel(self.root, "to see what the best option for you is.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            ttk.Label(self.root, text="").grid(columnspan=3, row=5, column=0, ipadx=0, ipady=0, pady=0)
            global detectionmethod
            detectionmethod = tk.StringVar()
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="LSTR Lane Detection (Recomended)", value="lstr").grid(columnspan=3, row=6, column=0, sticky='w', padx=5, pady=5)
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="UFLD Lane Detection (Only for use with Nvidia GPU > GTX 1060)", value="ufld").grid(columnspan=3, row=7, column=0, sticky='w', padx=5, pady=5)
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="Navigation Detection (Uses the minimap for lane detection)", value="nav").grid(columnspan=3, row=8, column=0, sticky='w', padx=5, pady=5)
            detectionmethod.set("lstr")
            ttk.Label(self.root, text="").grid(columnspan=3, row=9, column=0, ipadx=0, ipady=0, pady=0)
            
            def detectionsettings():
                if detectionmethod.get() == "lstr":
                    print("LSTR Selected")
                    settings.AddToList("Plugins", "Enabled", ["LSTRDrawLanes"])
                    settings.AddToList("Plugins", "Enabled", ["LSTRLaneDetection"])
                elif detectionmethod.get() == "ufld":
                    print("UFLD Selected")
                    settings.AddToList("Plugins", "Enabled", ["UFLDrawLanes"])
                    settings.AddToList("Plugins", "Enabled", ["UFLDLaneDetection"])
                elif detectionmethod.get() == "nav":
                    settings.AddToList("Plugins", "Enabled", ["NavigationDetection"])
                else:
                    print("Please select a detection method")
                    return
                self.page1()
            
            helpers.MakeButton(self.root, "Back", lambda: self.page0(), 10,0)
            helpers.MakeButton(self.root, "Wiki", openwiki, 10,1)
            helpers.MakeButton(self.root, "Confirm", detectionsettings, 10,2)
            self.root.pack()

        def page1(self):
            self.root.destroy()
            del self.root
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Select your controller type", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "First I'm going to ask you about your controller.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "So please select the correct control type that you want to use.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)        

            helpers.MakeButton(self.root, "Gamepad", lambda: self.gamepadPage(), 3,0)
            helpers.MakeButton(self.root, "Wheel", lambda: self.wheelPage(), 3,1)
            helpers.MakeButton(self.root, "Keyboard", lambda: self.keyboardPage(), 3,2)
            helpers.MakeButton(self.root, "Back", lambda: self.detectionselection(), 4,1)
            
            self.root.pack()
            
            
        def gamepadPage(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            settings.CreateSettings("DefaultSteering", "gamepad", True)
            settings.CreateSettings("DefaultSteering", "gamepadSmoothness", 0.05)

            helpers.MakeLabel(self.root, "Gamepad", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Great! I'll automatically set all the necessary options for gamepad usage.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "Just be aware that you will have to set the controller type to 'wheel' in the game.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)        
            helpers.MakeLabel(self.root, "Don't worry there will be instructions later! For now please select your controller from the list below.", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)

            pygame.event.pump()

            self.joysticks = pygame.joystick.get_count()
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(self.joysticks)]
            
            self.listVariable = tk.StringVar(self.root)
            self.listVariable.set([j.get_name() for j in self.joysticks])
            
            self.list = tk.Listbox(self.root, width=70, height=4, listvariable=self.listVariable, selectmode="single")
            self.list.grid(row=6, column=0, columnspan=2, padx=30, pady=10)

            helpers.MakeLabel(self.root, "The list is scrollable, if you can't find your controller then go back and open the page again.", 7,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)

            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 8,0)
            helpers.MakeButton(self.root, "Next", lambda: self.axisSetup(), 8,1)

            self.root.pack()
            
            
        def wheelPage(self):
            
            settings.CreateSettings("DefaultSteering", "gamepad", False)
            settings.CreateSettings("DefaultSteering", "gamepadsmoothness", 0.05)
            
            from plugins.DefaultSteering.main import updateSettings
            updateSettings()
            
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Wheel", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Great! Using a wheel has the most straight forward setup process.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
            helpers.MakeLabel(self.root, "Please select your wheel from the list below.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)

            pygame.event.pump()

            self.joysticks = pygame.joystick.get_count()
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(self.joysticks)]
            
            self.listVariable = tk.StringVar(self.root)
            self.listVariable.set([j.get_name() for j in self.joysticks])
            
            self.list = tk.Listbox(self.root, width=70, height=4, listvariable=self.listVariable, selectmode="single")
            self.list.grid(row=3, column=0, columnspan=2, padx=30, pady=10)

            helpers.MakeLabel(self.root, "The list is scrollable, if you can't find your controller then go back and open the page again.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)

            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 5,0)
            helpers.MakeButton(self.root, "Next", lambda: self.axisSetup(), 5,1)

            self.root.pack()
            
            
        def keyboardPage(self):
            
            settings.CreateSettings("DefaultSteering", "keyboard", True)
            settings.CreateSettings("DefaultSteering", "gamepad", False)
            settings.CreateSettings("DefaultSteering", "gamepadsmoothness", 0.05)
            
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Keyboard", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Great! Just a warning, keyboard support is VERY EXPERIMENTAL.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "There might be issues but it will get updates along the way.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
            helpers.MakeLabel(self.root, "You can use the A and D key to move the wheel, and by default the", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
            helpers.MakeLabel(self.root, "N key for toggling, and E and Q as the blinker keys.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)      

            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 5,0)
            if dxcam != None:
                helpers.MakeButton(self.root, "Next", lambda: self.screenCaptureSetup(), 5,1)
            else:
                helpers.MakeButton(self.root, "Next", lambda: self.laneDetectionFeatures(), 5,1)

            self.root.pack()
            
        
        def axisSetup(self):
            
            import src.settings as settings
            settings.CreateSettings("DefaultSteering", "controller", self.list.curselection()[0])
            settings.CreateSettings("DefaultSteering", "controller name", self.joysticks[self.list.curselection()[0]].get_name())
            
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Axis Setup", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Now we are going to detect the different axis' on your controller.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
            helpers.MakeLabel(self.root, "So please go ahead and select the axis corresponding to steering from the below list.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
            
            # Create sliders for all axis
            index = settings.GetSettings("DefaultSteering", "controller")
            self.sliderVars = []
            for i in range(self.joysticks[index].get_numaxes()):
                variable = tk.IntVar(self.root)
                helpers.MakeCheckButton(self.root, f"Axis {i}", "DefaultSteering", f"steeringAxis", i+4, 1, values=[i, ""], onlyTrue=True)
                slider = tk.Scale(self.root, from_=-1, to=1, variable=variable, orient=tk.HORIZONTAL, length=200, resolution=0.01)
                self.sliderVars.append(variable)
                slider.grid(row=i+4, column=0, padx=0, pady=5)
            

            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 10,0)
            helpers.MakeButton(self.root, "Next", lambda: self.buttonSetup(), 10,1)

            self.root.pack()
            
        def buttonSetup(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Button Setup", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Then for the buttons.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
            helpers.MakeLabel(self.root, "Please select the correct button corresponding to each category from the list.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
            
            # Create a notebook for each of the groups (both blinkers, and enable / disable)
            notebook = ttk.Notebook(self.root)
            notebook.grid(row=3, column=0, columnspan=2, padx=30, pady=10)
            
            # leftBlinkerFrame = ttk.Frame(notebook)
            # leftBlinkerFrame.pack()
            # rightBlinkerFrame = ttk.Frame(notebook)
            # rightBlinkerFrame.pack()
            enableDisableFrame = ttk.Frame(notebook)
            enableDisableFrame.pack()
            
            # Get a list of all buttons
            index = settings.GetSettings("DefaultSteering", "controller")
            pygame.event.pump()
            
            buttons = []
            for i in range(self.joysticks[index].get_numbuttons()):
                buttons.append("Button " + str(i))
            
            # Create a combobox for each of the groups
            # leftBlinker = tk.StringVar()
            # rightBlinker = tk.StringVar()
            enableDisable = tk.StringVar()
            
            # self.leftBlinkerCombo = ttk.Combobox(leftBlinkerFrame, textvariable=leftBlinker, width=50)
            # self.leftBlinkerCombo['values'] = buttons
            # self.rightBlinkerCombo = ttk.Combobox(rightBlinkerFrame, textvariable=rightBlinker, width=50)
            # self.rightBlinkerCombo['values'] = buttons
            self.enableDisableCombo = ttk.Combobox(enableDisableFrame, textvariable=enableDisable, width=50)
            self.enableDisableCombo['values'] = buttons
            
            # self.leftBlinkerCombo.pack()
            # self.rightBlinkerCombo.pack()
            self.enableDisableCombo.pack()
            
            # notebook.add(leftBlinkerFrame, text="Left Blinker")
            # notebook.add(rightBlinkerFrame, text="Right Blinker")
            notebook.add(enableDisableFrame, text="Enable / Disable")
            
            helpers.MakeLabel(self.root, "You are currently pressing: ", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            self.pressedButtons = tk.StringVar()
            tk.Label(self.root, textvariable=self.pressedButtons).grid(row=5, column=0, columnspan=2, padx=30, pady=0)

            helpers.MakeButton(self.root, "Previous", lambda: self.axisSetup(), 6,0)
            helpers.MakeButton(self.root, "Next", lambda: self.saveButtonSettings(), 6,1)

            self.root.pack()
            self.root.update()
            
        def saveButtonSettings(self):
            
            # Save the button settings
            # settings.CreateSettings("DefaultSteering", "leftIndicator", int(self.leftBlinkerCombo.get().split(" ")[1]))
            # settings.CreateSettings("DefaultSteering", "rightIndicator", int(self.rightBlinkerCombo.get().split(" ")[1]))
            settings.CreateSettings("DefaultSteering", "enableDisable", int(self.enableDisableCombo.get().split(" ")[1]))
            
            from plugins.DefaultSteering.main import updateSettings
            updateSettings()
            
            if dxcam != None:
                self.screenCaptureSetup()      
            else:
                self.laneDetectionFeatures()
        
        def screenCaptureSetup(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Screen Capture", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "This app will screen capture your screen and detect the lanes on those images.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "For this reason we need to make sure that the location of that screen capture is correct.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)  
            helpers.MakeLabel(self.root, " ", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)       
            helpers.MakeLabel(self.root, "First, select your display below.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 

            # Detect all displays
            dxcamOutput = dxcam.output_info()
            for i in range(0,4):
                # Remove GPU indices
                dxcamOutput = dxcamOutput.replace(f"Device[{i}]", "")
                # Also remove 'rot'?
                dxcamOutput = dxcamOutput.replace(f"Rot:{i}", "")
                
            
            displays = dxcamOutput.split("\n")
            
            displayArray = []
            for display in displays:
                if display != "":
                    display = display.split(":")
                    displayObject = ""
                    # This is extremely ugly but it works
                    displayObject += f'Display{(display[0].replace("Output", "").replace("[", "").replace("]", ""))}'
                    displayObject += f' ({display[2].replace("(", "").replace(")", "").replace(",", "x").replace(" ", "").replace("Primary", "")})'
                    if display[3] == "True":
                        displayObject += " (Primary)"
                    
                    displayArray.append(displayObject)
            
            self.displays = ttk.Combobox(self.root, state="readonly", width=50)
            self.displays['values'] = displayArray
            self.displays.set(displayArray[0])
            
            self.displays.grid(row=5, column=0, columnspan=2, padx=30, pady=10)

            helpers.MakeButton(self.root, "Previous", lambda: self.buttonSetup(), 6,0)
            helpers.MakeButton(self.root, "Next", lambda: self.setScreenCaptureSettings(self.displays.get().split(' ')[1]), 6,1)

            self.root.pack()
            
            
        def startScreenCapture(self, display):
            try:
                self.camera.stop()
                del self.camera
            except: 
                self.camera = dxcam.create(output_color="BGR", output_idx=int(display))
                self.camera.start(target_fps=self.refreshRate.get())
            
        def screenCaptureSetup2(self, ):
            screenIndex = self.displays.get().split(' ')[1]
            
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, f"Screen Capture (Display {screenIndex})", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "Now we need to determine a refreshrate. So use the slider below", 1,0, font=("Segoe UI", 10), padx=30, pady=10, columnspan=3)

            
            self.refreshRate = tk.IntVar(self.root)
            self.refreshRate.set(30)
            self.refreshRateSlider = ttk.Scale(self.root, from_=1, to=60, variable=self.refreshRate, orient=tk.HORIZONTAL, length=200, command=lambda x: self.refreshRateVar.set(f"{self.refreshRate.get()}"))
            self.refreshRateSlider.grid(row=2, column=0, padx=0, pady=5, columnspan=2, sticky="e")
            
            self.refreshRateVar = helpers.MakeLabel(self.root, "", 2,2, font=("Segoe UI", 10), padx=30, pady=0, columnspan=1, sticky="w")
            self.refreshRateVar.set("30")

            helpers.MakeLabel(self.root, "Then use the button below to test that it works.", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "Keep an eye on the CPU usage, make sure the app does not use over ~10-20%.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "Try to move around a window (not the app) and see if it is smooth.", 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            
            helpers.MakeButton(self.root, "Back", lambda: self.screenCaptureSetup(), 6,0)
            helpers.MakeButton(self.root, "Toggle Preview", lambda: self.startScreenCapture(screenIndex), 6,1)
            helpers.MakeButton(self.root, "Next", lambda: self.setScreenCaptureSettings(screenIndex), 6,2)

            
            self.root.pack()
            
        
        def setScreenCaptureSettings(self, display):
            settings.CreateSettings("dxcam", "display", int(display))
            #settings.CreateSettings("Screen Capture", "Refresh Rate", self.refreshRate.get())
            if detectionmethod.get() == "nav":
                self.soundSettings()
            else:
                self.laneDetectionFeatures()
        
        
        def laneDetectionFeatures(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Lane Detection Customization", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "You can skip this part if you are fine with the default look.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)    
            helpers.MakeLabel(self.root, "Below is a list of all default features, and you can change them as you want.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3) 
            
            # Create a notebook for each of the groups (both blinkers, and enable / disable)
            notebook = ttk.Notebook(self.root)
            notebook.grid(row=3, column=0, columnspan=3, padx=30, pady=10)
            
            defaultFrame = ttk.Frame(notebook)
            defaultFrame.pack()
            drawLanesFrame = ttk.Frame(notebook)
            drawLanesFrame.pack()
            drawSteeringLineFrame = ttk.Frame(notebook)
            drawSteeringLineFrame.pack()
            fillLaneFrame = ttk.Frame(notebook)
            fillLaneFrame.pack()
            showLanePointsFrame = ttk.Frame(notebook)
            showLanePointsFrame.pack()
            
            # Default image
            if os.name == "nt":
                ftsPath = r"assets\firstTimeSetup"
            else:
                ftsPath = "assets/firstTimeSetup"
                
            self.defaultImage = Image.open(os.path.join(variables.PATH, ftsPath, "Default.jpg"))
            height = 220
            width = round(height * 1.7777) # 16:9
            self.defaultImage = self.defaultImage.resize((width, height), resample=Image.LANCZOS)
            self.defaultImage = ImageTk.PhotoImage(self.defaultImage)
            
            # Draw lanes image
            self.drawLanesImage = Image.open(os.path.join(variables.PATH, ftsPath, "DrawLanes.jpg"))
            self.drawLanesImage = self.drawLanesImage.resize((width, height), resample=Image.LANCZOS)
            self.drawLanesImage = ImageTk.PhotoImage(self.drawLanesImage)
            
            # Draw steering line image
            self.drawSteeringLineImage = Image.open(os.path.join(variables.PATH, ftsPath, "DrawSteeringLine.jpg"))
            self.drawSteeringLineImage = self.drawSteeringLineImage.resize((width, height), resample=Image.LANCZOS)
            self.drawSteeringLineImage = ImageTk.PhotoImage(self.drawSteeringLineImage)
            
            # Fill lane image
            self.fillLaneImage = Image.open(os.path.join(variables.PATH, ftsPath, "FillLane.jpg"))
            self.fillLaneImage = self.fillLaneImage.resize((width, height), resample=Image.LANCZOS)
            self.fillLaneImage = ImageTk.PhotoImage(self.fillLaneImage)
            
            # Show lane points image
            self.showLanePointsImage = Image.open(os.path.join(variables.PATH, ftsPath, "ShowLanePoints.jpg"))
            self.showLanePointsImage = self.showLanePointsImage.resize((width, height), resample=Image.LANCZOS)
            self.showLanePointsImage = ImageTk.PhotoImage(self.showLanePointsImage)
            
            
            # Default page
            helpers.MakeLabel(defaultFrame, "If you don't want to customize anything click the button below.", 0,0, font=("Segoe UI", 10), padx=30, pady=10, sticky="e")
            defaultPageImageLabel = tk.Label(defaultFrame, image=self.defaultImage)
            defaultPageImageLabel.grid(row=1, column=0, pady=10, padx=30, sticky="e")
            
            # Draw lanes page
            helpers.MakeCheckButton(drawLanesFrame, "Draw Lanes", "LSTRDrawLanes", "Draw Lanes", 0, 0)
            drawLanesImageLabel = tk.Label(drawLanesFrame, image=self.drawLanesImage)
            drawLanesImageLabel.grid(row=4, column=0, columnspan=2, pady=10, padx=30)
            
            # Draw steering line page
            helpers.MakeCheckButton(drawSteeringLineFrame, "Draw Steering Line", "LSTRDrawLanes", "Draw Steering Line", 0, 0)
            drawSteeringLineImageLabel = tk.Label(drawSteeringLineFrame, image=self.drawSteeringLineImage)
            drawSteeringLineImageLabel.grid(row=4, column=0, columnspan=2, pady=10, padx=30)
            
            # Fill lane page
            helpers.MakeCheckButton(fillLaneFrame, "Fill Lane", "LSTRDrawLanes", "Fill Lane", 0, 0)
            helpers.MakeComboEntry(fillLaneFrame, "Fill Color", "LSTRDrawLanes", "Fill Color", 1, 0, value="#10615D")
            fillLaneImageLabel = tk.Label(fillLaneFrame, image=self.fillLaneImage)
            fillLaneImageLabel.grid(row=4, column=0, columnspan=2, pady=10, padx=30)
            
            # Show lane points page
            helpers.MakeCheckButton(showLanePointsFrame, "Show Lane Points", "LSTRDrawLanes", "Show Lane Points", 0, 0)
            showLanePointsImageLabel = tk.Label(showLanePointsFrame, image=self.showLanePointsImage)
            showLanePointsImageLabel.grid(row=4, column=0, columnspan=2, pady=10, padx=30)
            
            
            notebook.add(defaultFrame, text="Default")
            notebook.add(drawLanesFrame, text="Draw Lanes")
            notebook.add(drawSteeringLineFrame, text="Draw Steering Line")
            notebook.add(fillLaneFrame, text="Fill Lane")
            notebook.add(showLanePointsFrame, text="Show Lane Points")

            helpers.MakeButton(self.root, "Previous", lambda: self.axisSetup(), 6,0)
            helpers.MakeButton(self.root, "Use Defaults", lambda: self.setLaneDetectionFeatures(True), 6,1)
            helpers.MakeButton(self.root, "Next", lambda: self.setLaneDetectionFeatures(False), 6,2)

            self.root.pack()
            self.root.update()
            
        
        def setLaneDetectionFeatures(self, defaults):
            if defaults:
                settings.CreateSettings("LSTRDrawLanes", "drawLaneLines", True)
                settings.CreateSettings("DefaultSteering", "drawSteeringLine", True)
                settings.CreateSettings("LSTRDrawLanes", "fillLane", True)
                settings.CreateSettings("LSTRDrawLanes", "fillLaneColor", "#10615D")
                settings.CreateSettings("LSTRDrawLanes", "drawLanePoints", False)
            else:
                # Check if the settings exist, if not create them with false values (they weren't toggled once)
                
                try: settings.GetSettings("LSTRDrawLanes", "drawLaneLines")
                except: settings.CreateSettings("LSTRDrawLanes", "drawLaneLines", False)
                
                try: settings.GetSettings("DefaultSteering", "drawSteeringLine")
                except: settings.CreateSettings("DefaultSteering", "drawSteeringLine", False)
                
                try: settings.GetSettings("LSTRDrawLanes", "fillLane")
                except: settings.CreateSettings("LSTRDrawLanes", "fillLane", False)
                
                try: settings.GetSettings("LSTRDrawLanes", "fillLaneColor")
                except: settings.CreateSettings("LSTRDrawLanes", "fillLaneColor", "#10615D")
                
                try: settings.GetSettings("LSTRDrawLanes", "drawLanePoints")
                except: settings.CreateSettings("LSTRDrawLanes", "drawLanePoints", False)
            
            
            from plugins.LSTRDrawLanes.main import loadSettings
            loadSettings()
                
            self.soundSettings()
                    
                    
                    
        def soundSettings(self):
            self.root.destroy()
            settings.CreateSettings("Sound", "enabled", True)
            settings.CreateSettings("Sound", "enable", "assets/sounds/start.mp3")
            settings.CreateSettings("Sound", "disable", "assets/sounds/end.mp3")
            settings.CreateSettings("Sound", "warning", "assets/sounds/warning.mp3")
            
            self.root = tk.Canvas(self.master)
            
            helpers.MakeLabel(self.root, "Sounds", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Almost there!", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
            helpers.MakeLabel(self.root, "If you have custom sounds then place them in the folder and type out the path here.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
            
            helpers.MakeCheckButton(self.root, "Sounds Enabled", "Sound", "enabled", 3, 0)
            self.enable = helpers.MakeComboEntry(self.root, "Enable", "Sound", "enable", 4, 0, value="assets/sounds/start.mp3", width=50, isString=True)
            self.disable = helpers.MakeComboEntry(self.root, "Disable", "Sound", "disable", 5, 0, value="assets/sounds/end.mp3", width=50, isString=True)
            self.warning = helpers.MakeComboEntry(self.root, "Warning", "Sound", "warning", 6, 0, value="assets/sounds/warning.mp3", width=50, isString=True)
            
            helpers.MakeButton(self.root, "Previous", lambda: self.laneDetectionFeatures(), 7,0)
            helpers.MakeButton(self.root, "Next", lambda: self.saveSounds(), 7,1)
            
            self.root.pack()
            self.root.update()
            
        
        def saveSounds(self):
            settings.CreateSettings("Sound", "enable", self.enable.get())
            settings.CreateSettings("Sound", "disable", self.disable.get())
            settings.CreateSettings("Sound", "warning", self.warning.get())
            
            self.ets2APIsetup()
        
        def ets2APIsetup(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)
            self.waitForAPI = True
            
            
            helpers.MakeLabel(self.root, "ETS2 API", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "This app will also connect to your ETS2's / ATS' API and get data about your truck.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "Press the button below to open the instructions (scroll down on the page).\nThe loading window will automatically disappear once connection is established.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
        
            helpers.MakeButton(self.root, "Previous", lambda: self.soundSettings(), 3,0)
            import webbrowser
            helpers.MakeButton(self.root, "Open instructions", lambda: webbrowser.open("https://wiki.tumppi066.fi/en/LaneAssist/InGame"), 3,1)
            self.apiNextButton = helpers.MakeButton(self.root, "Waiting for api...", lambda: self.lastPage(), 3,2, state="disabled")
            
            helpers.MakeLabel(self.root, "Automatic installation", 4,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            
            # Check for ETS2 / ATS directories 
            import plugins.FirstTimeSetup.steamParser as steamParser
            
            self.scsGames = steamParser.FindSCSGames()
                
            foundString = "Found the following games automatically:\n"
            
            for game in self.scsGames:
                foundString += game + ": True\n"
            
            self.gameText = helpers.MakeLabel(self.root, foundString, 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            
            from tkinter import filedialog
            
            self.foundAdditionalDir = False
            def GetAdditionalDir(self):
                self.additionalDir = filedialog.askdirectory()
                # Check the base.scs file exists in that directory
                if os.path.isfile(os.path.join(self.additionalDir, "base.scs")):
                    self.gameText.config(text=foundString + self.additionalDir + ": True")
                    self.foundAdditionalDir = True
                else:
                    self.gameText.config(text=foundString + self.additionalDir + ": False")
                    self.foundAdditionalDir = False
            
            helpers.MakeButton(self.root, "Add game (if not found)", lambda: GetAdditionalDir(self), 6,0, columnspan=3, width=30)
            
            import shutil
            
            def InstallETS2ATSPlugin(self):
                pluginInstallDir = r"bin\win_x64\plugins"
                # Make that folder if it doesn't exist
                try:
                    self.scsGames += [self.additionalDir]
                except:
                    pass
                
                # Copy the plugin to the correct folder
                successfullyInstalled = []
                for game in self.scsGames:
                    print(game)
                    # Check if the plugins folder exists
                    if not os.path.isdir(os.path.join(game, pluginInstallDir)):
                        os.makedirs(os.path.join(game, pluginInstallDir))
                    
                    # Copy the plugin to the folder
                    try:
                        shutil.copy(os.path.join(variables.PATH, "assets", "firstTimeSetup", "sdkPlugin", "scs-telemetry.dll"), os.path.join(game, pluginInstallDir))
                        successfullyInstalled.append(game)
                    except:
                        print("Failed to copy the plugin to " + os.path.join(game, pluginInstallDir))
                        
                from tkinter import messagebox
                if successfullyInstalled != []:
                    messagebox.showinfo("Success", "Successfully installed at least some plugin(s)!\nYou should start the game now to enable the SDK and continue on!\n\nInstalled to:\n" + "\n".join(successfullyInstalled))    
                else:
                    messagebox.showerror("Error", "Failed to install the plugin(s)!\nAre you sure you set your path properly?")
                
                
            
            # Display the automatic installation buttons if the directories were found
            helpers.MakeButton(self.root, "Install ETS2 / ATS Plugin", lambda: InstallETS2ATSPlugin(self), 7,0, columnspan=3, width=30)
            
            
        
            self.root.pack()
            self.root.update()
            
            try:
                if not api.loading:
                    api.checkAPI()
            except:
                api.checkAPI()
        
        def lastPage(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)
            
            # Set all necessary plugins
            settings.AddToList("Plugins", "Enabled", ["FPSLimiter", "DefaultSteering", "DXCamScreenCapture", "VGamepadController", "ShowImage", "TruckSimAPI"])
            if detectionmethod.get() == "nav":
                helpers.MakeLabel(self.root, "Almost there!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
                helpers.MakeLabel(self.root, "You should now open the game and return to this page!", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, " ", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "We need to make sure that the app can see the game, so set your game to borderless!", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "And then click the button below, and move the ", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "window to where it is perfectly alignned over the minimap.", 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            else:
                helpers.MakeLabel(self.root, "One more step!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
                helpers.MakeLabel(self.root, "You should now open the game and return to this page!", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, " ", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "We need to make sure that the app can see the game, so set your game to borderless!", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "And then click the button below, and move the ", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "window to where you are looking forward out of your truck.", 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)


            helpers.MakeButton(self.root, "Previous", lambda: self.ets2APIsetup(), 7,0)
            from src.mainUI import switchSelectedPlugin
            if os.name == "nt":
                helpers.MakeButton(self.root, "Open Panel", lambda: switchSelectedPlugin("plugins.ScreenCapturePlacement.main"), 7,1)
            else:
                helpers.MakeLabel(self.root, "Detected non windows system. You will have to manually enter the values!", 6,0, columnspan=2)
                helpers.MakeButton(self.root, "Open Panel", lambda: switchSelectedPlugin("plugins.MSSScreenCapture.main"), 7,1)
            
            self.root.pack()
            self.root.update()
        
        def update(self, data):
            self.root.update()
            pygame.event.pump()
            try:
                for i in range(len(self.sliderVars)):
                    self.sliderVars[i].set(self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_axis(i))
            except: pass
            
            try:
                value = ""
                for i in range(self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_numbuttons()):
                    if self.joysticks[settings.GetSettings("DefaultSteering", "controller")].get_button(i):
                        value += (" Button " + str(i))
                self.pressedButtons.set(value)
            except: pass
            
            try:
                image = self.camera.get_latest_frame()
                image = cv2.resize(image, (int(image.shape[1]/3), int(image.shape[0]/3)))
                cv2.imshow("test", image)
                
            except: 
                cv2.destroyAllWindows()
                pass
            
            try:
                self.apiNextButton.config(state="normal", text="Next")
            except:
                pass
                
                
            
    except Exception as ex:
        print(ex.args)
        destroy()
