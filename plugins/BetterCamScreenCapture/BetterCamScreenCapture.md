---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: stack
tags: 
  - plugin
---

[!button Developer Documentation](Docs.md)
### Description
This plugin will capture your display extremely fast with DirectX and provide that data to the rest of the plugins.

### Usage
There is no special usage notes... the plugin should work as is.

### Configuration / UI
The UI includes some settings for the plugin. The settings are as follows:
```
  Width : The width of the image capture
 Height : The height of the image capture
      X : The X coordinate of the image capture
      Y : The Y coordinate of the image capture
Display : The display to capture from
 Device : The device to capture from
```

### Installation
This plugin will install the following python packages:
```
bettercam
```

### Debugging
##### 'The specified device interface or feature level is not supported on this system.'
There are two cases in which this error happens:
1. You have a device that has an integrated GPU (for example on a laptop), and python is running on the dedicated GPU.
2. Your computer is too old to support the directx version dxcam needs.

***Fix for case 1:***

Go into your windows graphics settings, and set python.exe to run on the iGPU. (you might have to search for python.exe if it's not shown in the list)

A common location could be `C:\Users\YourUserName\AppData\Local\Programs\Python\Python311`

***Fix for case 2:***

Disable dxcam and enable mss in the plugin menu. Keep in mind that plugins are designed to run on dxcam, and not everything will work with mss.