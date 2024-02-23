---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
date: 2024-2-18
icon: checklist
tags: 
  - plugin
---
# LSTR Lane Detection
!!! danger Note:
This is a depreciated version of lane detection. You should use Navigation Detection instead. This is a legacy lane detection model that was used before Navigation Detection.
!!!

### Description
A depreciated lane detection model that searches for lane lines on the screen. This model can be low on CPU usage. This is because it searchs in patches of pixels instead of each indiviual pixel. This lowers accuracy though. If you have a GPU an alternative to this is UFLD, although Navigation Detection is reccomended as it is the best lane detection model.

### Usage
Run through First Time Setup and select LSTR as your detection method.

### Configuration / UI
=== Load Model
Allows you to select a custom model for LSTR to run on. This can mess with performance and accuracy.
===


### Installation
This plugin will install the following python packages:
=== numpy
Used for image proccessing. In this case, we create the lane lines to display.
=== onnx
Loads the LSTR model.
=== onnxruntime
Allows for use of the LSTR model.
=== opencv-python (cv2)
Used to display lane lines and symbols.
===

### Requirements
=== DefaultSteering
Steers using the detection results.
=== ShowImage
Show the detection results and steering data.
=== BetterCamScreenCapture **OR** MSS ScreenCapture
Provides a image of your screen to search for lanes in.
===