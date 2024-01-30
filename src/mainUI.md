---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: browser
title: Main UI
---

!!!warning Warning
This page is meant for `developers`
!!!
!!! Note
There are more functions and values available, but they are either not meant for direct use or are so obscure that they are not documented here.
!!!

## Directly usable functions and values
```python
from src.mainUI import switchSelectedPlugin, resizeWindow, quit

# Should be in the following format "plugins.<pluginName>.main"
switchSelectedPlugin(pluginName:str)

# Will resize the window to the given size.
resizeWindow(newWidth:int, newHeight:int)

# Will quit the program.
quit()
```

## Description
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.