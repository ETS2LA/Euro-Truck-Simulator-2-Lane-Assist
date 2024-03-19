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
from tkinter import messagebox
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
import threading
import src.controls as controls
try:
    import bettercam
except:
    bettercam = None

def init_pygame():
    pygame.display.init()
    pygame.joystick.init()

threading.Thread(target=init_pygame).start()

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
            
            helpers.MakeLabel(self.root, "Welcome", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "This setup will automatically configure the OFFICIAL plugins. ", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "If you have any other plugins installed, please configure them manually.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)

            helpers.MakeEmptyLine(self.root, 3,0, columnspan=3)
            
            # REMEMBER TO CHANGE BACK TO PAGE1
            helpers.MakeButton(self.root, "Tutorial Video ↗", lambda: helpers.OpenInBrowser("https://www.youtube.com/watch?v=0pic0rzjvik"), 4,0, width=20)
            helpers.MakeButton(self.root, "Wiki ↗", lambda: helpers.OpenInBrowser("https://wiki.tumppi066.fi/en/LaneAssist"), 4,1, width=20)
            helpers.MakeButton(self.root, "Next", lambda: self.detectionselection(), 4,2, width=20)

            helpers.MakeEmptyLine(self.root, 5,0, columnspan=3)
            
            # Load the logo
            self.logo = Image.open(os.path.join(variables.PATH, "assets", "firstTimeSetup", "logo.png"))
            height = 320
            width = round(height * 1.665)
            self.logo = self.logo.resize((width, height), resample=Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.logo)
            self.logoLabel = tk.Label(self.root, image=self.logo)
            self.logoLabel.grid(row=6, column=0, columnspan=3, pady=10, padx=30)

            self.root.pack(anchor="center")
            
            self.root.update()
        

        def detectionselection(self):
            settings.CreateSettings("Plugins", "Enabled", ["TruckersMPLock"])
            def openwiki():
                    webview.create_window("Lane Assist Wiki", "https://wiki.tumppi066.fi/en/LaneAssist/DetectionTypes")
                    webview.start()
            self.root.destroy()
            del self.root
            self.root = tk.Canvas(self.master, highlightthickness=0)
            helpers.MakeLabel(self.root, "Lane detection type.", 0,0, font=("Roboto", 15, "bold"), padx=30, pady=10, columnspan=3,)
            helpers.MakeLabel(self.root, "TLDR: Navigation Detection is the recommended model for most people.", 1,0, font=("Segoe UI", 12), padx=30, pady=0, columnspan=3)
            ttk.Label(self.root, text="").grid(columnspan=3, row=2, column=0, ipadx=0, ipady=0, pady=0)
            ttk.Label(self.root, text="").grid(columnspan=3, row=5, column=0, ipadx=0, ipady=0, pady=0)
            global detectionmethod
            detectionmethod = tk.StringVar()
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="LSTR Lane Detection (Scans the road for lane lines)", value="lstr").grid(columnspan=3, row=6, column=0, sticky='w', padx=5, pady=5)
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="UFLD Lane Detection (Only for use with Nvidia GPU > GTX 1060)", value="ufld").grid(columnspan=3, row=7, column=0, sticky='w', padx=5, pady=5)
            ttk.Radiobutton(master=self.root, variable=detectionmethod, text="Navigation Detection (Uses the minimap for lane detection (Recommended))", value="nav").grid(columnspan=3, row=8, column=0, sticky='w', padx=5, pady=5)
            detectionmethod.set("nav")
            ttk.Label(self.root, text="").grid(columnspan=3, row=9, column=0, ipadx=0, ipady=0, pady=0)
            
            def detectionsettings():
                if detectionmethod.get() == "lstr":
                    print("LSTR Selected")
                    settings.AddToList("Plugins", "Enabled", ["LSTRDrawLanes"])
                    settings.AddToList("Plugins", "Enabled", ["LSTRLaneDetection"])
                elif detectionmethod.get() == "ufld":
                    ufldmessagebox = helpers.AskOkCancel("Are you sure you want to use UFLD",
                                            "UFLD requires a NVIDIA GPU 1060 TI or better, if you use UFLD without one you risk crashing your system. You are responsible for any damage while using UFLD.")
                    if ufldmessagebox == False:
                        return
                    print("UFLD Selected")
                    settings.AddToList("Plugins", "Enabled", ["UFLDDrawLanes"])
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
            helpers.MakeLabel(self.root, "Great! Now we need to know what kind of controller you are using.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeEmptyLine(self.root, 2,0, columnspan=3)
            
            helpers.MakeButton(self.root, "Gamepad", lambda: self.gamepadPage(), 3,0)
            helpers.MakeButton(self.root, "Wheel", lambda: self.wheelPage(), 3,1)
            helpers.MakeButton(self.root, "Keyboard", lambda: self.keyboardPage(), 3,2)
            helpers.MakeEmptyLine(self.root, 4,0, columnspan=3)
            helpers.MakeButton(self.root, "Back", lambda: self.detectionselection(), 5,1)
            
            self.root.pack()
            
            
        def gamepadPage(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            settings.CreateSettings("DefaultSteering", "gamepad", True)
            settings.CreateSettings("DefaultSteering", "gamepadSmoothness", 0.05)

            # helpers.MakeLabel(self.root, "Gamepad", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # helpers.MakeLabel(self.root, "Great! I'll automatically set all the necessary options for gamepad usage.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            # helpers.MakeLabel(self.root, "Just be aware that you will have to set the controller type to 'wheel' in the game.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)        
            # helpers.MakeLabel(self.root, "Don't worry there will be instructions later! For now please select your controller from the list below.", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            # pygame.event.pump()
            # 
            # 
            # helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 8,0)
            # helpers.MakeButton(self.root, "Next", lambda: self.axisSetup(), 8,1)

            self.buttonSetup()
            
            
        def wheelPage(self):
            
            settings.CreateSettings("DefaultSteering", "gamepad", False)
            settings.CreateSettings("DefaultSteering", "gamepadsmoothness", 0.05)
            # 
            # from plugins.DefaultSteering.main import updateSettings
            # updateSettings()
            # 
            # self.root.destroy()
            # self.root = tk.Canvas(self.master)
# 
            # helpers.MakeLabel(self.root, "Wheel", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # helpers.MakeLabel(self.root, "Great! Using a wheel has the most straight forward setup process.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
            # helpers.MakeLabel(self.root, "Please select your wheel from the list below.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
# 
            # pygame.event.pump()
# 
            # self.joysticks = pygame.joystick.get_count()
            # self.joysticks = [pygame.joystick.Joystick(i) for i in range(self.joysticks)]
            # 
            # self.listVariable = tk.StringVar(self.root)
            # self.listVariable.set([j.get_name() for j in self.joysticks])
            # 
            # self.list = tk.Listbox(self.root, width=70, height=4, listvariable=self.listVariable, selectmode="single")
            # self.list.grid(row=3, column=0, columnspan=2, padx=30, pady=10)
# 
            # helpers.MakeLabel(self.root, "The list is scrollable, if you can't find your controller then go back and open the page again.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
# 
            # helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 5,0)
            # helpers.MakeButton(self.root, "Next", lambda: self.axisSetup(), 5,1)

            self.buttonSetup()
            
            
        def keyboardPage(self):
            
            settings.CreateSettings("DefaultSteering", "keyboard", True)
            settings.CreateSettings("DefaultSteering", "gamepad", False)
            settings.CreateSettings("DefaultSteering", "gamepadsmoothness", 0.05)
            
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Keyboard", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Please bind the following buttons", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 

            helpers.MakeButton(self.root, "Bind enable / disable key", lambda: controls.ChangeKeybind("Enable/Disable Steering", updateUI=False), 2, 0, columnspan=2, width=25, tooltip="This button will enable and disable the steering.")
            # helpers.MakeButton(self.root, "Bind steer left key", lambda: controls.ChangeKeybind("Steer Left Key", updateUI=False), 3, 0)
            # helpers.MakeButton(self.root, "Bind steer right key", lambda: controls.ChangeKeybind("Steer Right Key", updateUI=False), 4, 0)

            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 8,0)
            if bettercam != None:
                helpers.MakeButton(self.root, "Next", lambda: self.screenCaptureSetup(), 8,1)
            else:
                helpers.MakeButton(self.root, "Next", lambda: self.soundSettings(), 8,1)

            self.root.pack()
            
            
        def buttonSetup(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Button Setup", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            
            def ButtonBound():
                self.boundVar.set(f"Bound to button index {settings.GetSettings('Input', 'Enable/Disable Steering')['buttonIndex']}")
            
            helpers.MakeLabel(self.root, "                                                  Please bind the enable disable button.                                                  ", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeButton(self.root, "Bind enable / disable button", lambda: controls.ChangeKeybind("Enable/Disable Steering", updateUI=False, callback=lambda: ButtonBound()), 3, 1, width=25, tooltip="This button will enable and disable the steering.")

            self.boundVar = helpers.MakeLabel(self.root, "", 4,0, columnspan=3)
            
            helpers.MakeButton(self.root, "Previous", lambda: self.page1(), 5,0, columnspan=2)
            helpers.MakeButton(self.root, "Next", lambda: self.saveButtonSettings(), 5,1, columnspan=2)


            self.root.pack()
            self.root.update()
            
        def saveButtonSettings(self):
            
            # Save the button settings
            # settings.CreateSettings("DefaultSteering", "leftIndicator", int(self.leftBlinkerCombo.get().split(" ")[1]))
            # settings.CreateSettings("DefaultSteering", "rightIndicator", int(self.rightBlinkerCombo.get().split(" ")[1]))
            # settings.CreateSettings("DefaultSteering", "enableDisable", int(self.enableDisableCombo.get().split(" ")[1]))
            
            from plugins.DefaultSteering.main import updateSettings
            updateSettings()
            
            if bettercam != None:
                self.screenCaptureSetup()      
            else:
                self.soundSettings()
        
        def screenCaptureSetup(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)

            helpers.MakeLabel(self.root, "Screen Capture", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "This app will screen capture your screen and detect the lanes on those images.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
            helpers.MakeLabel(self.root, "For this reason we need to make sure that the screen we capture on is correct.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)  
            helpers.MakeLabel(self.root, " ", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)       
            helpers.MakeLabel(self.root, "Please select the monitor ETS2 is going to be on.", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 

            # Detect all displays
            bettercamOutput = bettercam.output_info()
            for i in range(0,4):
                # Remove GPU indices
                bettercamOutput = bettercamOutput.replace(f"Device[{i}]", "")
                # Also remove 'rot'?
                bettercamOutput = bettercamOutput.replace(f"Rot:{i}", "")
                
            
            displays = bettercamOutput.split("\n")
            
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
            
        
        def setScreenCaptureSettings(self, display):
            settings.CreateSettings("bettercam", "display", int(display))
            #settings.CreateSettings("Screen Capture", "Refresh Rate", self.refreshRate.get())
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
            
            helpers.MakeButton(self.root, "Previous", lambda: self.screenCaptureSetup(), 7,0)
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
                    self.installButton.config(state="normal")
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
                        # Copy the API
                        shutil.copy(os.path.join(variables.PATH, "assets", "firstTimeSetup", "sdkPlugin", "scs-telemetry.dll"), os.path.join(game, pluginInstallDir))
                        # Copy the controller SDK
                        shutil.copy(os.path.join(variables.PATH, "assets", "firstTimeSetup", "sdkPlugin", "input_semantical.dll"), os.path.join(game, pluginInstallDir))
                        successfullyInstalled.append(game)
                    except:
                        print("Failed to copy the plugin to " + os.path.join(game, pluginInstallDir))
                        
                from tkinter import messagebox
                if successfullyInstalled != []:
                    helpers.ShowSuccess("Successfully installed at least some plugin(s)!\nYou should start the game now to enable the SDK and continue on!\n\nInstalled to:\n" + "\n".join(successfullyInstalled))    
                else:
                    helpers.ShowFailure("Failed to install the plugin(s)!\nAre you sure you set your path properly?", title="Error")
                
                
            
            # Display the automatic installation buttons if the directories were found
            if self.scsGames != []:
                self.installButton = helpers.MakeButton(self.root, "Install ETS2 / ATS Plugin", lambda: InstallETS2ATSPlugin(self), 7,0, columnspan=3, width=30)
            else:
                self.installButton = helpers.MakeButton(self.root, "Install ETS2 / ATS Plugin", lambda: InstallETS2ATSPlugin(self), 7,0, columnspan=3, width=30, state="disabled")
            
            helpers.MakeLabel(self.root, "\nETS2 API", 8,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=3)
            helpers.MakeLabel(self.root, "This app will also connect to your ETS2's / ATS' API and get data about your truck.", 9,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
            helpers.MakeLabel(self.root, "Press the button below to open the instructions (scroll down on the page).\nThe loading window will automatically disappear once connection is established.", 10,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=3)
        
            helpers.MakeButton(self.root, "Previous", lambda: self.soundSettings(), 11,0)
            import webbrowser
            helpers.MakeButton(self.root, "Open instructions", lambda: webbrowser.open("https://wiki.tumppi066.fi/en/LaneAssist/InGame"), 11,1)
            self.apiNextButton = helpers.MakeButton(self.root, "Waiting for api...", lambda: self.lastPage(), 11,2, state="disabled")
        
            self.root.pack()
            self.root.update()
            
            try:
                if not api.loading:
                    api.checkAPI(dontClosePopup=True)
            except:
                api.checkAPI(dontClosePopup=True)
                
            if api.isConnected:
                self.apiNextButton.config(state="normal", text="Next")
        
        def lastPage(self):
            self.root.destroy()
            self.root = tk.Canvas(self.master)
            
            # Set all necessary plugins
            settings.AddToList("Plugins", "Enabled", ["FPSLimiter", "DefaultSteering", "BetterCamScreenCapture", "SDKController", "ShowImage", "TruckSimAPI"])
            variables.UpdatePlugins()
            if detectionmethod.get() == "nav":
                helpers.MakeLabel(self.root, "Almost there!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
                helpers.MakeLabel(self.root, "You should now open the game and return to this page!", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, " ", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "We need to make sure that the app can see the game, so set your game to windowed mode.", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "And then click the button below, and open the ", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
                helpers.MakeLabel(self.root, "Navigation Detection setup.", 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
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
                if detectionmethod.get() == "nav":
                    helpers.MakeButton(self.root, "Open Panel", lambda: switchSelectedPlugin("plugins.NavigationDetection.main"), 7,1)
                else:
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
                if self.apiNextButton != None:
                    api.checkAPI(dontClosePopup=True)
                    if api.isConnected:
                        self.apiNextButton.config(state="normal", text="Next")
            except:
                pass
                
                
            
    except Exception as ex:
        print(ex.args)
        destroy()
