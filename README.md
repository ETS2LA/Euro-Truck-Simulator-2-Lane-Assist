# Euro-Truck-Simulator-2-Lane-Assist
Lane assist for ETS2, built with the ultra-fast-lane-detection model.

This project was made possible by the amazing people behind the original [Ultra Fast Lane Detection](https://github.com/cfzd/Ultra-Fast-Lane-Detection) paper.
In addition to ibaiGorordo for his [example scripts for Pytorch](https://github.com/ibaiGorordo/Ultrafast-Lane-Detection-Inference-Pytorch-) and rdbender for his  [sun valley theme for ttk](https://github.com/rdbende/Sun-Valley-ttk-theme).

[Example Video](https://youtu.be/oHBFTHrOqCU)


It is important to note that in the video I overlayed the laneAssist window on top of ETS2, unfortunately I do not yet know how to get it on top without messing with the screen capture.

# Installation
Copy the repository ( Code -> Download zip ) and unpack it to a folder. Now install all the requirements.

# Requirements
You must have at least python 3.7 installed for pytorch to work.
To install pytorch go to [their](https://pytorch.org/get-started/locally/) website and select the appropriate options.
If you have an nvidia graphics card then select cuda, otherwise go for cpu. If you download cuda then you also have to download the [cuda api](https://developer.nvidia.com/cuda-downloads) from NVIDIA.


Other requirements can be installed with pip like this (if you have > python 3.10, then use pip3.10):
> pip3 install -r requirements.txt

# Lane Detection models
In addition to the normal requirements this application requires a lane detection model to work.
To download a pretrained model go to the [Ultra Fast Lane Detection](https://github.com/cfzd/Ultra-Fast-Lane-Detection) github page and scroll down until you see Trained models.

There are two different models to choose from. CUlane is a more stable model, but might not work in more difficult situations (like the road being white). On the other hand Tusimple is a more sporadic model that will almost certainly work in any situation. It is also worth noting that Tusimple in some cases requires some of the top of the dashboard and steering wheel to show, while CUlane doesn't. There is a tradeoff to both but I have included a way to switch between them while running the app, so downloading both of them is no issue.
After you have downloaded a model, make a models folder in the root folder of the app (the folder where MainFile.py is) and move the model there.

# Preparations
Before even starting the app make sure your ETS2 or any other game is in borderless mode. It is not required for the app to work, but for setting it up it is highly recommended. To start the app, open a command prompt or terminal in the app's folder ( on windows this can be done by holding alt and right clicking ). Once the terminal is open type:
> python3 MainFile.py

This will start the application and you should see two windows. One is the main window where you can start the program and change the settings. The other is the preview to show you what the program sees. Don't worry if it's black, that doesn't mean that it isn't working.

Before pressing Toggle Enable it is important to head over to the settings to configure a couple of important options.

The first is to change the position of the video capture from the general tab. I recommend starting up ETS 2 and setting the game on pause. Then move the window around by changing the position values (I recommend setting them to 0x0 and then going from there) so that the app sees the road, but preferably not the steering wheel as this can throw off the lane detection. Even though it's not recommended you might also need to change the dimensions of the screen capture. This might have to be done on 1080 or 4k monitors for example. Just if you do try to keep the aspect ratio the same (16:9)

The second important option is your input device. Even if you play on a keyboard you must have a controller selected. The default selection is for my G29. If you also have one then be sure to make sure the controller is correct, after that you can head over to the next step. 

If you do not play on a G29 then select your controller and additionally select the steering axis ( the blue slider will move with the axis ) and the button to toggle the Lane Assist ( this can usually be found by searching on google for *controller* button numbers )

After that go to the final tab, and if you do have a nvidia gpu then you can enable Use GPU, after that you can hit Change Model.

Finally if you want to save your settings, most of them can be easily changed by editing MainFile.py

# Usage
Once all the preparations are done let's actually use the lane assist. When you start the program it will make a virtual xbox 360 controller. You have to set the ingame steering axis to this controller, it will not recognize the controller unless put it as a secondary device. Under the main device (Should be Keyboard + *controller*) there are a multitude of slots, one of these slots must be the 360. This controller follows your own wheel/gamepad so managing to set it in the settings can be hard. Unfortunately this virtual controller means you will lose all force feedback from your main wheel. 

Once the controller is setup in game it's time to use the app. To start the lane assist you can either press the set button on your controller or manually toggle it with Toggle Enable. You should see the lane show up on the preview and after that, Happy Trucking!
