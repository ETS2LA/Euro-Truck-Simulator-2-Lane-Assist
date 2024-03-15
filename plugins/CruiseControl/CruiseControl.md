---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
  - name: Glas42
    link: https://github.com/Glas42
    avatar: https://avatars.githubusercontent.com/u/145870870?v=4
date: 2024-3-15
icon: stack
tags: 
  - plugin
---
# CruiseControl

### Description
CruiseControl is a plugin that keeps your truck going at the speed limit using in-game ACC. Because it uses the in-game ACC, it can accelerate, brake and stop for other vehicles and obstacles.

### Usage
Enable the CruiseControl plugin and configure the setttings shown below.

### Configuration / UI
+++ General
==- Automatically enable cruise control when available
Enabling this feature will automatically enable in-game cruise control when you are fast enough (30kph).
==-

==- Stop the truck when a red traffic light is detected
!!!warning Important
This feature will only work if the TrafficLightDetection plugin is enabled and set up. See the TrafficLightDetection plugin documentation for more information.
!!!

Enabling this feature will stop the truck when a red traffic light is detected.
==-

==- Automatically accelerate when the traffic light turns green
!!!warning Important
This feature will only work if the TrafficLightDetection plugin is enabled and set up. See the TrafficLightDetection plugin documentation for more information.
!!!

Enabling this feature will automatically accelerate the truck back to the speed limit when a red traffic light turns green.
==-

==- Automatically accelerate to the target speed, even when the truck is standing still
!!! Info
Automatic acceleration will not work if lane assist is disabled.
!!!

Enabling this feature will accelerate to the target speed, which is the speed limit, even when the truck is standing still.
==-

==- Automatically enable the hazard light, when the user does an emergency stop
Enabling this feature will automatically enable the hazard flashers, when the user stops the truck by fully pressing the brakes.
==-

==- Automatically come to a stop and enable the hazard lights if no lane is detected
!!!warning Important
This feature will only work if the NavigationDetection plugin is enabled and set up. See the NavigationDetection plugin documentation for more information.
!!!

If no lane is detected, the truck will automatically come to stop and enable hazard flashers. This will prevent the truck from crashing into other vehicles or objects.
==-

==- Show cruise control symbol in the Lane Assist window. (ShowImage Plugin)

Enabling this feature will show the cruise control symbol in the Lane Assist window. It will look like this:
![Cruise Control Symbol](/assets/CruiseControl/cruisecontrol_on_set.png)
==-

==- Acceleration strength in percent (%)
Strength of acceleration from 0 to 100. This has only an effect when using the cruise control under 30kph. Choose wiith the slider or text box.
==-

==- Brake strength in percent (%)
Strength of braking from 0 to 100. This is the brake strength used to stop the truck at red traffic lights. Choose wiith the slider or text box.
==-
+++

### Requirements
=== TruckSimApi
Allows CruiseControl to get data from the game, including speed, and speed limit.
=== SDKController
Allows CruiseControl to send input to the game, including acceleration and brake.
===

### Installation
This plugin will install the following python packages:
=== opencv-python
Used for image processing, in this case we use it to show the cruise control symbol on the ShowImage frame.
=== numpy
Used for image processing, in this case we use it to create masks.
=== ctypes
Used to detect if the user is in the game.
===