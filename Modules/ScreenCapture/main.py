from ETS2LA.Module import *
import os

import ETS2LA.Utils.settings as settings
display = settings.Get("Global", "display", 0)
if type(display) != int:
    display = 0

class Module(ETS2LAModule):
    has_initialized = False
    
    monitor_x1 = 0
    monitor_y1 = 0
    monitor_x2 = 0
    monitor_y2 = 0
    
    def imports(self):
        global variables, Literal, np, logging, cv2, mss, os
        import ETS2LA.variables as variables
        from typing import Literal
        import numpy as np
        import logging
        import cv2
        import mss
        
        if os.name == "nt":
            global WindowsCapture, Frame, InternalCaptureControl
            from windows_capture import WindowsCapture, Frame, InternalCaptureControl

    def init(self):
        global sct, mode, monitor, cam, cam_process, latest_windows_frame
        sct = mss.mss()
        mode = "grab"
        monitor = sct.monitors[(display + 1)] # type: ignore
        self.monitor_x1 = monitor["left"]
        self.monitor_y1 = monitor["top"]
        self.monitor_x2 = monitor["width"]
        self.monitor_y2 = monitor["height"]
        cam = None
        cam_process = None
        latest_windows_frame = None

        global LINUX
        #Check if on linux
        LINUX = os.path.exists("/etc/os-release")

        self.has_initialized = True

    def CreateCam(self, CamSetupDisplay:int = display):        
        if variables.OS == "nt":
            global cam
            global cam_process
            global latest_windows_frame
            
            try:
                print("Starting windows capture on monitor:", CamSetupDisplay)
                capture = WindowsCapture(
                    cursor_capture=False,
                    draw_border=False,
                    monitor_index=CamSetupDisplay + 1,
                    window_name=None,
                )
                
                @capture.event # type: ignore
                def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
                    global latest_windows_frame
                    latest_windows_frame = frame.convert_to_bgr().frame_buffer.copy()
                    
                @capture.event # type: ignore
                def on_closed():
                    print("Capture Session Closed")
                
                try:
                    cam_process.stop() # type: ignore
                except:
                    pass
                
                cam_process = capture.start_free_threaded()
                print("Screen Capture using windows_capture")
                logging.debug("Screen Capture using windows_capture")
                return # We are using windows_capture instead of bettercam
            except:
                pass
                
            
            import bettercam
            if cam is not None:
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
            if mode == "continuous":
                cam.start()
            print("Screen Capture using bettercam")
            logging.debug("Screen Capture using bettercam")
        else:
            global display
            display = CamSetupDisplay + 1
            print("Screen Capture using mss")
            logging.debug("Screen Capture using mss")

    if os.name == "nt": # Windows
        def run(self, imgtype:str = "both"):
            """imgtype: "both", "cropped", "full" """
            global cam
            if not self.has_initialized:
                return
            try:
                if cam == None and cam_process == None:
                    self.CreateCam()
                    
                if cam != None:
                    # return the requested image, only crop when needed
                    if imgtype == "both":
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                        else:
                            img = cam.grab()
                        
                        if img is None:
                            return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                        
                        croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        return croppedImg, img
                    elif imgtype == "cropped":
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                            croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        else:
                            croppedImg = cam.grab(region=(self.monitor_x1, self.monitor_y1, self.monitor_x2, self.monitor_y2))
                        return croppedImg
                    elif imgtype == "full":
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                        else:
                            img = cam.grab()
                        return img
                    else:
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                        else:
                            img = cam.grab()
                        if img is None:
                            return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                        
                        croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        return croppedImg, img
                    
                elif cam_process != None:
                    if latest_windows_frame is None:
                        return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                    # return the requested image, only crop when needed
                    if imgtype == "both":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        return croppedImg, img
                    elif imgtype == "cropped":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        return croppedImg
                    elif imgtype == "full":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        return img
                    else:
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                        return croppedImg, img
                    
            except:
                import traceback
                logging.exception(traceback.format_exc())
                try:
                    return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                except:
                    pass
    else: # Linux
        def run(imgtype:str = "both"):
            """imgtype: "both", "cropped", "full" """
            try:
                # Capture the entire screen
                if LINUX:
                    fullMonitor = sct.monitors[display]
                else:
                    fullMonitor = sct.monitors[(display) + 1]
                img = np.array(sct.grab(fullMonitor))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # return the requestet image, only crop when needed
                if imgtype == "both":
                    croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                    return croppedImg, img
                elif imgtype == "cropped":
                    croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                    return croppedImg
                elif imgtype == "full":
                    return img
                else:
                    croppedImg = img[self.monitor_y1:self.monitor_y2, self.monitor_x1:self.monitor_x2]
                    return croppedImg, img
            except:
                import traceback
                logging.exception(traceback.format_exc())
                try:
                    return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                except:
                    pass