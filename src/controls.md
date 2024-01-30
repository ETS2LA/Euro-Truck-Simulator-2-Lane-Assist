---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: pencil
---

!!!warning Warning
This page is meant for `developers`
!!!

## Directly usable functions and values
```python
from src.controls import RegisterKeybind, GetKeybindValue, ChangeKeybind

# This function is used to register a keybind for the keybind manager.
RegisterKeybind(name:str, 
                callback=None, 
                notBoundInfo:str="", 
                description:str="", 
                axis:bool=False, 
                defaultButtonIndex:int=-1, 
                defaultAxisIndex:int=-1
                ) # returns nothing

# Conversely this one is used to get the current value of said keybind.
GetKeybindValue(name:str) # returns either a bool or a float depending on the keybind type.

# If you want to trigger the keybind change window manually, then you can use this one
ChangeKeybind(name:str, callback=None):
```

## Description
The controls.py file is used to interface with user input devices. You register keybinds that the user can then change in the settings menu. This makes it easy to add new keybinds to your plugin without having to worry about the technicality of implementing the checks.