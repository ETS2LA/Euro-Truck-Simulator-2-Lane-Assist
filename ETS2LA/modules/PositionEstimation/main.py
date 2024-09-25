from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import ETS2LA.variables as variables
import numpy as np
import logging
import time
import math
import cv2
import os

# Conditional import for window management
if os.name == "nt":
    import win32gui
else:
    from Xlib import X, display
    import Xlib.error
    import Xlib.ext
    import Xlib.XK

from ETS2LA.modules.PositionEstimation.classes import (
    HeadTranslation,
    Position,
    ObjectDetection,
    ObjectTrack,
    ConvertToAngle
)

from ETS2LA.modules.PositionEstimation.api import GetHeadTranslation, GetPosition

runner: PluginRunner = None
objects: list[ObjectTrack] = []
time_to_retain_objects = 1  # second(s)


def DeleteOldObjects() -> None:
    global objects
    current_time = time.time()
    objects = [obj for obj in objects if current_time - obj.last_update_time <= time_to_retain_objects]


def GetIDs() -> list[str]:
    return [obj.id for obj in objects]


def GetObjectById(id: str) -> ObjectTrack:
    for obj in objects:
        if obj.id == id:
            return obj


def Initialize():
    global API
    API = runner.modules.TruckSimAPI


def get(id: str) -> ObjectTrack | None:
    for obj in objects:
        if obj.id == id:
            return obj
    return None


def UpdateGamePosition():
    if os.name == "nt":
        # Windows-specific code
        hwnd = None
        top_windows = []
        win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
        for hwnd, window_text in top_windows:
            if "Truck Simulator" in window_text and "Discord" not in window_text:
                rect = win32gui.GetClientRect(hwnd)
                tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                br = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
                window = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])
                window_x = window[0]
                window_y = window[1]
                window_width = window[2]
                window_height = window[3]
                last_window_position = (current_time, window[0], window[1], window[2], window[3])
                break
    else:
        # Linux-specific code
        d = display.Display()
        root = d.screen().root
        top_windows = root.query_tree().children
        for window in top_windows:
            try:
                window_name = window.get_wm_name()
                if window_name and "Truck Simulator" in window_name and "Discord" not in window_name:
                    geom = window.get_geometry()
                    window_attrs = window.get_attributes()
                    window_x = geom.x
                    window_y = geom.y
                    window_width = geom.width
                    window_height = geom.height
                    last_window_position = (current_time, window_x, window_y, window_width, window_height)
                    break
            except (Xlib.error.XError, AttributeError):
                continue


def run(id: str, detection: tuple | ObjectDetection) -> ObjectTrack | None:
    try:
        if type(id) != str:
            id = str(id)

        data = {}
        data["api"] = API.run()
        UpdateGamePosition()

        head = GetHeadTranslation(data)

        if type(detection) == tuple:
            detection = ObjectDetection(detection[0], detection[1], detection[2], detection[3])

        head.angle = ConvertToAngle(detection.x, detection.y)[0]

        if id not in GetIDs():
            obj = ObjectTrack(id, detection, head)
            objects.append(obj)
        else:
            obj = GetObjectById(id)
            obj.update(detection, head)

        DeleteOldObjects()
        return obj
    except:
        logging.exception("Failed to run position estimation for object " + id)
        return None