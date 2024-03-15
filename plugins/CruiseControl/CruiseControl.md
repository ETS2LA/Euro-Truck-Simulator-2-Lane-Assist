---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
date: 2024-2-18
icon: stack
tags: 
  - plugin
  - lane detection
---
# CruiseControl

### Description
CruiseControl is a plugin that keeps your truck going at the speed limit using in-game ACC. Because it uses the in-game ACC, it can accelerate, brake and stop for other vehicles and obstacles.

### Usage
Enable the CruiseControl plugin and configure the setttings shown below.

### Configuration / UI
+++ General
==- Automatically enable cruise control when available
Enabling this feature will automatically enable cruise control when lane assist is enabled and available.
==-

==- Stop the truck when a red traffic light is detected
!!!warning Important
This feature will only work if TrafficlightDetection is enabled and set up. See the TrafficlightDetection plugin documentation for more information.
!!!

Enabling this feature will stop the truck when a red traffic light is detected.
==-

==- Automatically accelerate when the traffic light turns green
!!!warning Important
This feature will only work if TrafficlightDetection is enabled and set up. See the TrafficlightDetection plugin documentation for more information.
!!!

Enabling this feature will automatically accelerate when a red traffic light turns green.
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

If no lane is detected, the truck will automatically come to stop and enable hazard flashers. this will prevent the truck from crashing into other vehicles. or onjects.
==-

==- Shows cruise control symbol in the Lane Assist window. (Showimage Plugin)

Enabling this feature will show the cruise control symbol in the Lane Assist window. It will look like this:
![Cruise Control Symbol](/assets/CruiseControl/cruisecontrol_on_set.png)
==-

==- Acceleration strength in percent (%)
Strength of acceleration from 0 to 100. Choose wiith the slider or text box.
==-

==- Brake strength in percent (%)
Strength of braking from 0 to 100. Choose wiith the slider or text box.
==-
+++

### Requirements
=== TruckSimApi
allows CruiseControl to get data from the game, including speed, and speed limit.
=== SDKController
allows CruiseControl to send input to the game, including acceleration and brake.
===