![Logo](LaneAssistLogoWide.jpg)
# Lane Assist For ETS2 and ATS
A lane assist, built with the ultra-fast-lane-detection model.

This project was made possible by the amazing people behind the original [Ultra Fast Lane Detection](https://github.com/cfzd/Ultra-Fast-Lane-Detection) paper.
In addition to [ibaiGorordo](https://github.com/ibaiGorordo/Midasv2_1_small-TFLite-Inference/commits?author=ibaiGorordo) for his [example scripts for Pytorch](https://github.com/ibaiGorordo/Ultrafast-Lane-Detection-Inference-Pytorch-) and the [MiDaS tflite implementation](https://github.com/ibaiGorordo/Midasv2_1_small-TFLite-Inference). [rdbende](https://github.com/rdbende) for his  [sun valley theme for ttk](https://github.com/rdbende/Sun-Valley-ttk-theme). Logo was made with [Designevo](https://www.designevo.com/).

[Example Video](https://youtu.be/Ssw2JlbthHw)

[Installation and Usage Video](https://www.youtube.com/watch?v=TNXlCT3Zr6Y)

It is important to note that in the video I overlayed the laneAssist window on top of ETS2, unfortunately I do not yet know how to get it on top without messing with the screen capture.

> For feature requests please go to the [Trello](https://trello.com/b/zkMRzdjN/euro-truck-simulator-2-lane-assist) or add a github issue.

> It is recommended to use the installation video. If that does not work then you can read the written instructions here.

# Features
- Easy to use installer that will take you most of the way there. The installer also handles updates.
- Surprisingly reliable lane detection with multiple available models (they are not made by me).
- Either GPU (Nvidia) or CPU lane detection.
- Lane assist, that automatically disables when indicating (this can be turned off).
- Automatic controller detection for easy controller setup.
- Easy to use UI with plenty of options, this UI also provides a preview of what the lane detection sees.
- In addition to the UI the main files allow even deeper customization without any special editors (notepad is fine).
- Somewhat easy control setup ingame.
- Controls are handled on a separate thread. This means that it doesn't depend on your Lane Detection FPS, and will be smooth all the time.
- Automatic saving and loading of settings in a portable json file.
- High performance screen capture using [DXCam](https://github.com/ra1nty/DXcam) (alternatively mss for Linux/Mac)

### What is not implemented and possible drawbacks
- THIS APP WILL NOT WORK WITH A KEYBOARD. You have to have a controller, [this](https://www.youtube.com/watch?v=_UHNavRGav4) (youtube.com) is a possible alternative. I have not tested it myself.
- The lane detection is trained in the real world, thus it might not detect the lanes properly in some conditions.
- You will loose any sort of rumble or force feedback, due to having to use a virtual controller for steering.
- You will most likely have to fiddle with the settings to get lane detection to be reliable.

# Why are updates sparse
The program is at a point where I can comfortably use it with no issues. This however does not mean that development has stopped, you can check my [Trello](https://trello.com/b/zkMRzdjN/euro-truck-simulator-2-lane-assist) page for the current progress.
> I will update the program to meet the needs of other people and fix any bugs that you might encounter. Just make an issue report, comment on the youtube videos or message me on discord at Tumppi066#2874 for suggestions and bug reports.

# Installation (updated for v0.3 aka the experimental version)
The releases now include a python file to install the program and most of the requirements.
It can be used by selecting the newest release and downloading updater.py and then running
> python updater.py

and by following the instructions.

# Requirements
You must have at least python 3.7 installed for pytorch to work (there are some bugs with 3.11).

If you want to use GPU acceleration then you also have to download the [cuda api](https://developer.nvidia.com/cuda-downloads) from NVIDIA.

# Lane Detection models
> The recommended model is TuSimple34. It can be downloaded [here](https://github.com/cfzd/Ultra-Fast-Lane-Detection/issues/270) (credit to [Adorable Jiang](https://github.com/AdorableJiang))

In addition to the normal requirements this application requires a lane detection model to work.
[This](https://github.com/cfzd/Ultra-Fast-Lane-Detection/issues/270) is a new deeper model from Adorable Jiang. These models will run slower but work better, I have added support for these so it is your choice if you want these or the originals.

To download one of the original models go to the [Ultra Fast Lane Detection](https://github.com/cfzd/Ultra-Fast-Lane-Detection#trained-models), and download either tusimple18 or culane18.

CUlane is a more stable model, but might not work in more difficult situations (like the road being white). 

On the other hand Tusimple is a more sporadic model that will almost certainly work in any situation, but might overcorrect etc... in some places. It is also worth noting that Tusimple in some cases requires some of the top of the dashboard and steering wheel to show, while CUlane doesn't. 

There is a tradeoff to both but I have included a way to switch between them while running the app, so downloading both of them is no issue.
After you have downloaded a model move the model to the models folder.

# Preparations
Before even starting the app make sure your ETS2 or any other game is in borderless mode. It is not required for the app to work, but for setting it up it is highly recommended. Also remember disable automatic indicators in game (if you intend on using the automatic turn off while indicatong). 

To start the app just run the start.bat file (alternatively by running -> python AppUI.py)

I recommend making a new profile so that you always have the defaults available, this can be done by clicking the profile button and then clicking the new profile button. This will clone your current profile and make a new file.
If you do not intend on using your GPU then click the profile button in the top left and load the defaultCPU profile (app folder -> profiles -> defaultCPU).

This will start the application and you should see two windows. One is the main window where you can start the program and change the settings. The other is the preview to show you what the program sees.

Before pressing Enable it is important to head over to the settings to configure a couple of important options.

The first is to change the position of the video capture. I recommend starting up ETS 2 and setting the game on pause. Then move the window around by changing the position values (I recommend setting them to 0x0 and then going from there) so that the app sees the road, but preferably not the steering wheel as this can throw off the lane detection. 
You might also need to change the dimensions of the screen capture. This might have to be done on 1080 or 4k monitors for example (recommended 960x540 for 1080p and 1920x1080 for 4k).

The second important option is your input device. You must have a controller selected otherwise the app will crash. After selecting the controller select the correct axis (there is a slider to show the current position).
You will also have to select the indicator buttons and the toggle button (indicators are optional if you disable automatic turn-off when indicating).

# Usage
Once all the preparations are done let's actually use the lane assist. When you start the program it will make a virtual xbox 360 controller. You have to set the ingame steering axis to this controller, it will not recognize the controller unless put it as a secondary device. 

Under the main device (Keyboard + *virtual xbox controller*) there are a multitude of slots, one of these slots must be the your actual controller. The virtual controller follows your own wheel/gamepad so managing to set it in the settings can be hard and it is recommended to not bind your actual controller before setting the steering axis. Unfortunately this virtual controller means you will lose all force feedback from your main wheel. 

### If the virtual controller is not working then update your ViGeM Bus drivers [here](https://github.com/ViGEm/ViGEmBus/releases/tag/v1.21.442.0).

Once the controller is setup in game it's time to use the app. To start the lane assist you can either press the set button on your controller or manually toggle it with Toggle Enable. You should see the lane show up on the preview and after that, Happy Trucking!

