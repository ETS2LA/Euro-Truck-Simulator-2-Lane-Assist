"""
This is an example of a plugin (type="dynamic"), they will be updated during the stated point in the mainloop.
If you need to make a panel that is only updated when it's open then check the Panel example!
"""


from plugins.plugin import PluginInformation
from src.logger import print
from src.mainUI import switchSelectedPlugin, resizeWindow

PluginInfo = PluginInformation(
    name="CruiseControl", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    description="this is a plugin which uses a virtual controller\nor virtual keyboard to set the in-game cruise control,\nuses TrafficLightDetection to stop at red traffc lights",
    version="0.1",
    author="Glas42",
    url="https://github.com/Glas42/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before game", # Will run the plugin before anything else in the mainloop (data will be empty)
    requires=["TruckSimAPI"]
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
from src.translator import Translate
from tkinter import messagebox
import os

import plugins.DefaultSteering.main as DefaultSteering


import time
import keyboard as kb


left_trigger_setup = False
right_trigger_setup = False
left_trigger_value = 0
right_trigger_value = 0
trigger_setup_value = 0
trigger_setup_add_or_sub = 1
trigger_setup_time = time.time()
button_setup_time = time.time()
button_A_setup = False
button_B_setup = False
button_X_setup = False

def UpdateSettings():
    global keyboardmode
    global brakeatredtrafficlight
    global automatic_acceleration_after_traffic_light
    global automatic_acceleration
    global automatic_cruise_control_activation
    global advancedsettings
    global buttonup
    global buttondown
    global buttonactivate
    global buttonbrake
    global buttonaccelerate
    global accelerationspeed
    global unreleased_buttonbrake
    global unreleased_buttonaccelerate
    global accelerate_red_traffic_light
    global waitforresponse
    global waitforresponsetimer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight
    global trafficlightdetectionisenabled
    global deactivate_traffic_light_stop_temporary_key
    global enabledeactflstempkey
    global red_traffic_light_time
    global last_frame_without_traffic_light
    global left_trigger_value
    global right_trigger_value
    global left_trigger_setup
    global right_trigger_setup
    global trigger_setup_time
    global trigger_setup_value
    global trigger_setup_add_or_sub
    global button_A_setup
    global button_B_setup
    global button_X_setup
    global button_setup_time
    global cruisespeedinturns
    global cruisespeedattrafficlight

    keyboardmode = settings.GetSettings("CruiseControl", "keyboardmode", False)
    automatic_cruise_control_activation = settings.GetSettings("CruiseControl", "autoccacti", True)
    brakeatredtrafficlight = settings.GetSettings("CruiseControl", "brakeredtrafficlight", True)
    automatic_acceleration_after_traffic_light = settings.GetSettings("CruiseControl", "autoaccelatrflght", True)
    automatic_acceleration = settings.GetSettings("CruiseControl", "autoaccel", False)
    advancedsettings = settings.GetSettings("CruiseControl", "advancedsettings", False)
    enabledeactflstempkey = settings.GetSettings("CruiseControl", "enabledeactflstempkey", True)


    buttonup = settings.GetSettings("CruiseControl", "keyup")
    if buttonup == None:
        settings.CreateSettings("CruiseControl", "keyup", "please set")
        buttonup = "please set"

    buttondown = settings.GetSettings("CruiseControl", "keydown")
    if buttondown == None:
        settings.CreateSettings("CruiseControl", "keydown", "please set")
        buttondown = "please set"

    buttonactivate = settings.GetSettings("CruiseControl", "keyactivate")
    if buttonactivate == None:
        settings.CreateSettings("CruiseControl", "keyactivate", "please set")
        buttonactivate = "please set"

    buttonbrake = settings.GetSettings("CruiseControl", "keybrake")
    if buttonbrake == None:
        settings.CreateSettings("CruiseControl", "keybrake", "please set")
        buttonbrake = "please set"

    buttonaccelerate = settings.GetSettings("CruiseControl", "keyaccelerate")
    if buttonaccelerate == None:
        settings.CreateSettings("CruiseControl", "keyaccelerate", "please set")
        buttonaccelerate = "please set"


    accelerationspeed = settings.GetSettings("CruiseControl", "accelerationspeed")
    if accelerationspeed == None:
        settings.CreateSettings("CruiseControl", "accelerationspeed", 1)
        accelerationspeed = 1


    unreleased_buttonbrake = False
    unreleased_buttonaccelerate = False

    accelerate_red_traffic_light = False
    red_traffic_light_time = 0
    last_frame_without_traffic_light = time.time()

    if "TrafficLightDetection" in settings.GetSettings("Plugins", "Enabled"):
        trafficlightdetectionisenabled = True
    else:
        trafficlightdetectionisenabled = False

    deactivate_traffic_light_stop_temporary_key = settings.GetSettings("CruiseControl", "deactflstempkey")
    if deactivate_traffic_light_stop_temporary_key == None:
        settings.CreateSettings("CruiseControl", "deactflstempkey", "please set")
        deactivate_traffic_light_stop_temporary_key = "please set"


    waitforresponse = False
    waitforresponsetimer = time.time()

    last_speed = 0
    last_speedlimit = 0
    last_cruisecontrolspeed = 0

    cruisespeedinturns = settings.GetSettings("CruiseControl", "cruisespeedinturns")
    if cruisespeedinturns == None:
        settings.CreateSettings("CruiseControl", "cruisespeedinturns", 30)
        cruisespeedinturns = 30
    if cruisespeedinturns < 30:
        cruisespeedinturns = 30

    cruisespeedattrafficlight = settings.GetSettings("CruiseControl", "cruisespeedattrafficlight")
    if cruisespeedattrafficlight == None:
        settings.CreateSettings("CruiseControl", "cruisespeedattrafficlight", 0)
        cruisespeedattrafficlight = 0
    if cruisespeedattrafficlight < 30:
        if cruisespeedattrafficlight != 0:
            cruisespeedattrafficlight = 0


def plugin(data):
    global keyboardmode
    global brakeatredtrafficlight
    global automatic_acceleration_after_traffic_light
    global automatic_acceleration
    global automatic_cruise_control_activation
    global advancedsettings
    global buttonup
    global buttondown
    global buttonactivate
    global buttonbrake
    global buttonaccelerate
    global accelerationspeed
    global unreleased_buttonbrake
    global unreleased_buttonaccelerate
    global accelerate_red_traffic_light
    global waitforresponse
    global waitforresponsetimer
    global last_speed
    global last_speedlimit
    global last_cruisecontrolspeed
    global trafficlight
    global trafficlightdetectionisenabled
    global deactivate_traffic_light_stop_temporary_key
    global enabledeactflstempkey
    global red_traffic_light_time
    global last_frame_without_traffic_light
    global left_trigger_value
    global right_trigger_value
    global left_trigger_setup
    global right_trigger_setup
    global trigger_setup_time
    global trigger_setup_value
    global trigger_setup_add_or_sub
    global button_A_setup
    global button_B_setup
    global button_X_setup
    global button_setup_time
    global cruisespeedinturns
    global cruisespeedattrafficlight

    
    try:
        data["controller"]["leftStick"]
    except:
        data["controller"] = {}

    if left_trigger_setup == True or right_trigger_setup == True:
        
        if trigger_setup_value > 1:
            trigger_setup_add_or_sub = 0

        if trigger_setup_value < 0:
            trigger_setup_add_or_sub = 1

        if trigger_setup_add_or_sub == 1:
            trigger_setup_value += 0.05
        else:
            trigger_setup_value -= 0.05

        if left_trigger_setup == True:
            data["controller"]["lefttrigger"] = trigger_setup_value
            data["controller"]["righttrigger"] = 0

        if right_trigger_setup == True:
            data["controller"]["lefttrigger"] = 0
            data["controller"]["righttrigger"] = trigger_setup_value

        if trigger_setup_time + 15 < time.time():
            left_trigger_setup = False
            right_trigger_setup = False
            data["controller"]["lefttrigger"] = 0
            data["controller"]["righttrigger"] = 0
            variables.ENABLELOOP = False


    if button_A_setup == True or button_B_setup == True or button_X_setup == True:
        data["controller"]["button_A"] = False
        data["controller"]["button_B"] = False
        data["controller"]["button_X"] = False

        if button_A_setup == True:
            if button_B_setup == True:
                button_B_setup = False
            if button_X_setup == True:
                button_X_setup = False
            if round(time.time()) % 2 == 0:
                data["controller"]["button_A"] = True

        if button_B_setup == True:
            if button_A_setup == True:
                button_A_setup = False
            if button_X_setup == True:
                button_X_setup = False
            if round(time.time()) % 2 == 0:
                data["controller"]["button_B"] = True

        if button_X_setup == True:
            if button_A_setup == True:
                button_A_setup = False
            if button_B_setup == True:
                button_B_setup = False
            if round(time.time()) % 2 == 0:
                data["controller"]["button_X"] = True

        if button_setup_time + 15 < time.time():
            button_A_setup = False
            button_B_setup = False
            button_X_setup = False
            variables.ENABLELOOP = False


    if left_trigger_setup != True and right_trigger_setup != True and button_A_setup != True and button_B_setup != True and button_X_setup != True:

        # get api data
        try:
            speed = round(data["api"]["truckFloat"]["speed"]*3.6, 1)
            last_speed = speed
            speedlimit = round(data["api"]["truckFloat"]["speedLimit"]*3.6, 1)
            last_speedlimit = speedlimit
            cruisecontrolspeed = round(data["api"]["truckFloat"]["cruiseControlSpeed"]*3.6, 1)
            gamepaused = data["api"]["pause"]
        except:
            speed = last_speed
            speedlimit = last_speedlimit
            cruisecontrolspeed = 0
            gamepaused = False

        data["controller"]["button_A"] = False
        data["controller"]["button_B"] = False
        data["controller"]["button_X"] = False

        #set target speeds
        targetspeed = speedlimit

        try:
            turnincoming = data["NavigationDetectionV2"]["turnincoming"]
        except:
            turnincoming = False
        if turnincoming == True:
            targetspeed = cruisespeedinturns
        
        if trafficlightdetectionisenabled == True:
            try:
                trafficlight = data["TrafficLightDetection"]
            except:
                trafficlight = "---"
        else:
            trafficlight = "Off"

        if trafficlight != "Red":
            last_frame_without_traffic_light = time.time()

        if enabledeactflstempkey == True:
            if kb.is_pressed(deactivate_traffic_light_stop_temporary_key):
                trafficlight = "---"
                red_traffic_light_time = time.time() - 1.1

        if trafficlight == "Red":
            if brakeatredtrafficlight == True:
                if time.time() - 0.5 > last_frame_without_traffic_light:
                    targetspeed = cruisespeedattrafficlight
                    red_traffic_light_time = time.time()
                    if speed < 30:
                        accelerate_red_traffic_light = True

        if red_traffic_light_time > time.time()-1:
            if brakeatredtrafficlight == True:
                if time.time() - 0.2 > last_frame_without_traffic_light:
                    targetspeed = cruisespeedattrafficlight

        #check for response or timeout of button click
        if last_cruisecontrolspeed != cruisecontrolspeed or time.time() - waitforresponsetimer > 1:
            waitforresponse = False

        #if there are no open requests
        if waitforresponse == False:

            #activate cruise control
            if targetspeed != 0 and cruisecontrolspeed == 0 and speed > 30:
                if automatic_cruise_control_activation == True:
                    if DefaultSteering.enabled and gamepaused == False:
                        if keyboardmode == True:
                            kb.press_and_release(buttonactivate)
                        else:
                            data["controller"]["button_X"] = True
                        waitforresponse = True
                        waitforresponsetimer = time.time()
                        unreleased_buttonbrake
                        unreleased_buttonaccelerate
            
            #change the cruisecontrol speed if needed
            if targetspeed != 0:
                if targetspeed > cruisecontrolspeed:
                    if cruisecontrolspeed != 0:
                        if DefaultSteering.enabled and gamepaused == False:
                            if keyboardmode == True:
                                kb.press_and_release(buttonup)
                            else:
                                data["controller"]["button_B"] = True
                            waitforresponse = True
                            waitforresponsetimer = time.time()

                if targetspeed < cruisecontrolspeed:
                    if cruisecontrolspeed != 0:
                        if DefaultSteering.enabled and gamepaused == False:
                            if keyboardmode == True:
                                kb.press_and_release(buttondown)
                            else:
                                data["controller"]["button_A"] = True
                            waitforresponse = True
                            waitforresponsetimer = time.time()


            #accelerate after traffic light if enabled in settings
            if targetspeed != 0 and cruisecontrolspeed == 0:
                if automatic_acceleration_after_traffic_light == True or automatic_acceleration == True:
                    if DefaultSteering.enabled and gamepaused == False:
                        if accelerate_red_traffic_light == True or automatic_acceleration == True:
                            if keyboardmode == True:
                                kb.release(buttonbrake)
                                kb.press(buttonaccelerate)
                            else:
                                left_trigger_value = 0
                                right_trigger_value = accelerationspeed
                            unreleased_buttonaccelerate = True
                            if speed > 30:
                                accelerate_red_traffic_light = False

            #brake if target speed is 0
            if targetspeed == 0:
                if speed > 0.5:
                    if DefaultSteering.enabled and gamepaused == False:
                        if keyboardmode == True:
                            kb.release(buttonaccelerate)
                            kb.press(buttonbrake)
                        else:
                            right_trigger_value = 0
                            left_trigger_value = 1
                        waitforresponse = True
                        waitforresponsetimer = time.time()
                        unreleased_buttonbrake = True

        #release brake button if needed
        if unreleased_buttonbrake == True and speed < 0.5:
            if keyboardmode == True:
                kb.release(buttonbrake)
            else:
                left_trigger_value = 0
            unreleased_buttonbrake = False
                
        #release acceleration button if needed
        if automatic_acceleration_after_traffic_light == True:
            if unreleased_buttonaccelerate == True and speed > 30:
                if keyboardmode == True:
                    kb.release(buttonaccelerate)
                else:
                    right_trigger_value = 0
                unreleased_buttonaccelerate = False

        if DefaultSteering.enabled == False or gamepaused == True:
            left_trigger_value = 0
            right_trigger_value = 0

        data["controller"]["lefttrigger"] = left_trigger_value
        data["controller"]["righttrigger"] = right_trigger_value

        last_cruisecontrolspeed = cruisecontrolspeed
    return data # Plugins need to ALWAYS return the data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    UpdateSettings()
    pass

def onDisable():
    pass

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        global colortheme
        if settings.GetSettings("User Interface", "ColorTheme") == "SunValley":
            colortheme = "sunvalley"
        else:
            colortheme = "notsunvalley"

        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()

            if colortheme == "sunvalley":
                resizeWindow(900,668)
            else:
                resizeWindow(900,620)
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self
        
        def UpdateScaleValueFromSlider(self):
            self.accelerationspeed.set(self.accelerationspeedSlider.get())
        
        def exampleFunction(self):
            try:
                self.root.destroy() 
            except: pass
            
            self.root = tk.Canvas(self.master, width=700, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) 
            self.root.pack_propagate(0)
            
            notebook = ttk.Notebook(self.root)
            notebook.pack(anchor="center", fill="both", expand=True)
            
            generalFrame = ttk.Frame(notebook)
            generalFrame.pack()
            keyboardFrame = ttk.Frame(notebook)
            keyboardFrame.pack()
            controllerFrame = ttk.Frame(notebook)
            controllerFrame.pack()
            advancedFrame = ttk.Frame(notebook)
            advancedFrame.pack()
            
            generalFrame.columnconfigure(0, weight=1)
            generalFrame.columnconfigure(1, weight=1)
            generalFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(generalFrame, "General", 0, 0, font=("Robot", 12, "bold"), columnspan=3)
            
            keyboardFrame.columnconfigure(0, weight=1)
            keyboardFrame.columnconfigure(1, weight=1)
            keyboardFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(keyboardFrame, "Keyboard", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            controllerFrame.columnconfigure(0, weight=1)
            controllerFrame.columnconfigure(1, weight=1)
            controllerFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(controllerFrame, "Controller", 0, 0, font=("Robot", 12, "bold"), columnspan=3)

            advancedFrame.columnconfigure(0, weight=1)
            advancedFrame.columnconfigure(1, weight=1)
            advancedFrame.columnconfigure(2, weight=1)
            helpers.MakeLabel(advancedFrame, "Advanced", 0, 0, font=("Robot", 12, "bold"), columnspan=7)

            notebook.add(generalFrame, text=Translate("General"))
            notebook.add(keyboardFrame, text=Translate("Keyboard"))
            notebook.add(controllerFrame, text=Translate("Controller"))
            notebook.add(advancedFrame, text=Translate("Advanced"))
            
            ttk.Button(self.root, text="Save", command=self.save, width=15).pack(anchor="center", pady=6)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()


            helpers.MakeCheckButton(generalFrame, "Use Keyboard for cruise control", "CruiseControl", "keyboardmode", 1, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatically activate cruise control when above 30kph", "CruiseControl", "autoccacti", 2, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Brake at a red traffic light\n(requires that the TrafficLightDetection plugin is enabled)", "CruiseControl", "brakeredtrafficlight", 3, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Automatic acceleration after a red traffic light", "CruiseControl", "autoaccelatrflght", 4, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Accelerate to targetspeed, even if you are slower than 30kph\n(if you disable the lane assist with the the key you set in the\nDefault Steering plugin, the truck will not accelerate to the targetspeed)", "CruiseControl", "autoaccel", 5, 0, width=60, callback=UpdateSettings())
            helpers.MakeCheckButton(generalFrame, "Use Advanced Settings", "CruiseControl", "advancedsettings", 6, 0, width=60, callback=UpdateSettings())


            self.keyactivate = helpers.MakeComboEntry(keyboardFrame, "Key to activate in-game cruise control", "CruiseControl", "keyactivate", 1, 0, labelwidth=70, width=10, isString=True)
            self.keyup = helpers.MakeComboEntry(keyboardFrame, "Key to increase in-game cruise control speed", "CruiseControl", "keyup", 2, 0, labelwidth=70, width=10, isString=True)
            self.keydown = helpers.MakeComboEntry(keyboardFrame, "Key to decrease in-game cruise control speed", "CruiseControl", "keydown", 3, 0, labelwidth=70, width=10, isString=True)
            self.keyaccelerate = helpers.MakeComboEntry(keyboardFrame, "Key to accelerate (in-game)", "CruiseControl", "keyaccelerate", 4, 0, labelwidth=70, width=10, isString=True)
            self.keybrake = helpers.MakeComboEntry(keyboardFrame, "Key to brake (in-game)", "CruiseControl", "keybrake", 5, 0, labelwidth=70, width=10, isString=True)


            self.cruisespeedinturns = helpers.MakeComboEntry(advancedFrame, "Cruise speed in turns (30kph or more)", "CruiseControl", "cruisespeedinturns", 1, 0, labelwidth=70, width=10)
            self.cruisespeedattrafficlight = helpers.MakeComboEntry(advancedFrame, "Cruise speed at red traffic lights (30 kph or more, or 0 kph)", "CruiseControl", "cruisespeedattrafficlight", 2, 0, labelwidth=70, width=10)
            

            self.accelerationspeedSlider = tk.Scale(controllerFrame, from_=0.01, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=600, command=lambda x: self.UpdateScaleValueFromSlider())
            self.accelerationspeedSlider.set(settings.GetSettings("CruiseControl", "accelerationspeed", 1))
            self.accelerationspeedSlider.grid(row=9, column=0, padx=10, pady=0, columnspan=2)
            self.accelerationspeed = helpers.MakeComboEntry(controllerFrame, "Accelerationspeed after red traffic light\n(1 is full throttle)", "CruiseControl", "accelerationspeed", 10,0, labelwidth=45, width=45)


            helpers.MakeCheckButton(generalFrame, "Enable the key to temporary ignore the detected traffic lights\n(if disabled, you dont have to set the key below)", "CruiseControl", "enabledeactflstempkey", 7, 0, width=60, callback=UpdateSettings())
            self.deactflstempkey = helpers.MakeComboEntry(generalFrame, "Key to temporary ignore the detected traffic lights\n(press and hold to use in-game)", "CruiseControl", "deactflstempkey", 8, 0, labelwidth=70, width=10, isString=True)


            helpers.MakeButton(controllerFrame, "BRAKE SETUP (LEFT TRIGGER)\n(this will move the left trigger of the virtual\ncontroller, so you can set up the controls\nin the in-game settings)", command=self.lefttriggersetup, row=11, column=0, width=50, columnspan=1)
            helpers.MakeButton(controllerFrame, "THROTTLE SETUP (RIGHT TRIGGER)\n(this will move the right trigger of the virtual\ncontroller, so you can set up the controls\nin the in-game settings)", command=self.righttriggersetup, row=11, column=1, width=50, columnspan=1)

            helpers.MakeButton(controllerFrame, "DECREASE BUTTON SETUP (BUTTON A)\n(this will press the button A for 15s so you can set\nup your controls in game, later the button A will be\npressed to decrease the cruisecontrol speed)", command=self.buttonAsetup, row=13, column=1, width=50, columnspan=1)
            helpers.MakeButton(controllerFrame, "INCREASE BUTTON SETUP (BUTTON B)\n(this will press the button B for 15s so you can set\nup your controls in game, later the button B will be\npressed to increase the cruisecontrol speed)", command=self.buttonBsetup, row=12, column=1, width=50, columnspan=1)
            helpers.MakeButton(controllerFrame, "ACTIVATE BUTTON SETUP (BUTTON X)\n(this will press the button X for 15s so you can set\nup your controls in game, later the button X will be\npressed to activate or deactivate the cruise control)", command=self.buttonXsetup, row=12, column=0, width=50, columnspan=1)

            helpers.MakeButton(controllerFrame, "STOP SETUP MODE\n(if you press the button the setup mode will stop and the\nthe triggers and buttons of the virtual controller will\nnot get moved or pressed anymore)", command=self.stopsetup, row=13, column=0, width=50, columnspan=1)

            helpers.MakeButton(generalFrame, "Reset Advanced Settings", command=self.resetalladvancedsettingstodefault, row=6, column=1, width=32)
            helpers.MakeButton(advancedFrame, "Reset Advanced Settings", command=self.resetalladvancedsettingstodefault, row=3, column=1, width=32)

        def save(self):
            settings.CreateSettings("CruiseControl", "keyactivate", self.keyactivate.get())
            settings.CreateSettings("CruiseControl", "keyup", self.keyup.get())
            settings.CreateSettings("CruiseControl", "keydown", self.keydown.get())
            settings.CreateSettings("CruiseControl", "keybrake", self.keybrake.get())
            settings.CreateSettings("CruiseControl", "keyaccelerate", self.keyaccelerate.get())
            settings.CreateSettings("CruiseControl", "cruisespeedinturns", self.cruisespeedinturns.get())
            settings.CreateSettings("CruiseControl", "cruisespeedattrafficlight", self.cruisespeedattrafficlight.get())
            settings.CreateSettings("CruiseControl", "accelerationspeed", self.accelerationspeedSlider.get())
            settings.CreateSettings("CruiseControl", "deactflstempkey", self.deactflstempkey.get())
            UpdateSettings()
            if self.deactflstempkey.get() == "please set" and enabledeactflstempkey == True:
                messagebox.showwarning(title="CruiseControl", message="Please set the key to temporary ignore the detected traffic lights in General")
            if keyboardmode == True:
                if (self.keyactivate.get() == "please set" or
                    self.keyup.get() == "please set" or
                    self.keydown.get() == "please set" or
                    self.keybrake.get() == "please set" or
                    self.keyaccelerate.get() == "please set"):
                    messagebox.showwarning(title="CruiseControl", message="Please set the correct keys in the Keyboard window")
            UpdateSettings()


        def resetalladvancedsettingstodefault(self):
            settings.CreateSettings("CruiseControl", "cruisespeedinturns", 30)
            settings.CreateSettings("CruiseControl", "cruisespeedattrafficlight", 0)
            UpdateSettings()
            switchSelectedPlugin("plugins." + "CruiseControl" + ".main")


        def lefttriggersetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = True
            right_trigger_setup = False
            trigger_setup_time = time.time()
            button_A_setup = False
            button_B_setup = False
            button_X_setup = False
            button_setup_time = time.time()
            variables.ENABLELOOP = True
            UpdateSettings()

        def righttriggersetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = False
            right_trigger_setup = True
            trigger_setup_time = time.time()
            button_A_setup = False
            button_B_setup = False
            button_X_setup = False
            button_setup_time = time.time()
            variables.ENABLELOOP = True
            UpdateSettings()

        def buttonAsetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = False
            right_trigger_setup = False
            trigger_setup_time = time.time()
            button_A_setup = True
            button_B_setup = False
            button_X_setup = False
            button_setup_time = time.time()
            variables.ENABLELOOP = True
            UpdateSettings()

        def buttonBsetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = False
            right_trigger_setup = False
            trigger_setup_time = time.time()
            button_A_setup = False
            button_B_setup = True
            button_X_setup = False
            button_setup_time = time.time()
            variables.ENABLELOOP = True
            UpdateSettings()

        def buttonXsetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = False
            right_trigger_setup = False
            trigger_setup_time = time.time()
            button_A_setup = False
            button_B_setup = False
            button_X_setup = True
            button_setup_time = time.time()
            variables.ENABLELOOP = True
            UpdateSettings()

        def stopsetup(self):
            global left_trigger_setup
            global right_trigger_setup
            global trigger_setup_time
            global button_A_setup
            global button_B_setup
            global button_X_setup
            global button_setup_time
            left_trigger_setup = False
            right_trigger_setup = False
            trigger_setup_time = time.time()
            button_A_setup = False
            button_B_setup = False
            button_X_setup = False
            button_setup_time = time.time()
            variables.ENABLELOOP = False
            UpdateSettings()
        

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)