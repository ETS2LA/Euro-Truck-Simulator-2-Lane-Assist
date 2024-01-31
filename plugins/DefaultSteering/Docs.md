---
# https://retype.com/configuration/page/
# please also see the docs for components 
# https://retype.com/components/alert/
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-31
icon: stack
visibility: hidden
tags: 
  - documentation
---
!!!warning Warning
This page is meant for `developers`
!!!

## Data variable usage
The plugin will use the following data variable values:
=== [!badge variant="ghost" text="Input"] ‎ data/LaneDetection/difference
The input value from a lane detection plugin.
=== [!badge variant="ghost" text="Input"] ‎ data/api/truckFloat/speed
Input speed from the game. Used to automatically lower steering sensitivity at high speeds.
=== [!badge variant="ghost" text="Input"] ‎ data/api/truckBool/blinkerLeftActive (and right)
Used to disable the steering when indicating.
=== [!badge variant="dark" text="Output"] ‎ data/Controller/leftStick
The output value to the game. Goes from -1 to 1.
===

### Example
Copied from the BetterCamScreenCapture plugin:
```python
def plugin(data):
    steeringOutput = data["Controller"]["leftStick"]
    # Do something with the steeringOutput

    return data
```