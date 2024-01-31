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
tags:
  - plugin
  - before controller
---

### Description
This plugin handles converting the steering offset from the lane detection models into a usable output for the game.

### Usage
This plugin will just work when it's enabled. 
**It is however important to note that this plugin won't do anything without a lane detection model, or a way of outputting the steering offset to the game.**

### Configuration / UI

+++ General

==- Steering Offset
Will control how much the steering will be offset from the center of the lane detection model. This is useful if you find the truck driving too far to the right or left.
==- Control Smoothness
Will control how many frames the steering offset will be averaged over. This will control how "smooth" the steering will be.
!!!warning Warning
Setting this value too high, especially on low FPS, will cause "bouncing" between the lanes.
!!!
==- Sensitivity
Will control the multiplier on the steering. Essentially changing how much the app is responding to the input commands from the lane detection model.
==- Maximum Control
The maximum control the app is allowed to output. 1 is the maximum, 0 is the minimum.
==-

+++ Gamepad

==- Gamepad mode
Will smooth the input from the controller to the app. If you are using a gamepad then this is basically required.
==- Control Smoothness
Will control how many frames the steering offset will be averaged over. This will control how "smooth" the steering will be.
==-
!!! Note
This page is only necessary if you are using vgamepad to replace the main steering axis in game. 
!!!

+++ Keyboard

==- Keyboard Mode
Will listen to keyboard inputs instead of controller inputs.
==- Keyboard Sensitivity
How fast the steering will react to the keyboard inputs.
==- Keyboard Return Sensitivity
How fast the steering will return to the center when no keyboard inputs are detected.
==-
!!! Note
This page is only necessary if you are using vgamepad to replace the main steering axis in game. 
!!!

+++


### Installation
This plugin will install the following python packages:
=== opencv-python
Used for image processing, in this case we use it to draw text on the output frame.
=== pygame
Used for gamepad input
=== keyboard
Used for keyboard input
===

### Requirements
This plugin needs and will enable the following plugins:
=== TruckSimAPI
Used to communicate with the game.
===
[!button Developer Documentation](Docs.md)