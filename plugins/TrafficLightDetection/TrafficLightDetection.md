---
# https://retype.com/configuration/page/
# please also see the docs for components 
# https://retype.com/components/alert/
authors: 
  - name: Glas42
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/145870870?v=4
date: 2024-1-31
icon: stack
tags:
  - plugin
---

### Description
This plugin is able to detect traffic lights and their state by looking at the users screen.

### Usage
To use this plugin you will have to set the screencapture area and select the settings you want to use for the detection. 
**It is however important to note that this plugin won't do anything without an enabled screen capture method.**

### Configuration / UI

+++ General

==- Yellow Light Detection
Set whether the yellow light detection should be enabled or not. However, for performance reasons, it is recommended to leave it disabled.
==-

==- Performance Mode
Set whether the performance mode should be enabled or not. This will increase the performance of the plugin by disabling the green light detection.
==-

==- Advanced Settings
Enable this if you want to use the settings you set in the advanced settings tab.
==-


+++ Screen Capture

==- Use Full Frame
If enabled, the TrafficLightDetection will look at the top top two thirds of the screen for detection.
==-

==- X1, Y1, X2, Y2 Sliders
You can set your own screencapture area with these four sliders, X1 and Y1 set the top left corner and X2 and Y2 the bottom right corner of the screencapture area.
!!!warning Warning
To set your own area, you need to disable the Use Full Frame option.
!!!
==-


+++ Output Window

==- Final Window, Grayscale Window, Red/Yellow/Green Window
These window can output the results of the detection.
==-

==- Automatic Windowsize
If enabled, the Window Width and Window Height sliders will no longer have any effect and the output window keeps the aspect ratio of the captured frame, however you can still set the size of the output window with the Window Scale slider.
==-

==- Window Width, Window Height, Window Scale Sliders
You can set the size of the output window with these three sliders.
==-


+++ Tracker/AI

==- Do Yolo Detection confirmation
If enabled, the app tracks the detected traffic lights and confirms them with the YOLO object detection.
What this means: higher accuracy, but a small lag every time the detection detects a new traffic light.
==-

==- Show unconfirmed traffic lights
If enabled, the unconfirmed or wrongly detected traffic lights will be shown in gray.
==-

==- YOLOv5 Model
YOLO object detection has some pretrained models, which can be selected here. It is recommended to use the YOLOv5n model as it is the fastest model. Keep in mind that models with higher accuracy are slower and could lag the app more.
Don't forget to press "Save and Load Model" if you changed the model.
==-


+++ Advanced

==- Color Settings
You can set your own 8-bit color masks in the RGB format for the detection here. The input field only accepts values from 0 to 255.
==-

==- Rect Size Filter
The size of the light of the traffic light must be within the allowed size you can set with the two sliders at the bottom.
==-

==- Width Height Ratio Filter
The ratio of the width to the height of the light of the traffic light must be near 1 for a contour to be considered a traffic light.
==-

==- Pixel Percentage Filter
The non-zero percentage of the light in a square around the traffic light must be near 78.5 for a contour to be considered a traffic light.
==-

==- Other Lights Filter
A contour will only be considered a traffic light if the other two lights of the traffic light are off.
==-

==- Min. Traffic Light Size Filter, Max. Traffic Light Size Filter Sliders
You can set the min and max size of a contour to be considered as a traffic light.
(look Rect Size Filter for more information)
==-

+++


### Installation
This plugin will install the following python packages:
=== opencv-python
Used for image processing, in this case we use it to detect contours, create masks and draw symbols.
=== numpy
Used for image processing, in this case we use it to create masks.
=== pyautogui
Used for some calculations, in this case to get the screen size.
=== ctypes
Used for detecting the output window.
=== math
Used for some calculations.
===