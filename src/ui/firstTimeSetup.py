import tkinter as tk
from tkinter import ttk
import sv_ttk
import src.helpers as helpers
from src.mainUI import quit
from PIL import Image, ImageTk
import src.variables as variables
import os
import pygame
import src.settings as settings

pygame.display.init()
pygame.joystick.init()

class FirstTimeSetup():
    
    def __init__(self, master) -> None:
        self.done = False
        self.master = master
        self.page0()
    
    def destroy(self):
        self.done = True
        self.root.destroy()
        del self
    
    def page0(self):
        
        try:
            self.root.destroy()
        except: pass
        
        self.root = tk.Canvas(self.master)
        
        label = ttk.Label(self.root, text="Welcome!", font=("Roboto", 20, "bold"))
        label.grid(row=0, column=0, columnspan=2, pady=10, padx=30)

        label = ttk.Label(self.root, text="This is the first time you've run this program, so we need to set up some things first.", font=("Segoe UI", 10))
        label.grid(row=1, column=0, columnspan=2, pady=10, padx=30)

        helpers.MakeButton(self.root, "Quit", lambda: quit(), 2,0)
        helpers.MakeButton(self.root, "Next", lambda: self.page1(), 2,1)

        self.root.pack(anchor="center")
        

    def page1(self):
        self.root.destroy()
        self.root = tk.Canvas(self.master)

        helpers.MakeLabel(self.root, "Select your controller type", 0,1, font=("Roboto", 20, "bold"), padx=30, pady=10)
        helpers.MakeLabel(self.root, "First I'm going to ask you about your controller.", 1,1, font=("Segoe UI", 10), padx=30, pady=0)
        helpers.MakeLabel(self.root, "So please select the correct control type that you want to use.", 2,1, font=("Segoe UI", 10), padx=30, pady=0)        

        helpers.MakeButton(self.root, "Gamepad", lambda: self.gamepadPage(), 3,0)
        helpers.MakeButton(self.root, "Wheel", lambda: self.wheelPage(), 3,1)
        helpers.MakeButton(self.root, "Keyboard", lambda: self.keyboardPage(), 3,2)

        self.root.pack()
        
        
    def gamepadPage(self):
        self.root.destroy()
        self.root = tk.Canvas(self.master)

        helpers.MakeLabel(self.root, "Gamepad", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
        helpers.MakeLabel(self.root, "Great! I'll automatically set all the necessary options for gamepad usage.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
        helpers.MakeLabel(self.root, "Just be aware that you will have to set the controller type to 'wheel' in the game.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)        
        helpers.MakeLabel(self.root, "Don't worry there will be instructions later! For now please select your controller from the list below.", 3,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
        helpers.MakeLabel(self.root, "The list is scrollable, if you can't find your controller then go back and open the page again.", 5,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)

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
        self.root.destroy()
        self.root = tk.Canvas(self.master)

        helpers.MakeLabel(self.root, "Keyboard", 0,1, font=("Roboto", 20, "bold"), padx=30, pady=10)
        helpers.MakeLabel(self.root, "Unfortunately my application does not yet support keyboards :(", 1,1, font=("Segoe UI", 10), padx=30, pady=0)
        helpers.MakeLabel(self.root, "You can send me a message on discord asking for the feature, I might even have a dev build for you.", 2,1, font=("Segoe UI", 10), padx=30, pady=0) 
        helpers.MakeLabel(self.root, "But for now, you will need a controller to use the app.", 3,1, font=("Segoe UI", 10), padx=30, pady=0)       

        helpers.MakeButton(self.root, "Quit", lambda: quit(), 4,1)

        self.root.pack()
        
    
    def axisSetup(self):
        
        try:
            import src.settings as settings
            settings.CreateSettings("Controller", "Index", self.list.curselection()[0])
            settings.CreateSettings("Controller", "Name", self.joysticks[self.list.curselection()[0]].get_name())
        except: pass
        
        self.root.destroy()
        self.root = tk.Canvas(self.master)

        helpers.MakeLabel(self.root, "Axis Setup", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
        helpers.MakeLabel(self.root, "Now we are going to detect the different axis' on your controller.", 1,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)    
        helpers.MakeLabel(self.root, "So please go ahead and select the axis corresponding to steering from the below list.", 2,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2) 
        
        # Create sliders for all axis
        index = settings.GetSettings("Controller", "Index")
        self.sliderVars = []
        for i in range(self.joysticks[index].get_numaxes()):
            variable = tk.IntVar(self.root)
            helpers.MakeCheckButton(self.root, f"Axis {i}", "Controller", f"Axis {i}", i+4, 1)
            slider = ttk.Scale(self.root, from_=-100, to=100, variable=variable, orient=tk.HORIZONTAL, length=200)
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
        
        leftBlinkerFrame = ttk.Frame(notebook)
        leftBlinkerFrame.pack()
        rightBlinkerFrame = ttk.Frame(notebook)
        rightBlinkerFrame.pack()
        enableDisableFrame = ttk.Frame(notebook)
        enableDisableFrame.pack()
        
        # Get a list of all buttons
        index = settings.GetSettings("Controller", "Index")
        pygame.event.pump()
        
        buttons = []
        for i in range(self.joysticks[index].get_numbuttons()):
            buttons.append("Button " + str(i))
        
        # Create a combobox for each of the groups
        leftBlinker = tk.StringVar()
        rightBlinker = tk.StringVar()
        enableDisable = tk.StringVar()
        
        leftBlinkerCombo = ttk.Combobox(leftBlinkerFrame, textvariable=leftBlinker, width=50)
        leftBlinkerCombo['values'] = buttons
        rightBlinkerCombo = ttk.Combobox(rightBlinkerFrame, textvariable=rightBlinker, width=50)
        rightBlinkerCombo['values'] = buttons
        enableDisableCombo = ttk.Combobox(enableDisableFrame, textvariable=enableDisable, width=50)
        enableDisableCombo['values'] = buttons
        
        leftBlinkerCombo.pack()
        rightBlinkerCombo.pack()
        enableDisableCombo.pack()
        
        notebook.add(leftBlinkerFrame, text="Left Blinker")
        notebook.add(rightBlinkerFrame, text="Right Blinker")
        notebook.add(enableDisableFrame, text="Enable / Disable")
        
        helpers.MakeLabel(self.root, "You are currently pressing: ", 4,0, font=("Segoe UI", 10), padx=30, pady=0, columnspan=2)
        self.pressedButtons = tk.StringVar()
        tk.Label(self.root, textvariable=self.pressedButtons).grid(row=5, column=0, columnspan=2, padx=30, pady=0)

        helpers.MakeButton(self.root, "Previous", lambda: self.axisSetup(), 6,0)
        helpers.MakeButton(self.root, "Next", lambda: self.destroy(), 6,1)

        self.root.pack()
        self.root.update()
        
    def update(self):
        self.root.update()
        pygame.event.pump()
        try:
            for i in range(len(self.sliderVars)):
                self.sliderVars[i].set(self.joysticks[settings.GetSettings("Controller", "Index")].get_axis(i)*100)
        except: pass
        
        try:
            value = ""
            for i in range(self.joysticks[settings.GetSettings("Controller", "Index")].get_numbuttons()):
                if self.joysticks[settings.GetSettings("Controller", "Index")].get_button(i):
                    value += (" Button " + str(i))
            self.pressedButtons.set(value)
        except: pass