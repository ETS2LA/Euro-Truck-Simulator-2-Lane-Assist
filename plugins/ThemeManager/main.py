from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ThemeManager",
    description="Allows you to select and use different themes",
    version="0.1",
    author="DylDev",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static"
)


from src.loading import LoadingWindow
import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
from src.mainUI import quit, switchSelectedPlugin
import src.variables as variables
import src.settings as settings
import os
from PIL import Image, ImageTk

class Theme():
    name = ""
    description = ""
    author = ""
    version = ""
    titlebar = ""
    base = ""

class UI():
    try:
        def findThemes(self):
            # Find themes
            print("Importing Themes...")
            path = os.path.join(variables.PATH, r"themes")
            themes = []
            for folder in os.listdir(path):
                if os.path.isdir(os.path.join(path, folder)):
                    for file in os.listdir(os.path.join(path, folder)):
                        if file == "themeTemplate.json" or file == "theme.json":
                            # Parse the json into the class
                            theme = Theme()
                            fileContent = open(os.path.join(path, folder, file), "r").read()
                            import json
                            jsonContent = json.loads(fileContent)
                            theme.name = jsonContent["name"]
                            theme.description = jsonContent["description"]
                            theme.author = jsonContent["author"]
                            theme.version = jsonContent["version"]
                            theme.base = jsonContent["base"].lower()
                            theme.titlebar = jsonContent["titlebar"]
                            
                            themes.append(theme)
                               
            return themes
        

        
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
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0)
            
            self.themes = self.findThemes()
            
            self.listVariable = tk.StringVar()
            self.listVariable.set([helpers.ConvertCapitalizationToSpaces(t.name) for t in self.themes])
            
            self.themeList = tk.Listbox(self.root, width=20, height=20, listvariable=self.listVariable, font=("Roboto", 12), selectmode="single", activestyle="none")
            self.themeList.grid(row=1, column=0, padx=10, pady=2)
            
            helpers.MakeLabel(self.root, "Select a theme to load:", 0,0, font=("Roboto", 8), padx=30, pady=10, columnspan=1)
            
            self.root.pack(anchor="center", expand=False)
            
            self.root.update()
        
        
        def selectedTheme(self, theme):
            try:
                self.themeInfoFrame.destroy()
            except:
                pass
            
            self.theme = theme
            
            print("Selected theme: " + theme.name)
            
            self.themeInfoFrame = ttk.LabelFrame(self.root, text=theme.name, width=380, height=500)
            self.themeInfoFrame.pack_propagate(0)
            self.themeInfoFrame.grid_propagate(0)
            self.themeInfoFrame.grid(row=0, column=1, padx=10, pady=2, rowspan=3)

            helpers.MakeLabel(self.themeInfoFrame, theme.name, 0,0, font=("Roboto", 16, "bold"), padx=10, pady=10, columnspan=2, sticky="w")
                
            helpers.MakeLabel(self.themeInfoFrame, "Description", 1,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
            helpers.MakeLabel(self.themeInfoFrame, theme.description, 2,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
            helpers.MakeLabel(self.themeInfoFrame, "Author", 5,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
            helpers.MakeLabel(self.themeInfoFrame, theme.author, 6,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
            helpers.MakeLabel(self.themeInfoFrame, "Version", 7,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
            helpers.MakeLabel(self.themeInfoFrame, theme.version, 8,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")

            helpers.MakeButton(self.themeInfoFrame, "Load theme", lambda: self.loadTheme(), 9, 0, width=15, padx=8)        

        def loadTheme(self):
            if self.theme.base == "forest":
                import plugins.ThemeSelector.main as ThemeSelector
                ThemeSelector.ChangeThemeCustom(fr"themes\{self.theme.name}\theme.tcl", self.master, self.theme.base, self.theme.name, self.theme.titlebar)
                
            pass
        
        def tabFocused(self):
            self.page0()
        
        def update(self, data):
            try:
                self.theme
            except:
                self.selectedTheme(self.themes[0])
            
            try:
                if self.themes[self.themeList.curselection()[0]].name != self.theme.name:
                    self.selectedTheme(self.themes[self.themeList.curselection()[0]])
            except:
                pass
                    
            self.root.update()
    
    except Exception as ex:
        print(ex.args)