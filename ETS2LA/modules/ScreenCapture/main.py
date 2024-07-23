from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import ETS2LA.variables as variables
import numpy as np
import cv2
import mss

runner:PluginRunner = None

sct = mss.mss()
display = settings.Get("ScreenCapture", "display", 0)
monitor = sct.monitors[(display + 1)]
monitor_x1 = monitor["left"]
monitor_y1 = monitor["top"]
monitor_x2 = monitor["width"]
monitor_y2 = monitor["height"]
cam = None

def CreateCam(CamSetupDisplay:int = display):
    if variables.OS == "nt":
        global cam
        import bettercam
        try:
            cam.stop() # stop the old instance of cam
        except:
            pass
        try:
            cam.close() # close the old instance of cam
        except:
            pass
        try:
            cam.release() # release the old instance of cam
        except:
            pass
        try:
            del cam
        except:
            pass
        cam = bettercam.create(output_idx=CamSetupDisplay)
        #cam.start()
    else:
        global display
        display = CamSetupDisplay + 1
        
def Initialize():
    CreateCam()

if variables.OS == "nt":
    def run(imgtype:str = "both"):
        """imgtype: "both", "cropped", "full" """
        global cam
        try:
            if cam == None:
                CreateCam()
            #mg = np.array(img)
            # return the requestet image, only crop when needed
            if imgtype == "both":
                img = cam.grab()
                croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                return croppedImg, img
            elif imgtype == "cropped":
                croppedImg = cam.grab(region=(monitor_x1, monitor_y1, monitor_x2, monitor_y2))
                return croppedImg
            elif imgtype == "full":
                img = cam.grab()
                return img
            else:
                img = cam.grab()
                croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                return croppedImg, img
        except:
            import traceback
            runner.logger.exception(traceback.format_exc())
            try:
                return (None, None) if imgtype != "cropped" or imgtype != "full" else None
            except:
                pass
else:
    def run(imgtype:str = "both"):
        """imgtype: "both", "cropped", "full" """
        try:
            # Capture the entire screen
            fullMonitor = sct.monitors[(display + 1)]
            img = np.array(sct.grab(fullMonitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # return the requestet image, only crop when needed
            if imgtype == "both":
                croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                return croppedImg, img
            elif imgtype == "cropped":
                croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                return croppedImg
            elif imgtype == "full":
                return img
            else:
                croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                return croppedImg, img
        except:
            import traceback
            runner.logger.exception(traceback.format_exc())
            try:
                return (None, None) if imgtype != "cropped" or imgtype != "full" else None
            except:
                pass