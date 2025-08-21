"""
Provides several useful functions for interacting
with the window, mainly via the win32 APIs.
"""
import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
from ETS2LA.Utils.translator import _

from typing import Literal
import colorsys  
import logging
import time
import mss
import os

# TODO: Add Linux support.
if os.name == 'nt':
    import win32gui
    import win32con
    from ctypes import windll, c_int, byref, sizeof


def get_screen_dimensions(monitor: int = 1) -> tuple[int, int, int, int]:
    """
    Get the specified monitor's dimensions.
    
    :param int monitor: The monitor index.
    
    :return tuple[int, int, int, int]: The monitor's dimensions. (left, top, width, height)
    """
    try:
        sct = mss.mss()
        return sct.monitors[monitor]["left"], sct.monitors[monitor]["top"], \
               sct.monitors[monitor]["width"], sct.monitors[monitor]["height"]
    except:
        return 0, 0, 1280, 720


last_window_position_time = 0
"""
Last timestamp of the window position update.
"""
dont_check_window_open = False
"""
Don't check if the window is open.
This is to prevent the app from being closed when --no-ui is used
or the window has not started for another reason.
"""
window_position = settings.Get("global", "window_position", (
    get_screen_dimensions()[2] // 2 - 1280 // 2, 
    get_screen_dimensions()[3] // 2 - 720 // 2
))
"""
The current position of the window. 
Used mainly by other files to do vision checks.
"""

# TODO: Clean this function, it's old code so the if statements are 500 chars long.
def correct_window_position(window_x: int, window_y: int, width: int = 1280, height: int = 720) -> tuple[int, int]:
    """
    Correct the window position to be inside the screen area of the closest monitor.
    
    :param int window_x: The window's X position.
    :param int window_y: The window's Y position.
    :param int width: The window's width.
    :param int height: The window's height.
    
    :return tuple[int, int]: The corrected window position.
    """
    
    with mss.mss() as sct:
        monitors = sct.monitors
    
    closest_screen_index = None
    closest_distance = float('inf')
    for i, monitor in enumerate(monitors[1:]):
        center_x = (monitor['left'] + monitor['left'] + monitor['width']) // 2
        center_y = (monitor['top'] + monitor['top'] + monitor['height']) // 2
        distance = ((center_x - window_x - width//2) ** 2 + (center_y - window_y - height//2) ** 2) ** 0.5
        if distance < closest_distance:
            closest_screen_index = i + 1
            closest_distance = distance

    if closest_screen_index is None:
        return window_x, window_y
    
    screen_dimensions = get_screen_dimensions(closest_screen_index)
    left, top, screen_width, screen_height = screen_dimensions
    # if the window is outside the screen area, move it inside (in the x direction)
    if left > window_x + width // 2 or window_x + width // 2 > left + screen_width:
        window_x = left + screen_width - width \
                   if window_x + width // 2 > left + screen_width \
                   else left
    
    # if the window is outside the screen area, move it inside (in the y direction)
    if top > window_y or window_y + height // 2 > top + screen_height:
        window_y = top + screen_height - height \
                   if window_y + height // 2 > top + screen_height \
                   else top

    return window_x, window_y


def get_theme_color() -> str:
    """
    Get the current theme color in hexadecimal.
    
    :return str: The theme color in hexadecimal.
    """
    try:
        theme = settings.Get("global", "theme", "dark")
        
        with open(f"{variables.PATH}frontend\\src\\pages\\globals.css", "r") as file:
            content = file.read().split("\n")
            
            for i, line in enumerate(content):
                if i > 0:
                    line = content[i - 1].replace(" ", "")
                    if line.startswith(":root{" if theme == "light" else ".dark{") and line.startswith("--background"):
                        line = str(line.split(":")[1]).replace(";", "")
                        
                        for i, char in enumerate(line):
                            if char == " ":
                                line = line[i+1:]
                            else:
                                break
                            
                        line = line.split(" ")
                        line = [
                            round(float(line[0])), 
                            round(float(line[1][:-1])), 
                            round(float(line[2][:-1]))
                        ]
                        
                        rgb_color = colorsys.hls_to_rgb(
                            int(line[0]) / 360, 
                            int(line[2]) / 100, 
                            int(line[1]) / 100
                        )
                        hex_color = '#%02x%02x%02x' % (
                            round(rgb_color[0] * 255),
                            round(rgb_color[1] * 255),
                            round(rgb_color[2] * 255)
                        )
                        
                        return hex_color
    except:
        try:
            return "#ffffff" if settings.Get("global", "theme", "dark") == "light" else "#18181b"
        except:
            return "#18181b"
        
    return "#18181b"


def set_window_icon(image_path: str) -> None:
    """
    Set the ETS2LA window icon to a specified (.ico) image.
    
    :param str image_path: The path to the image.
    """
    try:
        hwnd = win32gui.FindWindow(None, variables.APPTITLE)
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(None, image_path, win32con.IMAGE_ICON, 0, 0, icon_flags) # type: ignore

        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon) # type: ignore
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)   # type: ignore
    except:
        pass


def color_title_bar(theme: Literal["dark", "light"] = "dark"):
    """
    Color the title bar based on the theme
    
    :param str theme: The theme to color the title bar with.
    """
    
    global dont_check_window_open
    
    sinceStart = time.perf_counter()
    
    colors = {
        "dark": 0x1b1818,
        "light": 0xFFFFFF
    }

    timeout = settings.Get("global", "window_timeout", 10)
    logging.info(_("Looking for ETS2LA window... [dim]({timeout}s timeout)[/dim]").format(timeout=timeout))
    
    hwnd = 0
    while hwnd == 0:
        time.sleep(0.01)
        hwnd = win32gui.FindWindow(None, variables.APPTITLE)
        if time.perf_counter() - sinceStart > timeout:
            logging.error(_("Couldn't find / start the ETS2LA window. Is your PC powerful enough? Use https://app.ets2la.com if you think you should be able to run it."))
            dont_check_window_open = True
            return
    
    try:
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(colors[theme])), sizeof(c_int))
        set_window_icon(variables.ICONPATH)
    except Exception as e:
        logging.error(f"Failed to set window attributes or icon: {e}")


def check_if_window_still_open() -> bool:
    """
    Check if the window is still open or if it
    has been closed.
    
    :return bool: The window is open.
    """
    
    global last_window_position_time
    global window_position
    if dont_check_window_open:
        return True
    
    if os.name == 'nt':
        hwnd = win32gui.FindWindow(None, variables.APPTITLE)
        if hwnd == 0:
            return False
        else:
            if last_window_position_time + 1 < time.perf_counter():
                rect = win32gui.GetClientRect(hwnd)
                tl = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                if (tl[0], tl[1]) != window_position:
                    window_position = (tl[0], tl[1])
                    settings.Set("global", "window_position", window_position)
                last_window_position_time = time.perf_counter()
            return True
    else:
        # TODO: Add Linux support.
        return True
    
    
    
def check_if_specified_window_open(name: str) -> bool:
    """
    Check if a window with the specified name is open.
    
    :param str name: The name of the window.
    
    :return bool: The window is open.
    """
    if os.name == 'nt':
        top_windows = []
        win32gui.EnumWindows(
            lambda hwnd, 
            top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), 
            top_windows
        )
        for hwnd, window_text in top_windows:
            if name in window_text:
                return True
            
        return False
    else:
        # TODO: Implement for linux
        return True
