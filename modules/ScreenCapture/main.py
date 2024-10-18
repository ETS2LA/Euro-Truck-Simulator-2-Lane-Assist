from ETS2LA.Module import *

class Module(ETS2LAModule):
    def imports(self):
        global settings, variables, Literal, np, logging, cv2, mss, os
        import ETS2LA.backend.settings as settings
        import ETS2LA.variables as variables
        from typing import Literal
        import numpy as np
        import logging
        import cv2
        import mss
        import os
        
        if os.name == "nt":
            global WindowsCapture, Frame, InternalCaptureControl
            from windows_capture import WindowsCapture, Frame, InternalCaptureControl

    def init():
        global sct, display, mode, monitor, monitor_x1, monitor_y1, monitor_x2, monitor_y2, cam, cam_process, latest_windows_frame
        sct = mss.mss()
        display = settings.Get("Global", "display", 0)
        mode: Literal["continuous", "grab"] = "grab"
        monitor = sct.monitors[(display + 1)]
        monitor_x1 = monitor["left"]
        monitor_y1 = monitor["top"]
        monitor_x2 = monitor["width"]
        monitor_y2 = monitor["height"]
        cam = None
        cam_process = None
        latest_windows_frame = None

        global LINUX
        #Check if on linux
        LINUX = os.path.exists("/etc/os-release")

    def CreateCam(self, CamSetupDisplay:int = display):
        if variables.OS == "nt":
            global cam
            global cam_process
            global latest_windows_frame
            
            try:
                capture = WindowsCapture(
                    cursor_capture=False,
                    draw_border=False,
                    monitor_index=CamSetupDisplay + 1,
                    window_name=None,
                )
                
                @capture.event
                def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
                    global latest_windows_frame
                    latest_windows_frame = frame.convert_to_bgr().frame_buffer.copy()
                    
                @capture.event
                def on_closed():
                    print("Capture Session Closed")
                
                try:
                    cam_process.stop()
                except:
                    pass
                
                cam_process = capture.start_free_threaded()
                print("Screen Capture using windows_capture")
                logging.debug("Screen Capture using windows_capture")
                return # We are using windows_capture instead of bettercam
            except:
                pass
                
            
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
            if mode == "continuous":
                cam.start()
            print("Screen Capture using bettercam")
            logging.debug("Screen Capture using bettercam")
        else:
            global display
            display = CamSetupDisplay + 1
            print("Screen Capture using mss")
            logging.debug("Screen Capture using mss")

    if variables.OS == "nt": # Windows
        def run(self, imgtype:str = "both"):
            """imgtype: "both", "cropped", "full" """
            global cam
            try:
                if cam == None and cam_process == None:
                    self.CreateCam()
                    
                if cam != None:
                    # return the requestet image, only crop when needed
                    if imgtype == "both":
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                        else:
                            img = cam.grab()
                        croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                        return croppedImg, img
                    elif imgtype == "cropped":
                        if mode == "continuous":
                            img = cam.get_latest_frame()
                            croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                        else:
                            croppedImg = cam.grab(region=(monitor_x1, monitor_y1, monitor_x2, monitor_y2))
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
                        croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                        return croppedImg, img
                    
                elif cam_process != None:
                    if latest_windows_frame is None:
                        return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                    # return the requested image, only crop when needed
                    if imgtype == "both":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                        return croppedImg, img
                    elif imgtype == "cropped":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
                        return croppedImg
                    elif imgtype == "full":
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        return img
                    else:
                        img = latest_windows_frame
                        img = img[:, :, ::-1]
                        croppedImg = img[monitor_y1:monitor_y2, monitor_x1:monitor_x2]
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
                logging.exception(traceback.format_exc())
                try:
                    return (None, None) if imgtype != "cropped" and imgtype != "full" else None
                except:
                    pass