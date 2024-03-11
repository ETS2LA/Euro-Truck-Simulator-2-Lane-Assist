"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DeepTranslator", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="DeepTranslator control panel.",
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
import src.translator as translator
import os

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def changeLanguage(self, language):
            settings.CreateSettings("User Interface", "DestinationLanguage", translator.FindCodeFromLanguage(language))
            translator.dest = translator.FindCodeFromLanguage(language)
            translator.MakeTranslator("google")
            variables.RELOAD = True
        
        def changeCacheSettings(self):
            translator.LoadSettings()
            translator.MakeTranslator("google")
            variables.RELOAD = True
        
        def removeCache(self):
            path = translator.cachePath
            if os.path.exists(path):
                os.remove(path)
                from tkinter import messagebox
                helpers.ShowSuccess("Cache removed successfully.")
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=1000, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.languages = translator.AVAILABLE_LANGUAGES
            
            languagesToDisplay = [string for string in self.languages if string not in ["auto"]]
            # Make a picker of the languages
            helpers.MakeLabel(self.root, "Language Settings", 0,0, sticky="w", padx=10, autoplace=True, font=("Segoe UI", 16, "bold"))
            helpers.MakeLabel(self.root, "Application language : ", 0,0, sticky="w", padx=10, autoplace=True)
            self.language = ttk.Combobox(self.root, values=languagesToDisplay, width=20)
            currentLanguage = translator.FindLanguageFromCode(settings.GetSettings("User Interface", "DestinationLanguage"))
            indexOfCurrentLanguage = languagesToDisplay.index(currentLanguage)
            self.language.current(indexOfCurrentLanguage)
            self.language.grid(row=1, column=1, padx=10, pady=10)
            
            helpers.MakeButton(self.root, "Apply", lambda: self.changeLanguage(self.language.get()), 1,0, padx=10, pady=10, width=25, autoplace=True)
            helpers.MakeButton(self.root, "Reset to OS", lambda: self.changeLanguage(translator.FindLanguageFromCode(translator.GetOSLanguage())), 1,1, padx=10, pady=10, width=21, autoplace=True)
            
            helpers.MakeEmptyLine(self.root, 2,0, columnspan=3, autoplace=True)
            
            helpers.MakeLabel(self.root, "Cache Settings", 2,0, sticky="w", padx=10, autoplace=True, font=("Segoe UI", 16, "bold"))
            helpers.MakeCheckButton(self.root, "Enable", "User Interface", "EnableTranslationCache", 3,1, columnspan=3, autoplace=True)
            
            helpers.MakeComboEntry(self.root, "Cache Path", "User Interface", "TranslationCachePath", 4,0, width=30, autoplace=True)
            
            helpers.MakeButton(self.root, "Reload and Save", lambda: self.changeCacheSettings(), 5,0, padx=10, pady=10, width=25, columnspan=3, sticky="w", autoplace=True)
            
            helpers.MakeButton(self.root, "Remove Cache", lambda: self.removeCache(), 6,1, padx=10, pady=10, width=25, columnspan=3, sticky="w", autoplace=True)
            
            helpers.MakeEmptyLine(self.root, 7,0, columnspan=3, autoplace=True)
            
            helpers.MakeLabel(self.root, "Custom Translations", 7,0, sticky="w", padx=10, autoplace=True, font=("Segoe UI", 16, "bold"))
            
            helpers.MakeButton(self.root, "Create Manual Cache", lambda: translator.CreateManualTranslationFile(), 7,0, padx=10, pady=10, width=25, columnspan=3, sticky="w", autoplace=True)
            helpers.MakeLabel(self.root, "Please open all UIs with the language chosen before creating the manual translation file.", 8,0, sticky="w", padx=10, columnspan=3, autoplace=True)
            
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)