"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ThemeMaker", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Let's you change the color of a theme to your liking.\nEXPERIMENTAL! - There can be themes that don't work well!\nBase theme is the forest theme.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os


# Color to replace
AccentBaseColor = [255,255,255]
HoverBaseColor = [245,245,245]
InvalidBaseColor = [235,235,235]

# Colors to replace with
AccentColor = [33,115,70]
HoverColor = [36,127,76]
InvalidColor = [208,68,35]

# Directories
SourceDir = "plugins/ThemeMaker/base_dark/"
EditedDir = "plugins/ThemeMaker/edited/"

def ColorExample():
    import cv2
    import numpy as np

    
    # Load the image
    img = cv2.imread("plugins/ThemeMaker/example.png")
    
    # Change the colors
    img[np.where((img == InvalidBaseColor).all(axis=2))] = InvalidColor
    img[np.where((img == HoverBaseColor).all(axis=2))] = HoverColor
    img[np.where((img == AccentBaseColor).all(axis=2))] = AccentColor
    
    # Show the image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow("Example", img)
    
    
def ColorTCLTheme():
    # If the edited folder is not yet created then create it
    if not os.path.exists(EditedDir):
        os.makedirs(EditedDir)
        
    # Load all the images from the base_dark theme
    import cv2
    import numpy as np

    ignoredFiles = ["up.png", "left.png", "right.png", "down.png"]
    for file in os.listdir(SourceDir):
        if file in ignoredFiles:
            # Copy the file as is
            import shutil
            shutil.copyfile(SourceDir + file, EditedDir + file)
            continue    
        
        try:
            img = cv2.imread(SourceDir + file)
            
            # Change the colors with a +- 5 range
            InvalidBaseColor_range = np.array(InvalidBaseColor) + np.array([-5, 5, -5])
            HoverBaseColor_range = np.array(HoverBaseColor) + np.array([-5, 5, -5])
            AccentBaseColor_range = np.array(AccentBaseColor) + np.array([-5, 5, -5])

            img[np.where((img >= InvalidBaseColor_range[0]).all(axis=2) & (img <= InvalidBaseColor_range[1]).all(axis=2))] = InvalidColor
            img[np.where((img >= HoverBaseColor_range[0]).all(axis=2) & (img <= HoverBaseColor_range[1]).all(axis=2))] = HoverColor
            img[np.where((img >= AccentBaseColor_range[0]).all(axis=2) & (img <= AccentBaseColor_range[1]).all(axis=2))] = AccentColor
            
            # Save the image
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(EditedDir + file, img)
            
        except Exception as ex:
            print(ex.args)
            print("Failed to edit " + file)
            pass
        

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def changeColor(self, color, index, value):
            if color == "accent":
                AccentColor[index] = int(float(value))
            elif color == "hover":
                HoverColor[index] = int(float(value))
            elif color == "invalid":
                InvalidColor[index] = int(float(value))
                
            ColorExample()
        
        def colorThemeAndSave(self):
            ColorTCLTheme()
            # Check that none of the values are empty
            if self.name.get() == "":
                from tkinter import messagebox
                messagebox.showerror("ThemeMaker", "Name can't be empty!")
                return
            if self.author.get() == "":
                from tkinter import messagebox
                messagebox.showerror("ThemeMaker", "Author can't be empty!")
                return
            if self.description.get() == "":
                self.description.set("No description")
            if self.version.get() == "":
                self.description.set("0.1.0")
                
            # Create a new folder in themes/ with the name of the theme
            path = os.path.join(variables.PATH, r"themes", self.name.get())
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                from tkinter import messagebox
                if messagebox.askyesno("ThemeMaker", "Theme already exists, overwrite?"):
                    # Remove the folder
                    import shutil
                    shutil.rmtree(path)
                    # Create a new folder
                    os.makedirs(path)
                else:
                    return
            
            # Copy the contents of the edited folder to newFolder/name
            import shutil
            shutil.copytree(EditedDir, os.path.join(path, self.name.get()))
            
            # Create a theme.json file
            import json
            theme = {}
            theme["name"] = self.name.get()
            theme["description"] = self.description.get()
            theme["author"] = self.author.get()
            theme["version"] = self.version.get()
            theme["base"] = "forest"
            theme["titlebar"] = "0x313131" # TODO: Add titlebar color picker
            with open(os.path.join(path, "theme.json"), "w") as file:
                json.dump(theme, file, indent=4)
            
            # Edit the .tcl file and save it to the new folder
            file = open(variables.PATH + r"plugins\ThemeMaker\dark.tcl", "r")
            lines = file.readlines()
            file.close()
            
            # Replace all forest-dark with the name of the theme
            for i in range(len(lines)):
                lines[i] = lines[i].replace("forest-dark", self.name.get())
                # Change the selectbg color to the hover color
                # Convert the rgb to hex
                selectbg = "#%02x%02x%02x" % (HoverColor[0], HoverColor[1], HoverColor[2])
                lines[i] = lines[i].replace('        -selectbg       "#217346"',
                                            f'        -selectbg       "{selectbg}"')
                
            # Save the file to the new folder as theme.tcl
            file = open(os.path.join(path, "theme.tcl"), "w")
            file.writelines(lines)
            file.close()
            
            from tkinter import messagebox
            messagebox.showinfo("ThemeMaker", "Theme saved!")    
            
                
            
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=700, height=600, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Create a notebook to hold tabs for each color category
            self.notebook = ttk.Notebook(self.root, width=700, height=600)
            self.notebook.pack(anchor="center", expand=False)
            
            # Create the tabs
            self.tabAccent = ttk.Frame(self.notebook)
            self.tabHover = ttk.Frame(self.notebook)
            self.tabInvalid = ttk.Frame(self.notebook)
            self.tabSave = ttk.Frame(self.notebook)
            
            # Add the tabs to the notebook
            self.notebook.add(self.tabAccent, text="Accent")
            self.notebook.add(self.tabHover, text="Hover")
            self.notebook.add(self.tabInvalid, text="Invalid")
            self.notebook.add(self.tabSave, text="Save")
            
            # Add the rgb sliders to the tabs
            self.accentR = tk.Scale(self.tabAccent, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("accent", 0, value))
            self.accentR.grid(row=0, column=0)
            self.accentR.set(AccentColor[0])
            ttk.Label(self.tabAccent, text="Red").grid(row=0, column=1)
            self.accentG = tk.Scale(self.tabAccent, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("accent", 1, value))
            self.accentG.grid(row=1, column=0)
            self.accentG.set(AccentColor[1])
            ttk.Label(self.tabAccent, text="Green").grid(row=1, column=1)
            self.accentB = tk.Scale(self.tabAccent, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("accent", 2, value))
            self.accentB.grid(row=2, column=0)
            self.accentB.set(AccentColor[2])
            ttk.Label(self.tabAccent, text="Blue").grid(row=2, column=1)
            
            
            self.hoverR = tk.Scale(self.tabHover, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("hover", 0, value))
            self.hoverR.grid(row=0, column=0)
            self.hoverR.set(HoverColor[0])
            ttk.Label(self.tabHover, text="Red").grid(row=0, column=1)
            self.hoverG = tk.Scale(self.tabHover, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("hover", 1, value))
            self.hoverG.grid(row=1, column=0)
            self.hoverG.set(HoverColor[1])
            ttk.Label(self.tabHover, text="Green").grid(row=1, column=1)
            self.hoverB = tk.Scale(self.tabHover, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("hover", 2, value))
            self.hoverB.grid(row=2, column=0)
            self.hoverB.set(HoverColor[2])
            ttk.Label(self.tabHover, text="Blue").grid(row=2, column=1)
            
            
            self.invalidR = tk.Scale(self.tabInvalid, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("invalid", 0, value))
            self.invalidR.grid(row=0, column=0)
            self.invalidR.set(InvalidColor[0])
            ttk.Label(self.tabInvalid, text="Red").grid(row=0, column=1)
            self.invalidG = tk.Scale(self.tabInvalid, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("invalid", 1, value))
            self.invalidG.grid(row=1, column=0)
            self.invalidG.set(InvalidColor[1])
            ttk.Label(self.tabInvalid, text="Green").grid(row=1, column=1)
            self.invalidB = tk.Scale(self.tabInvalid, from_=0, to=255, length=400, orient="horizontal", command=lambda value: self.changeColor("invalid", 2, value))
            self.invalidB.grid(row=2, column=0)
            self.invalidB.set(InvalidColor[2])
            ttk.Label(self.tabInvalid, text="Blue").grid(row=2, column=1)
            
            # Make entries for the theme name, author, description and version
            self.name = helpers.MakeComboEntry(self.tabSave, "Name", "ThemeMaker", "Name", 0, 0, isString=True, width=30)
            self.author = helpers.MakeComboEntry(self.tabSave, "Author", "ThemeMaker", "Author", 1, 0, isString=True, width=30)
            self.description = helpers.MakeComboEntry(self.tabSave, "Description", "ThemeMaker", "Description", 2, 0, isString=True, width=30)
            self.version = helpers.MakeComboEntry(self.tabSave, "Version", "ThemeMaker", "Version", 3, 0, isString=True, width=30)
            
            # Add a button to save the theme
            helpers.MakeButton(self.tabSave, "Save Theme", self.colorThemeAndSave, 10, 0, width=26, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)