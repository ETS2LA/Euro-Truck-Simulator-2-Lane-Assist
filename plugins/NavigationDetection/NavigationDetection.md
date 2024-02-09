---
# https://retype.com/configuration/page/
# please also see the docs for components 
# https://retype.com/components/alert/
authors: 
  - name: Glas42
    link: https://github.com/Glas42
    avatar: https://avatars.githubusercontent.com/u/145870870?v=4
date: 2024-2-9
icon: stack
tags:
  - plugin
  - lane detection
---

### Description
This plugin is used to detect the lane from the route advisor.

### Usage
To use this plugin you will have to do these steps:
Do the Setup of the NavigationDetection Plugin
Enable a screen capture plugin (BetterCamScreenCapture is recommended)
Enable the Default Steering Plugin
Enable the Truck SimAPI
Enable the SDK Controller
**It is important to enable all the named plugins above for the plugin to work**

### Configuration / UI

+++ General

==- Lane Offset
You can set a offset to the center of the lane if the truck is not driving in the middle of the lane.
==-

==- Left-hand traffic
The plugin is able to detect which lane it needs to follow even if multiple lanes are detected, but sometimes it could happen that the automatic lane selection is not working properly, in this case it will switch to a different lane selection method where it needs to know from the user if it is left-hand traffic.
==-

==- Lane Changing
If enabled, you can switch the lane you are driving on using the games indicators or the buttons you set in the controls menu.
-> Lane Changing Speed: Set the speed of the lane changing.
-> Lane Width: Set how much the truck has go left or right to change the lane.
==-


+++ Setup

==- Automatic Setup
If you press this button, the app will open a setup window, which will guide you through the automatic setup of the NavigationDetection Plugin.
Make sure that the games route advisor is visible all the time!
==-

==- Manual Setup
If you press this button, the app will open a setup window, where you need to do the following steps:
->Press "Set Top Left Coordinate of Map", then click on the topleft corner of the route advisor.
->Press "Set Bottom Right Coordinate of Map", then click on the bottom right corner of the route advisor.
->Press "Set Top Left Coordinate of Arrow", then click on the topleft corner of the blue arrow in the route advisor.
->Press "Set Bottom Right Coordinate of Arrow", then click on the bottom right corner of the blue arrow in the route advisor.
->Press "Finish Setup" to save the changes and close the setup window.
You can look at the Example Image window (it opens when you start the setup) for more information.
==-


+++ Advanced

==- Automatically change to lane 0
If enabled, the plugin will automatically change to the original lane if the plugin detects a upcoming turn.
==-

+++


### Installation
This plugin will install the following python packages:
=== opencv-python
Used for image processing, in this case to detect the lane and draw symbols.
=== numpy
Used for image processing, in this case we use it to create masks.
=== subprocess
Used for launching the setup scripts.
=== ctypes
Used to check if F5 is pressed.
=== time
Used for timing.
=== os
Used to check if necessary files exist.
===