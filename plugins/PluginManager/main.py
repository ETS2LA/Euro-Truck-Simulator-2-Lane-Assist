from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="PluginManager",
    description="Allows you to select different plugins.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static"
)


from src.loading import LoadingWindow
import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
from src.mainUI import quit, switchSelectedPlugin, resizeWindow
import src.variables as variables
import src.settings as settings
import os
from PIL import Image, ImageTk

class UI():
    
    def findPlugins(self):
        print("Importing plugins...")
        # loading = LoadingWindow("Importing plugins...")
        # Find plugins
        path = os.path.join(variables.PATH, "plugins")
        plugins = []
        for file in os.listdir(path):
            if os.path.isdir(os.path.join(path, file)):
                # Check for main.py
                if "main.py" in os.listdir(os.path.join(path, file)):
                    # Check for PluginInformation class
                    try:
                        pluginPath = "plugins." + file + ".main"
                        plugin = __import__(pluginPath, fromlist=["PluginInformation", "onDisable", "onEnable"])
                        if plugin.PluginInfo.type == "dynamic":
                            plugins.append(plugin)
                            print("Found plugin: " + pluginPath)
                    except Exception as ex:
                        print(ex.args)
                        pass
        
        # loading.destroy()
        return plugins
    

    
    def __init__(self, master) -> None:
        self.done = False
        self.master = master
        self.lastTheme = settings.GetSettings("User Interface", "Theme")
        self.lastPlugin = 0
        self.lastList = 0
        resizeWindow(1220, 700)
        self.page0()
        self.selectedPlugin(self.plugins[0])
    
    def destroy(self):
        self.done = True
        self.root.destroy()
        del self

    def tabFocused(self):
        resizeWindow(1220, 700)
    
    def page0(self):
        
        try:
            self.root.destroy()
            del self.plugin
        except: pass
        
        self.root = tk.Canvas(self.master, width=1000, height=590, border=0, highlightthickness=0)
        self.root.grid_propagate(0)
        
        self.plugins = self.findPlugins()
        
        self.listVariable = tk.StringVar()
        self.listVariable.set([helpers.ConvertCapitalizationToSpaces(p.PluginInfo.name) for p in self.plugins if p.PluginInfo.exclusive == None])
        
        self.laneDetectionVariable = tk.StringVar()
        self.laneDetectionVariable.set([helpers.ConvertCapitalizationToSpaces(p.PluginInfo.name) for p in self.plugins if p.PluginInfo.exclusive == "LaneDetection"])
        
        self.screenCaptureVariable = tk.StringVar()
        self.screenCaptureVariable.set([helpers.ConvertCapitalizationToSpaces(p.PluginInfo.name) for p in self.plugins if p.PluginInfo.exclusive == "ScreenCapture"])
        
        self.pluginList = tk.Listbox(self.root, width=20, height=26, listvariable=self.listVariable, font=("Roboto", 12), selectmode="single", activestyle="none", justify="center")
        self.pluginList.grid(row=2, column=0, padx=10, pady=2)
        # Bind double click
        self.pluginList.bind('<Double-Button>', lambda x: self.switchPluginState(self.pluginList.curselection()[0], self.pluginList))
        
        self.laneDetectionList = tk.Listbox(self.root, width=20, height=26, listvariable=self.laneDetectionVariable, font=("Roboto", 12), selectmode="single", activestyle="none", justify="center")
        self.laneDetectionList.grid(row=2, column=1, padx=10, pady=2)
        # Bind double click
        self.laneDetectionList.bind('<Double-Button>', lambda x: self.switchPluginState(self.laneDetectionList.curselection()[0], self.laneDetectionList))
        
        self.screenCaptureList = tk.Listbox(self.root, width=20, height=26, listvariable=self.screenCaptureVariable, font=("Roboto", 12), selectmode="single", activestyle="none", justify="center")
        self.screenCaptureList.grid(row=2, column=2, padx=10, pady=2)
        # Bind double click
        self.screenCaptureList.bind('<Double-Button>', lambda x: self.switchPluginState(self.screenCaptureList.curselection()[0], self.screenCaptureList))
        
        
        self.colorPlugins()
        
        helpers.MakeLabel(self.root, "Misc. Plugins", 0,0, font=("Roboto", 10), padx=30, pady=10, columnspan=1)
        helpers.MakeLabel(self.root, "optional", 1,0, font=("Roboto", 10), padx=30, pady=2, columnspan=1)
        helpers.MakeLabel(self.root, "Lane Detection Plugins", 0,1, font=("Roboto", 10), padx=30, pady=10, columnspan=1)
        helpers.MakeLabel(self.root, "required for lane detection", 1,1, font=("Roboto", 10), padx=30, pady=2, columnspan=1, fg="#cc0000")
        helpers.MakeLabel(self.root, "Screen Capture Plugins", 0,2, font=("Roboto", 10), padx=30, pady=10, columnspan=1)
        helpers.MakeLabel(self.root, "required for lane detection", 1,2, font=("Roboto", 10), padx=30, pady=2, columnspan=1, fg="#cc0000")
        
        self.root.pack(anchor="center", expand=False, ipady=10)
        
        self.root.update()
    
    
    def colorPlugins(self):
        
        enabledPlugins = settings.GetSettings("Plugins", "Enabled")
        if enabledPlugins == None:
            settings.CreateSettings("Plugins", "Enabled", [])
            enabledPlugins = []
            
        # Set plugin colors
        colorTone = settings.GetSettings("User Interface", "Theme")
        if colorTone == None:
            colorTone = "dark"
            
        colors = {
            "darkEnabled": "#204d63",
            "darkDisabled": "#2e2e2e",
            "lightEnabled": "#1e6fbc",
            "lightDisabled": "#d9d9d9"
        }
        
        def colorListbox(listbox, color):
            for i in range(len(listbox.get(0, "end"))):
                if listbox.get(i).replace(" ", "") in enabledPlugins:
                    listbox.itemconfig(i, bg=f"{colors[color + 'Enabled']}", fg="#ffffff")
                else:
                    listbox.itemconfig(i, bg=f"{colors[color + 'Disabled']}")
        
        colorListbox(self.pluginList, colorTone)
        colorListbox(self.laneDetectionList, colorTone)
        colorListbox(self.screenCaptureList, colorTone)

    
    def selectedPlugin(self, plugin):
        try:
            self.pluginInfoFrame.destroy()
        except:
            pass
        
        
        self.plugin = plugin.PluginInfo
        
        
        self.pluginInfoFrame = ttk.LabelFrame(self.root, text=self.plugin.name, width=375, height=580)
        self.pluginInfoFrame.pack_propagate(0)
        self.pluginInfoFrame.grid_propagate(0)
        self.pluginInfoFrame.grid(row=0, column=3, padx=10, pady=2, rowspan=3)
        
        
        if self.plugin.image != None:
            # Load the logo
            self.logo = Image.open(os.path.join(variables.PATH, "plugins", self.plugin.name, self.plugin.image))
            # Resize to height keeping the aspect ratio
            height = 130
            self.logo = self.logo.resize((int(height*self.logo.width/self.logo.height), height), Image.Resampling.BILINEAR)
            self.logo = ImageTk.PhotoImage(self.logo)
            self.logoLabel = tk.Label(self.pluginInfoFrame, image=self.logo)
            self.logoLabel.grid(row=0, column=0, columnspan=1, pady=10, padx=30)
            
            helpers.MakeLabel(self.pluginInfoFrame, self.plugin.name, 0,1, font=("Roboto", 16, "bold"), padx=10, pady=10, columnspan=1, sticky="w")
            
        else:
            helpers.MakeLabel(self.pluginInfoFrame, self.plugin.name, 0,0, font=("Roboto", 16, "bold"), padx=10, pady=10, columnspan=2, sticky="w")
            
        
        helpers.MakeLabel(self.pluginInfoFrame, "Description", 1,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, self.plugin.description, 2,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, "Version", 3,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, self.plugin.version, 4,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, "Author", 5,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, self.plugin.author, 6,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, "URL", 7,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, self.plugin.url, 8,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, "Update point", 9,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
        helpers.MakeLabel(self.pluginInfoFrame, self.plugin.dynamicOrder, 10,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        
        if self.plugin.exclusive != None:
            helpers.MakeLabel(self.pluginInfoFrame, "Exclusive Type", 11,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
            helpers.MakeLabel(self.pluginInfoFrame, self.plugin.exclusive, 12,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")
        
        if self.plugin.requires != None:
            helpers.MakeLabel(self.pluginInfoFrame, "Dependencies", 12,0, font=("Roboto", 12), padx=10, pady=10, columnspan=2, sticky="w")
            helpers.MakeLabel(self.pluginInfoFrame, self.plugin.requires, 13,0, font=("Roboto", 8), padx=10, pady=2, columnspan=2, sticky="w")

        if self.plugin.name in settings.GetSettings("Plugins", "Enabled"):
            helpers.MakeButton(self.pluginInfoFrame, "Disable plugin", lambda: self.disablePlugin(plugin), 14, 0, width=15, padx=8)
        else:
            helpers.MakeButton(self.pluginInfoFrame, "Enable plugin", lambda: self.enablePlugin(plugin), 14, 0, width=15, padx=8)
        
        if not self.plugin.noUI:
            helpers.MakeButton(self.pluginInfoFrame, "Load plugin UI", lambda: switchSelectedPlugin("plugins." + self.plugin.name + ".main"), 14, 1, width=15, padx=8)        
        else:
            helpers.MakeButton(self.pluginInfoFrame, "Load plugin UI", lambda: switchSelectedPlugin("plugins." + self.plugin.name + ".main"), 14, 1, width=15, padx=8, state="disabled")
        
        
    def convertFromListToGlobalIndex(self, list, pluginIndex):
        # Get the name
        plugin = list.get(pluginIndex).replace(" ", "")
        
        # Find the index of the plugin in the plugins array
        for i in range(len(self.plugins)):
            if self.plugins[i].PluginInfo.name == plugin:
                return i
            
        # Check if the plugin is a string
        print("Plugin not found.")
        return 0
        
        
    
    def switchPluginState(self, plugin, list):
        
        # Get the name
        plugin = self.convertFromListToGlobalIndex(list, plugin)
        plugin = self.plugins[plugin]
        
        if plugin.PluginInfo.name in settings.GetSettings("Plugins", "Enabled"):
            self.disablePlugin(plugin)
        else:
            self.enablePlugin(plugin)
    
    def disablePlugin(self, plugin):
        settings.RemoveFromList("Plugins", "Enabled", plugin.PluginInfo.name)
        variables.UpdatePlugins()
        plugin.onDisable()
        try:
            self.page0()
        except:
            pass
        
    def enablePlugin(self, plugin):
        # Check for exclusivity
        if plugin.PluginInfo.exclusive != None:
            from tkinter import messagebox
            if messagebox.askokcancel("Exclusive plugin", "This plugin is exclusive, enabling it will disable all other exclusive plugins of type '" + plugin.PluginInfo.exclusive + "'."):
                for otherPlugin in self.plugins:
                    if otherPlugin.PluginInfo.exclusive != None:
                        if otherPlugin.PluginInfo.exclusive == plugin.PluginInfo.exclusive:
                            settings.RemoveFromList("Plugins", "Enabled", otherPlugin.PluginInfo.name)
            else: return
            
        if plugin.PluginInfo.requires != None:
            from tkinter import messagebox
            if messagebox.askokcancel("Required plugins", "This plugin requires other plugins to work, enabling it will enable all required plugins.\n\n" + "\n".join(plugin.PluginInfo.requires) + "\n\nDo you want to continue?"):
                for otherPlugin in self.plugins:
                    if otherPlugin.PluginInfo.name in plugin.PluginInfo.requires:
                        settings.AddToList("Plugins", "Enabled", otherPlugin.PluginInfo.name)
            else:
                return
            
        settings.AddToList("Plugins", "Enabled", plugin.PluginInfo.name)
        variables.UpdatePlugins()
        plugin.onEnable()
        self.page0()
        #helpers.MakeLabel(self.root, "Restart Required", 11, 0, font=("Roboto", 12, "bold"), padx=10, pady=2, columnspan=1, sticky="n")
    
    def update(self, data):
        try:
            
            # Check which list is selected
            if self.pluginList.curselection() != ():
                if self.pluginList.curselection()[0] != self.lastPlugin or self.lastList != 0:
                    self.lastList = 0
                    self.lastPlugin = self.pluginList.curselection()[0]
                    self.selectedPlugin(self.plugins[self.convertFromListToGlobalIndex(self.pluginList, self.pluginList.curselection()[0])])
            elif self.laneDetectionList.curselection() != ():
                if self.laneDetectionList.curselection()[0] != self.lastPlugin or self.lastList != 1:
                    self.lastList = 1
                    self.lastPlugin = self.laneDetectionList.curselection()[0]
                    self.selectedPlugin(self.plugins[self.convertFromListToGlobalIndex(self.laneDetectionList, self.laneDetectionList.curselection()[0])])
            elif self.screenCaptureList.curselection() != ():
                if self.screenCaptureList.curselection()[0] != self.lastPlugin or self.lastList != 2:
                    self.lastList = 2
                    self.lastPlugin = self.screenCaptureList.curselection()[0]
                    self.selectedPlugin(self.plugins[self.convertFromListToGlobalIndex(self.screenCaptureList, self.screenCaptureList.curselection()[0])])
            
        except:
            try:
                self.plugin
            except:
                self.selectedPlugin(self.plugins[0])
        
        if settings.GetSettings("User Interface", "Theme") != self.lastTheme:
            self.lastTheme = settings.GetSettings("User Interface", "Theme")
            self.colorPlugins()
        
        self.root.update()
    