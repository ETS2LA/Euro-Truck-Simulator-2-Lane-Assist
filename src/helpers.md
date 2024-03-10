---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: question
order: 99
---

!!!warning Warning
This page is meant for `developers`
!!!
!!! Note
This file is extremely important for building UIs in both plugins and panels.
!!!

## Directly usable functions and values
```python
from src.helpers import *

# Make a standard button.
MakeButton(parent, text:str, command, 
           row:int, column:int, style:str="TButton", 
           width:int=15, center:bool=False, padx:int=5, 
           pady:int=10, state:str="!disabled", columnspan:int=1, 
           rowspan:int=1, translate:bool=True, sticky:str="n", 
           tooltip="", autoplace:bool=False
           )

# Make a standard checkbutton (checkbox).
MakeCheckButton(parent, text:str, category:str, 
                setting:str, row:int, column:int, 
                width:int=17, values=[True, False], onlyTrue:bool=False, 
                onlyFalse:bool=False, default=False, translate:bool=True, 
                columnspan:int=1, callback=None, tooltip="", 
                autoplace:bool=False
                )

# Make a standard combo entry.
# NOTE: This will place the label on the column provided, and the entry on the next column.
MakeComboEntry(parent, text:str, category:str, 
               setting:str, row: int, column: int, 
               width: int=10, labelwidth:int=15, isFloat:bool=False, 
               isString:bool=False, value="", sticky:str="w", 
               labelSticky:str="w", translate:bool=True, labelPadX:int=10, 
               tooltip="", autoplace:bool=False
               )

# Make a standard label.
MakeLabel(parent, text:str, row:int, 
          column:int, font=("Segoe UI", 10), pady:int=7, 
          padx:int=7, columnspan:int=1, sticky:str="n", 
          fg:str="", bg:str="", translate:bool=True, 
          tooltip="", autoplace:bool=False
          )

# Make an empty line.
MakeEmptyLine(parent, row:int, column:int, 
              columnspan:int=1, pady:int=7, autoplace:bool=False
              )

# Open a web view
# NOTE: This is blocking the main thread. The app will not continue until the web view is closed.
OpenWebView(title:str, urlOrFile:str, width:int=900, height:int=700)

# Open a url in a browser.
OpenInBrowser(url:str)

# Convert capitalization to spaces. This is useful for converting plugin names.
ConvertCapitalizationToSpaces(text:str)

# A more accurate sleep function, use this instead of time.sleep().
# NOTE: THIS IS BLOCKING
AccurateSleep(seconds:float)

# Run the code in the main thread (next time the thread is run)
RunInMainThread(func, *args, **kwargs)
```

## Example

The most basic way of using these is as follows:
```python
import src.helpers as helpers

# Assuming we are in a UI class so we have access to `self.root`.
helpers.MakeLabel(self.root, "Label text", 0, 0, autoplace=True)
helpers.MakeButton(self.root, "Button text", lambda: print("Button pressed"), 0, 0, autoplace=True)
# If autoplace = True then you don't need to specify the row.
# We can still specify the column to have multiple elements on a row.
helpers.MakeButton(self.root, "Button text 2", lambda: print("Button 2 pressed"), 0, 1, autoplace=True)
```
This example on the other hand is most of the code for the main menu.
Notice how I use the autoplace parameter to calculate the rows.
```python
import src.helpers as helpers
import src.variables as variables
from src.mainUI import switchSelectedPlugin

# Offset row 1 to the center of the window.
helpers.MakeLabel(pluginFrames[0], "                      ", 0, 0, autoplace=True)
# Make column 1 the default so that the autoplace function will calculate the rows from column 1.
helpers.defaultAutoplaceColumn = 1 # Will be reset to 0 after the root changes.
helpers.MakeLabel(pluginFrames[0], f"You are running ETS2LA version {str(variables.VERSION)}", 0, 1, columnspan=2, font=("Roboto", 18, "bold"), autoplace=True)

helpers.MakeButton(pluginFrames[0], "Panel Manager", lambda: switchSelectedPlugin("plugins.PanelManager.main"), 0, 1, width=20, autoplace=True)
helpers.MakeButton(pluginFrames[0], "Plugin Manager", lambda: switchSelectedPlugin("plugins.PluginManager.main"), 0, 2, width=20, autoplace=True)
helpers.MakeButton(pluginFrames[0], "First Time Setup", lambda: switchSelectedPlugin("plugins.FirstTimeSetup.main"), 0, 1, width=20, style="Accent.TButton", autoplace=True)
helpers.MakeButton(pluginFrames[0], "LANGUAGE - 语言设置", lambda: switchSelectedPlugin("plugins.DeepTranslator.main"), 0, 2, width=20, style="Accent.TButton", translate=False, autoplace=True)
helpers.MakeButton(pluginFrames[0], "Video Tutorial ↗ ", lambda: helpers.OpenInBrowser("https://www.youtube.com/watch?v=0pic0rzjvik"), 0, 1, width=20, autoplace=True, tooltip="https://www.youtube.com/watch?v=0pic0rzjvik")
helpers.MakeButton(pluginFrames[0], "ETS2LA Wiki ↗ ", lambda: helpers.OpenInBrowser("https://wiki.tumppi066.fi/en/LaneAssist"), 0, 2, width=20, autoplace=True, tooltip="https://wiki.tumppi066.fi/en/LaneAssist")
helpers.MakeEmptyLine(pluginFrames[0], 0, 1, columnspan=2, autoplace=True)
helpers.MakeLabel(pluginFrames[0], "You can use F5 to refresh the UI and come back to this page.\n                    (as long as the app is disabled)", 0, 1, columnspan=2, autoplace=True)
helpers.MakeLabel(pluginFrames[0], "The top of the app has all your currently open tabs.\n They can be closed with the middle mouse button.\n        (or right mouse button if so configured)", 0, 1, columnspan=2, autoplace=True)
```

## Description
Provides helper functions for mainly building UIs.