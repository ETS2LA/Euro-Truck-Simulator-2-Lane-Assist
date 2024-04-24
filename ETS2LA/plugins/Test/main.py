from ETS2LA.plugins.runner import PluginRunner
import time
import screeninfo
import os

runner:PluginRunner = None
lastTime = time.time()

def Initialize():
    global ScreenCapture
    global ShowImage
    ScreenCapture = runner.modules.ScreenCapture
    ShowImage = runner.modules.ShowImage
    # Will run when the plugin is first loaded
    screen = screeninfo.get_monitors()[0]
    if os.name == "nt":
        monitor = (0, 0, screen.width/2, screen.height/2)
        monitor = (int(screen.width/2-monitor[2]/2), int(screen.height/2-monitor[3]/2), int(screen.width/2+monitor[2]/2), int(screen.height/2+monitor[3]/2))
    else:
        monitor = {"top": 0, "left": 0, "width": screen.width/2, "height": screen.height/2}
        monitor = {"top": int(screen.height/2-monitor["height"]/2), "left": int(screen.width/2-monitor["width"]/2), "width": int(screen.width/2), "height": int(screen.height/2)}
    runner.modules.ScreenCapture.monitor = monitor
    print(monitor)

def plugin():
    img, fullImage = ScreenCapture.run()
    ShowImage.run(img)