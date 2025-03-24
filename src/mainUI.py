'''
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.

Main functions to take note of for plugins:
```python
# Should be in the following format "plugins.<pluginName>.main"
switchSelectedPlugin(pluginName:str)

# Will resize the window to the given size.
resizeWindow(newWidth:int, newHeight:int)
```'''

from src.logger import print
import time
import tkinter as tk
from tkinter import ttk, messagebox
import src.helpers as helpers
from tkinter import font
import src.variables as variables
from src.loading import LoadingWindow
from src.logger import print
import src.settings as settings
from src.translator import Translate
import plugins.ThemeSelector.main as themeSelector
from tktooltip import ToolTip
import src.server as server

print_ui_events = settings.GetSettings("Dev", "print_ui_events", False)

root = None
"""The root tk.Tk() window of the program."""

def DeleteRoot():
    """Will delete the root window and save it's location.
    """
    global root
    
    # Save the current position
    x = root.winfo_x()
    y = root.winfo_y()
    settings.CreateSettings("User Interface", "Position", [x, y])
    
    try:
        root.destroy()
        del root
    except:
        pass

lastClosedTabName = "About"
def closeTab(event):
    """Will close a tab based on the tkinter input event. Not intended to be called directly.

    Args:
        event (tkInputEvent): The input event that was triggered.
    """
    global lastClosedTabName
    try:
        index = pluginNotebook.tk.call(pluginNotebook._w, "identify", "tab", event.x, event.y)
        # Get plugin name from the pluginNotebook
        pluginName = pluginNotebook.tab(index, "text")
        pluginNotebook.forget(index)
        pluginFrames.pop(index)
        UIs.pop(index)
        lastClosedTabName = pluginName
        settings.RemoveFromList("User Interface", "OpenTabs", pluginName)
    except:
        pass

def closeTabName(name:str):
    """Close a tab with the given name.

    Args:
        name (str): Name of the tab to close.
    """
    global lastClosedTabName
    try:
        for i in range(len(pluginFrames)):
            if pluginNotebook.tab(i, "text") == name:
                pluginNotebook.forget(i)
                pluginFrames.pop(i)
                UIs.pop(i)
                lastClosedTabName = name
                settings.RemoveFromList("User Interface", "OpenTabs", name)
                break
    except:
        import traceback
        traceback.print_exc()
        pass

def selectedOtherTab():
    """Will run when the user selects another tab. Not intended to be called directly.
    """
    try:
        currentUI = UIs[pluginNotebook.index(pluginNotebook.select())]
        # Run the UI tab focus function
        if currentUI != None:
            try:
                currentUI.tabFocused()
            except:
                resizeWindow(width, height)
        else:
            resizeWindow(width, height)
    except:
        pass

def switchSelectedPlugin(pluginName:str):
    """Will open a new tab with the given plugin name.

    Args:
        pluginName (str): Enter the plugin name in the format of "plugins.<pluginName>.main"
    """
    global plugin
    global pluginFrame
    global pluginFrames
    global ui
    global root

            
    # Check if the plugin is already loaded
    notebookNames = []
    for tab in pluginNotebook.tabs():
        notebookNames.append(pluginNotebook.tab(tab, "text"))
    
    if "main" in pluginName or "src" in pluginName:
        if pluginName.split(".")[1] in notebookNames:
            pluginNotebook.select(notebookNames.index(pluginName.split(".")[1]))
            ui = UIs[pluginNotebook.index(pluginNotebook.select())]
            plugin = __import__(pluginName, fromlist=["UI", "PluginInfo"])
            return
    else:
        if pluginName.split(".")[1] + "." + pluginName.split(".")[2] in notebookNames:
            pluginNotebook.select(notebookNames.index(pluginName.split(".")[1] + "." + pluginName.split(".")[2]))
            ui = UIs[pluginNotebook.index(pluginNotebook.select())]
            plugin = __import__(pluginName, fromlist=["UI", "PluginInfo"])
            return
       
    plugin = __import__(pluginName, fromlist=["UI", "PluginInfo"])

    if plugin.PluginInfo.disablePlugins == True and (settings.GetSettings("Plugins", "Enabled") != []):
        if helpers.AskOkCancel("Plugins", Translate("The panel has asked to disable all plugins. Do you want to continue?")):
            settings.CreateSettings("Plugins", "Enabled", [])
            variables.UpdatePlugins()
        else: 
            return
        
    if plugin.PluginInfo.disableLoop == True and variables.ENABLELOOP == True:
        if helpers.AskOkCancel("Plugins", Translate("The panel has asked to disable the mainloop. Do you want to continue?")):
            variables.ToggleEnable()
            enableButton.config(text=(Translate("Disable") if variables.ENABLELOOP else Translate("Enable")))
        
        else: return
        
        
        
    # Create a new frame for the plugin in the notebook
    pluginFrame = ttk.Frame(pluginNotebook, width=width, height=height-20)
    pluginFrame.pack_propagate(0)
    pluginFrame.grid_propagate(0)
    
    ui = plugin.UI(pluginFrame)
    UIs.append(ui)
    
    pluginFrames.append(pluginFrame)
    pluginNotebook.add(pluginFrame, text=plugin.PluginInfo.name)
    
    pluginNotebook.select(pluginFrames.index(pluginFrame))
    
    if print_ui_events == True:
        print("Loaded " + pluginName)
    
    settings.AddToList("User Interface", "OpenTabs", plugin.PluginInfo.name, exclusive=True)
    
    if variables.WINDOWSCALING != 100:
        ui.root.update()
        # Increase the ui.root size based on the scaling
        ui.root.config(width=ui.root.winfo_width() * (variables.WINDOWSCALING / 100), height=ui.root.winfo_height() * (variables.WINDOWSCALING / 100))
        ui.root.update()

def quit():
    """Will kill the root. This means that the program will close on the next update from the mainloop.
    """
    global root
    savePosition()
    if helpers.AskOkCancel("Quit", "Do you want to quit?", yesno=True):
        # Destroy the root window
        root.destroy()
        del root

def addCurrentToFavorites():
    """Will add (or remove) the currently open tab from the favorites."""
    try:
        tabName = plugin.PluginInfo.name
        fullPath = f"plugins.{tabName}.main"
        # Check if the tab is already in the favorites
        favorites = settings.GetSettings("User Interface", "Favorites", value=["plugins.MainMenu.main"])
        if fullPath in favorites:
            settings.RemoveFromList("User Interface", "Favorites", fullPath)
        else:
            settings.AddToList("User Interface", "Favorites", fullPath, exclusive=True)
            
        variables.RELOAD = True
    except:
        print("Failed to add current tab to favorites")

def drawButtons(refresh:bool=False):
    """Will draw the buttons on the left menu.

    Args:
        refresh (bool, optional): Will create the root again. Defaults to False.
    """
    global enableButton
    
    if refresh:
        CreateRoot()
        
    for child in buttonFrame.winfo_children():
        child.destroy()
    
    for child in customButtonFrame.winfo_children():
        child.destroy()
    
    enableButton = helpers.MakeButton(buttonFrame, "Enable", lambda: (variables.ToggleEnable(), enableButton.config(text=("Disable" if variables.ENABLELOOP else "Enable"))), 0, 0, width=11, padx=9, style="Accent.TButton")
    helpers.MakeButton(buttonFrame, "Panels", lambda: switchSelectedPlugin("plugins.PanelManager.main"), 1, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Plugins", lambda: switchSelectedPlugin("plugins.PluginManager.main"), 2, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Performance", lambda: switchSelectedPlugin("plugins.Performance.main"), 3, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Settings", lambda: switchSelectedPlugin("plugins.Settings.main"), 4, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Controls", lambda: switchSelectedPlugin("src.controls"), 5, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Help/About", lambda: switchSelectedPlugin("plugins.About.main"), 6, 0, width=11, padx=9)
    helpers.MakeButton(buttonFrame, "Feedback", lambda: switchSelectedPlugin("plugins.Feedback.main"), 7, 0, width=11, padx=9)
    import webbrowser
    helpers.MakeButton(buttonFrame, "Discord", lambda: webbrowser.open("https://ets2la.com/discord"), 8, 0, width=11, padx=9, style="Accent.TButton", translate=False)

    # Draw the favorites
    helpers.MakeButton(customButtonFrame, "Add/Remove", lambda: addCurrentToFavorites(), 0, 0, width=11, padx=9, autoplace=True, style="Accent.TButton")
    favorites = settings.GetSettings("User Interface", "Favorites", value=["plugins.MainMenu.main"])
    for favorite in favorites:
        name = favorite.split(".")[1]
        name = helpers.ConvertCapitalizationToSpaces(name)
        if len(name) > 11:
            name = name[:10] + "..."
        helpers.MakeButton(customButtonFrame, name, lambda favorite=favorite: switchSelectedPlugin(favorite), 0, 0, width=11, padx=9, autoplace=True)
    

prevFrame = 100
def update(data:dict, dontOpenMenu:bool=False):
    """Update the mainUI.

    Args:
        data (dict): The input data from the mainloop.

    Raises:
        Exception: The root has been killed, most likely due to closing the app.
    """
    global fps
    global prevFrame
    
    # Calculate the UI caused overhead
    frame = time.time()
    try:
        fps.set(f"UI FPS: {round((frame-prevFrame)*1000)}ms ({round(1/(frame-prevFrame))}fps)")
    except: pass
    prevFrame = frame
        
    try:
        # Update the selected plugin
        ui = UIs[pluginNotebook.index(pluginNotebook.select())]
        if ui != None:
            ui.update(data)
    except Exception as ex:
        if "'UI' object has no attribute 'update'" in str(ex):
            print("Currently open panel does not have an update method. Please add one.")
        elif "name 'ui' is not defined" not in str(ex):
            print(str(ex))
        pass

    # Check if no tabs are open
    try:
        if pluginNotebook.index("end") == 0:
            # Open the mainmenu
            switchSelectedPlugin("plugins.MainMenu.main")
    except:
        pass

    try:
        root.update()
    except:
        raise Exception("The main window has been closed.", "If you closed the app this is normal.")
    
def resizeWindow(newWidth:int, newHeight:int):
    """Will resize the window to the given size.

    Args:
        newWidth (int)
        newHeight (int)
    """
    global root
    
    if settings.GetSettings("User Interface", "ScaleWindowBasedOnWindowsSetting", value=True):
        scaling = variables.WINDOWSCALING
        if scaling != 100:
            newWidth = int(newWidth * (scaling / 100))
            newHeight = int(newHeight * (scaling / 100))
    
    # Offsets for the new tabs
    newHeight += 20
    newWidth += 40
    # Offset for the new favorites screen
    newWidth += 150
    # Offsets for fps and copyright at the bottom
    showCopyright = settings.GetSettings("User Interface", "ShowCopyright")
    showFps = settings.GetSettings("User Interface", "ShowFPS")
    if showCopyright:
        newHeight += 16
    if showFps:
        newHeight += 16
    
    root.geometry(f"{newWidth}x{newHeight}")
    pluginNotebook.config(width=newWidth, height=newHeight-20)
    buttonFrame.config(height=newHeight-20)
    customButtonFrame.config(height=newHeight-20)
    root.update()
        
def changeTheme():
    """Would have changed the theme from dark / light to light / dark. Not currently in use.
    """
    print("Changing theme")
    helpers.ShowInfo(Translate("Unfortunately with the change to new themes you can no longer change the mode on the fly.\nThis functionality might return in the future."))
    # global themeButton
    # themeSelector.SwitchThemeType()
    # themeButton.config(text=Translate(settings.GetSettings("User Interface", "Theme")).capitalize() + " Mode")
    
# Save the position of the window if it's closed
def savePosition():
    """Will save the current position of the window.
    """
    global root
    x = root.winfo_x()
    y = root.winfo_y()
    settings.CreateSettings("User Interface", "Position", [x, y])

titlePath = ""    
def UpdateTitle(extraText:str=""):
    """Will update the application title.

    Args:
        extraText (str, optional): Additional text to add after all of the defaults. Defaults to "".

    Returns:
        success (bool, optional): If there was an error then this will return False. Otherwise True.
    """
    showCopyrightInTitlebar = settings.GetSettings("User Interface", "TitleCopyright")
    if showCopyrightInTitlebar == None:
        settings.CreateSettings("User Interface", "TitleCopyright", True)
        showCopyrightInTitlebar = True
    
    try:
        root.title("Lane Assist - ©Tumppi066 2024 " + titlePath + extraText if showCopyrightInTitlebar else "Lane Assist " + titlePath + extraText)
        return True
    except:
        return False

pluginFrames = []
UIs = []
additionals = []
ui = None
def CreateRoot():
    """Will create the root window and set it up.
    """
    global root
    global buttonFrame
    global customButtonFrame
    global pluginFrames
    global UIs
    global pluginNotebook
    global width
    global height
    global fps
    global fpsLabel
    
    # Stack overflow comes to the rescue once again here
    # https://stackoverflow.com/a/44422362
    import ctypes
    wantedAwareness = settings.GetSettings("User Interface", "DPIAwareness", 0)

    # Query DPI Awareness (Windows 10 and 8)
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    #print("Original DPI awareness value : " + str(awareness.value))

    # Set DPI Awareness  (Windows 10 and 8)
    try:
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(wantedAwareness)
        #print("Set DPI awareness value to " + str(wantedAwareness) + " (code " + str(errorCode) + ")")
    except:
        print("Failed to set DPI awareness value")
        #errorCode = ctypes.windll.user32.SetProcessDPIAware()

    # the argument is the awareness level, which can be 0, 1 or 2:
    # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)
    
    
    width = 800
    height = 600

    try:
        root.destroy()
    except:
        pass 
    root = tk.Tk()
    
    UpdateTitle()
    
    # Hack to make windows think we are our own app, and then show our icon
    import ctypes
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    root.iconbitmap(default="assets/favicon.ico")

    # Set the resize
    if not settings.GetSettings("User Interface", "AllowManualResizing", value=False):
        root.resizable(False, False)
    # Load the size and position
    position = settings.GetSettings("User Interface", "Position")
    if position == None:
        root.geometry(f"{width}x{height}")
    else:
        root.geometry(f"{width}x{height}+{position[0]}+{position[1]}")
    root.protocol("WM_DELETE_WINDOW", lambda: quit())
    
    theme = settings.GetSettings("User Interface", "ColorTheme")
    if theme == None:
        theme = "Forest"
        settings.CreateSettings("User Interface", "ColorTheme", theme)
    
    themeSelector.ChangeTheme(theme, root)

    # Check if an image exists in assets/images/wallpaper.png
    # If it does then set it as a background image called and then make a canvas
    try:
        from PIL import Image, ImageTk
        image = Image.open("assets/images/wallpaper.png")
        image = image.resize((width, height), Image.Resampling.BILINEAR)
        image = ImageTk.PhotoImage(image)
        imageLabel = tk.Label(root, image=image)
        imageLabel.image = image
        imageLabel.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass

    # Bottom text
    showCopyright = settings.GetSettings("User Interface", "ShowCopyright")
    if showCopyright == None:
        settings.CreateSettings("User Interface", "ShowCopyright", False)
        showCopyright = False
    if showCopyright:
        ttk.Label(root, text=f"ETS2 Lane Assist ({variables.VERSION})   ©Tumppi066 - 2024", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
    fps = tk.StringVar()
    
    showFps = settings.GetSettings("User Interface", "ShowFPS")
    if showFps == None:
        settings.CreateSettings("User Interface", "ShowFPS", False)
        showFps = False
    if showFps:
        fpsLabel = ttk.Label(root, textvariable=fps, font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)

    # Button Frame
    try:
        buttonFrame.destroy()
    except:
        pass
    
    buttonFrame = ttk.LabelFrame(root, text="Lane Assist", width=width-675, height=height)
    buttonFrame.pack_propagate(0)
    buttonFrame.grid_propagate(0)
    buttonFrame.pack(side="left", anchor="n", padx=10, pady=10)
    
    # Create the custom button frame on the right side of the window
    try:
        customButtonFrame.destroy()
    except:
        pass
    customButtonFrame = ttk.LabelFrame(root, text="Favorites", width=width-675, height=height)
    customButtonFrame.pack_propagate(0)
    customButtonFrame.grid_propagate(0)
    customButtonFrame.pack(side="right", anchor="n", padx=10, pady=10)

    # Create the plugin notebook
    try:
        pluginNotebook.destroy()
    except:
        pass
    pluginNotebook = ttk.Notebook(root, width=width, height=height-20)
    pluginNotebook.pack_propagate(0)
    pluginNotebook.grid_propagate(0)
    
    pluginNotebook.pack(side="left", anchor="n", padx=10, pady=10)
    
    # Make a callback for selecting another tab
    pluginNotebook.bind("<<NotebookTabChanged>>", lambda e: selectedOtherTab())
    
    # Reset the pluginFrames and UIs
    pluginFrames = []
    UIs = []
    
    # Bind middleclick on a tab to close it
    closeMMB = settings.GetSettings("User Interface", "CloseTabMMB")
    if closeMMB == None:
        settings.CreateSettings("User Interface", "CloseTabMMB", True)
        closeMMB = True
    closeRMB = settings.GetSettings("User Interface", "CloseTabRMB")
    if closeRMB == None:
        settings.CreateSettings("User Interface", "CloseTabRMB", False)
        closeRMB = False
        
    if closeMMB:
        pluginNotebook.bind("<Button-2>", lambda e: closeTab(e))
    if closeRMB:
        pluginNotebook.bind("<Button-3>", lambda e: closeTab(e))
    
    # Bind the custom key to close the tab
    try:
        customKey = settings.GetSettings("User Interface", "CustomKey")
        if customKey != None and customKey != "":
            root.bind(f"<{customKey}>", lambda e: closeTab(e))
            print(f"Bound <{customKey}> to close tab")
    except:
        print("Failed to bind custom key to close tab")
    
    # Bind rightclick on a tab to move it to another position
    # TODO: Make this work
    # pluginNotebook.bind("<Button-3>", lambda e: moveTab(e))

    # Bind CTRL Z to undo closing last tab
    root.bind("<Control-z>", lambda e: switchSelectedPlugin(f"plugins.{lastClosedTabName}.main"))
    if print_ui_events == True:
        print("Initialized UI")

    def Reload():
        variables.RELOAD = True

    # Bind F5 to drawButtons
    root.bind("<F5>", lambda e: Reload())
    if print_ui_events == True:
        print("Initialized UI")
    
    # Bind movement of the window to save the position
    # root.bind("<Configure>", lambda e: savePosition(e))

    root.update()
    
    if theme != "SunValley" and theme != "Forest" and theme != "Azure":
        themeSelector.ColorTitleBar(root, override="0x313131")
    else:
        themeSelector.ColorTitleBar(root)
        
    # Open previously open tabs
    ReopenTabs = settings.GetSettings("User Interface", "ReopenTabs")
    if ReopenTabs == None:
        settings.CreateSettings("User Interface", "ReopenTabs", True)
        ReopenTabs = True
        
    if settings.GetSettings("User Interface", "OpenTabs") is not None and ReopenTabs:
        for tab in settings.GetSettings("User Interface", "OpenTabs"):
            if print_ui_events == True:
                print("Loading " + tab)
            try:
                if tab == "controls" or tab == "Changelog" or tab == "FirstTimeSetup":
                    settings.RemoveFromList("User Interface", "OpenTabs", tab)
                    continue
                else:
                    switchSelectedPlugin(f"plugins.{tab}.main")
            except Exception as ex:
                print(ex.args)
                pass

    if print_ui_events == True:
        print("Loaded previously open tabs")

    root.update()
