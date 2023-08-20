from src.logger import print

'''
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.
'''

import time
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import src.helpers as helpers
from tkinter import font
import src.variables as variables
from src.loading import LoadingWindow
from src.logger import print
import src.settings as settings

def CreateRoot():
    global root
    global buttonFrame
    global pluginFrame
    global width
    global height
    global fps
    
    try:
        root.destroy()
    except:
        pass  
    
    width = 800
    height = 600

    root = tk.Tk()
    root.title("Lane Assist")


    root.resizable(False, False)
    root.geometry(f"{width}x{height}")
    root.protocol("WM_DELETE_WINDOW", lambda: quit())

    try:
        sv_ttk.inited = False
        sv_ttk.set_theme(settings.GetSettings("User Interface", "Theme"))
    except:
        try:
            sv_ttk.inited = False
            sv_ttk.set_theme("dark")
        except:
            # We remade the root and it already had a theme
            pass


    # Bottom text
    ttk.Label(root, text="ETS2 Lane Assist (1.1.6)   ©Tumppi066 - 2023", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
    fps = tk.StringVar()
    ttk.Label(root, textvariable=fps, font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)

    # Left button bar
    buttonFrame = ttk.LabelFrame(root, text="Lane Assist", width=width-675, height=height-20)
    buttonFrame.pack_propagate(0)
    buttonFrame.grid_propagate(0)


    # Plugin frame
    buttonFrame.pack(side="left", anchor="n", padx=10, pady=10)
    pluginFrame = ttk.LabelFrame(root, text="Selected Plugin", width=width, height=height-20)
    pluginFrame.pack_propagate(0)
    pluginFrame.grid_propagate(0)

    pluginFrame.pack(side="left", anchor="w", padx=10, pady=10)

    def Reload():
        variables.RELOAD = True

    # Bind F5 to drawButtons
    root.bind("<F5>", lambda e: Reload())

    root.update()

    # Stack overflow comes to the rescue once again here
    # https://stackoverflow.com/a/44422362
    import ctypes

    # Query DPI Awareness (Windows 10 and 8)
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    print(awareness.value)

    # Set DPI Awareness  (Windows 10 and 8)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(0)
    # the argument is the awareness level, which can be 0, 1 or 2:
    # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)


CreateRoot()

def quit():
    global root
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # Destroy the root window
        root.destroy()
        del root

def drawButtons(refresh=False):
    global enableButton
    global themeButton
    
    if refresh:
        CreateRoot()
    
    for child in pluginFrame.winfo_children():
        child.destroy()
        
    for child in buttonFrame.winfo_children():
        child.destroy()
    
    helpers.MakeButton(pluginFrame, "Panel Manager", lambda: switchSelectedPlugin("plugins.PanelManager.main"), 0, 0, width=20)
    helpers.MakeButton(pluginFrame, "Plugin Manager", lambda: switchSelectedPlugin("plugins.PluginManager.main"), 1, 0, width=20)
    helpers.MakeButton(pluginFrame, "First Time Setup", lambda: switchSelectedPlugin("plugins.FirstTimeSetup.main"), 2, 0, width=20, style="Accent.TButton")
    helpers.MakeLabel(pluginFrame, "You can use F5 to refresh the UI and come back to this page.\n(as long as the app is disabled)", 0, 1)
    enableButton = helpers.MakeButton(buttonFrame, "Enable", lambda: (variables.ToggleEnable(), enableButton.config(text=("Disable" if variables.ENABLELOOP else "Enable"))), 0, 0, width=10, padx=9, style="Accent.TButton")
    helpers.MakeButton(buttonFrame, "Panels", lambda: switchSelectedPlugin("plugins.PanelManager.main"), 1, 0, width=10, padx=9)
    helpers.MakeButton(buttonFrame, "Plugins", lambda: switchSelectedPlugin("plugins.PluginManager.main"), 2, 0, width=10, padx=9)
    helpers.MakeButton(buttonFrame, "Performance", lambda: switchSelectedPlugin("plugins.Performance.main"), 3, 0, width=10, padx=9)
    helpers.MakeButton(buttonFrame, "Settings", lambda: switchSelectedPlugin("plugins.Settings.main"), 4, 0, width=10, padx=9)
    helpers.MakeButton(buttonFrame, "About", lambda: switchSelectedPlugin("plugins.About.main"), 5, 0, width=10, padx=9)
    themeButton = helpers.MakeButton(buttonFrame, sv_ttk.get_theme().capitalize() + " Mode", lambda: changeTheme(), 6, 0, width=10, padx=9)
    import webbrowser
    helpers.MakeButton(buttonFrame, "Discord", lambda: webbrowser.open("https://discord.gg/DpJpkNpqwD"), 7, 0, width=10, padx=9, style="Accent.TButton")

prevFrame = 100
def update(data):
    global fps
    global prevFrame
    global ui
    
    # Calculate the UI caused overhead
    frame = time.time()
    try:
        fps.set(f"UI FPS: {round((frame-prevFrame)*1000)}ms ({round(1/(frame-prevFrame))}fps)")
    except: pass
    prevFrame = frame
        
    try:
        ui.update(data)
    except Exception as ex:
        if "name 'ui' is not defined" not in str(ex):
            print(str(ex))
        pass

    try:
        root.update()
    except:
        raise Exception("The main window has been closed.", "If you closed the app this is normal.")
    
    
def switchSelectedPlugin(pluginName):
    global pluginFrame
    global ui
    global root
    
    resizeWindow(width, height)
    
    plugin = __import__(pluginName, fromlist=["UI", "PluginInfo"])
    
    if plugin.PluginInfo.disablePlugins == True and settings.GetSettings("Plugins", "Enabled") != []:
        if messagebox.askokcancel("Plugins", "The panel has asked to disable all plugins. Do you want to continue?"):
            settings.CreateSettings("Plugins", "Enabled", [])
            variables.UpdatePlugins()
            
        else: return
        
    if plugin.PluginInfo.disableLoop == True and variables.ENABLELOOP == True:
        if messagebox.askokcancel("Plugins", "The panel has asked to disable the mainloop. Do you want to continue?"):
            variables.ToggleEnable()
            enableButton.config(text=("Disable" if variables.ENABLELOOP else "Enable"))
        
        else: return
        
    try:
        pluginFrame.destroy()
    except:
        pass
    
    pluginFrame = ttk.LabelFrame(root, text=pluginName.split(".")[1], width=width, height=height-20)
    pluginFrame.pack_propagate(0)
    pluginFrame.grid_propagate(0)
    
    
    ui = plugin.UI(pluginFrame)
    pluginFrame.pack(side="left", anchor="n", padx=10, pady=10, expand=True)
    
    print("Loaded " + pluginName)
    
def resizeWindow(newWidth, newHeight):
    global root
    root.geometry(f"{newWidth}x{newHeight}")
    
    pluginFrame.config(width=newWidth, height=newHeight)
    
    root.update()
        
def changeTheme():
    global themeButton
    #loading = LoadingWindow("Changing theme...", root)
    sv_ttk.toggle_theme()
    settings.CreateSettings("User Interface", "Theme", sv_ttk.get_theme())
    themeButton.config(text=sv_ttk.get_theme().capitalize() + " Mode")
    #loading.destroy()