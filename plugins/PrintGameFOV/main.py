"""
This example is a part of the wiki page available here: https://wiki.tumppi066.fi/tutorials/plugincreation/
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="PrintGameFOV", # This needs to match the folder name under plugins (this would mean plugins\Plugin\main.py)
    # In case the plugin is not the main file (for example plugins\Plugin\Plugin.py) then the name would be "Plugin.Plugin"
    
    description="This plugin will print the game fov to the console when pressing a defined keybind.\nI addition if the time is past 18:00 it will enable the lights,\nand if it's past 9:00 it will disable them.",
    version="0.1",
    author="Romans",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before controller" # Will run the plugin before anything else in the mainloop (data will be empty)
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.controls as controls # use controls.RegisterKeybind() and controls.GetKeybindValue()
import os
import src.gamefiles as gamefiles
import subprocess


def find_string_in_file(file_path, target_string, start_line=0):
    try:
        with open(file_path, 'r') as file:
            # Смещаем указатель файла к указанной строке
            for _ in range(start_line):
                next(file)
            
            # Производим поиск строки в оставшейся части файла
            for line_number, line in enumerate(file, start=start_line + 1):
                if target_string in line:
                    return line, line_number
        return None, None
    except FileNotFoundError:
        print("File no found")
        return None, None


def getpath():
     current_profile_path = gamefiles.GetCurrentProfilePath()
     saves = []
     for folder in os.listdir(current_profile_path + "/save"):
         saves.append((folder, os.path.getmtime(f"{current_profile_path}/save/{folder}")))
     if saves != []:
         saves.sort(key=lambda x: x[1], reverse=True)
         most_recent_save = saves[0]
     else:
         most_recent_save = None
     if most_recent_save != None:
         game_sii_path = gamefiles.GetCurrentProfilePath() + "/save/" + most_recent_save[0] + "/game.sii"
     else:
         print(RED + "No profile with saves in documents found, unable to read file." + NORMAL)
         game_sii_path = None
     return game_sii_path


current_directory = os.getcwd()

subprocess.call([current_directory + "\plugins\PrintGameFOV" + "\\SII_Decrypt.exe"] + [getpath()])

my_truck_result = find_string_in_file( getpath(), "my_truck:")
my_truck_string = my_truck_result[0]
my_truck_result_string = my_truck_string.replace("my_truck: ", "")
my_truck_result_string = my_truck_result_string.replace("\n", "")

vehicle_target = f"vehicle :{my_truck_result_string}"
fov_from_game = find_string_in_file( getpath(), "user_fov:", find_string_in_file( getpath(), vehicle_target)[1])
fov_from_game_result = fov_from_game[0].replace(" user_fov:", "")
fov_from_game_result = int(fov_from_game_result.replace("\n", ""))
print(fov_from_game_result)
fov_converted = fov_from_game_result + 65
print(fov_converted)


# The main file runs the "plugin" function each time the plugin is called
# The data variable contains the data from the mainloop, plugins can freely add and modify data as needed
# The data from the last frame is contained under data["last"]
controls.RegisterKeybind("Print game time", defaultButtonIndex=",")
lastPressed = False

def plugin(data):
    try:
        return data
    except Exception as ex:
        print(ex.args)
        return data


# Plugins need to all also have the onEnable and onDisable functions
def onEnable():
    pass

def onDisable():
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
            helpers.MakeLabel(self.root, "This is a plugin!", 0,0, font=("Roboto", 20, "bold"), padx=30, pady=10, columnspan=2)
            # Use the mainUI.quit() function to quit the app
            helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 1,0, padx=30, pady=10)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def tabFocused(self): # Called when the tab is focused
            pass
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)