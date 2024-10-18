from ETS2LA.Module import *

class Module(ETS2LAModule):
    def imports(self):
        global np, cv2, PluginRunner, variables, settings, logging
        import numpy as np
        import cv2
        import ETS2LA.variables as variables
        import ETS2LA.backend.settings as settings
        from ETS2LA.plugins.runner import PluginRunner
        import logging

    def init(self):
        self.overlays = {}
        """Dictionary of overlays... (name: np.ndarray)"""
        global LAST_WIDTH, LAST_HEIGHT
        LAST_WIDTH = 1280
        LAST_HEIGHT = 720

    def LoadSettings(self):
        data = settings.GetJSON(self.plugin.path)
        try:
            data = data["ShowImage"]
        except:
            pass # Load defaults...
        pass # Load settings...
        

    def InitializeWindow(windowName, img):
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST, 1)
        # Get the width and height
        width, height = LAST_WIDTH, LAST_HEIGHT
        cv2.resizeWindow(windowName, width, height)

        if variables.OS == "nt":
            import win32gui, win32con
            from ctypes import windll, byref, sizeof, c_int
            hwnd = win32gui.FindWindow(None, windowName)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x000000)), sizeof(c_int))
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(None, f"{variables.PATH}frontend/src/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, icon_flags)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)

    def DestroyWindow(windowName):
        try:
            cv2.destroyWindow(windowName)
        except:
            pass

    def Initialize():
        pass # Do nothing

    def run(self, img: np.ndarray = None, windowName:str = "Lane Assist"):
        global LAST_WIDTH, LAST_HEIGHT
        try:
            if type(img) != np.ndarray:
                return

            LAST_WIDTH, LAST_HEIGHT = img.shape[1], img.shape[0]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Add overlays
            for overlay in self.overlays:
                try:
                    img = cv2.addWeighted(img, 1, self.overlays[overlay], 1, 0)
                except:
                    logging.debug("Failed to add overlay: " + overlay)
                
            try:
                cv2.getWindowImageRect(windowName)
            except:
                self.InitializeWindow(windowName, img)
                
            cv2.imshow(windowName, img)
            cv2.waitKey(1)
        except:
            import traceback
            logging.exception(traceback.format_exc())
            pass
