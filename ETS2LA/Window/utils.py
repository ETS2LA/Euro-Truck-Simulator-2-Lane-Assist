"""Provides several useful functions for interacting
with the window, mainly via the win32 APIs.
"""

import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
from ETS2LA.Utils.translator import _

from typing import Literal
import multiprocessing
import colorsys
import logging
import time
import mss
import os

# TODO: Add Linux support.
if os.name == "nt":
    import win32gui
    import win32con
    import winxpgui
    import win32api
    from ctypes import windll, c_int, byref, sizeof


def get_screen_dimensions(monitor: int = 1) -> tuple[int, int, int, int]:
    """Get the specified monitor's dimensions.

    :param int monitor: The monitor index.

    :return tuple[int, int, int, int]: The monitor's dimensions. (left, top, width, height)
    """
    try:
        sct = mss.mss()
        return (
            sct.monitors[monitor]["left"],
            sct.monitors[monitor]["top"],
            sct.monitors[monitor]["width"],
            sct.monitors[monitor]["height"],
        )
    except Exception:
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
window_position = settings.Get(
    "global",
    "window_position",
    (
        get_screen_dimensions()[2] // 2 - 1280 // 2,
        get_screen_dimensions()[3] // 2 - 720 // 2,
    ),
)
"""
The current position of the window. 
Used mainly by other files to do vision checks.
"""


# TODO: Clean this function, it's old code so the if statements are 500 chars long.
def correct_window_position(
    window_x: int, window_y: int, width: int = 1280, height: int = 720
) -> tuple[int, int]:
    """Correct the window position to be inside the screen area of the closest monitor.

    :param int window_x: The window's X position.
    :param int window_y: The window's Y position.
    :param int width: The window's width.
    :param int height: The window's height.

    :return tuple[int, int]: The corrected window position.
    """
    with mss.mss() as sct:
        monitors = sct.monitors

    closest_screen_index = None
    closest_distance = float("inf")
    for i, monitor in enumerate(monitors[1:]):
        center_x = (monitor["left"] + monitor["left"] + monitor["width"]) // 2
        center_y = (monitor["top"] + monitor["top"] + monitor["height"]) // 2
        distance = (
            (center_x - window_x - width // 2) ** 2
            + (center_y - window_y - height // 2) ** 2
        ) ** 0.5
        if distance < closest_distance:
            closest_screen_index = i + 1
            closest_distance = distance

    if closest_screen_index is None:
        return window_x, window_y

    screen_dimensions = get_screen_dimensions(closest_screen_index)
    left, top, screen_width, screen_height = screen_dimensions
    # if the window is outside the screen area, move it inside (in the x direction)
    if left > window_x + width // 2 or window_x + width // 2 > left + screen_width:
        window_x = (
            left + screen_width - width
            if window_x + width // 2 > left + screen_width
            else left
        )

    # if the window is outside the screen area, move it inside (in the y direction)
    if top > window_y or window_y + height // 2 > top + screen_height:
        window_y = (
            top + screen_height - height
            if window_y + height // 2 > top + screen_height
            else top
        )

    return window_x, window_y


def get_theme_color() -> str:
    """Get the current theme color in hexadecimal.

    :return str: The theme color in hexadecimal.
    """
    try:
        theme = settings.Get("global", "theme", "dark")

        with open(f"{variables.PATH}frontend\\src\\pages\\globals.css", "r") as file:
            content = file.read().split("\n")

            for i, line in enumerate(content):
                if i > 0:
                    line = content[i - 1].replace(" ", "")
                    if line.startswith(
                        ":root{" if theme == "light" else ".dark{"
                    ) and line.startswith("--background"):
                        line = str(line.split(":")[1]).replace(";", "")

                        for i, char in enumerate(line):
                            if char == " ":
                                line = line[i + 1 :]
                            else:
                                break

                        line = line.split(" ")
                        line = [
                            round(float(line[0])),
                            round(float(line[1][:-1])),
                            round(float(line[2][:-1])),
                        ]

                        rgb_color = colorsys.hls_to_rgb(
                            int(line[0]) / 360, int(line[2]) / 100, int(line[1]) / 100
                        )
                        hex_color = "#%02x%02x%02x" % (
                            round(rgb_color[0] * 255),
                            round(rgb_color[1] * 255),
                            round(rgb_color[2] * 255),
                        )

                        return hex_color
    except Exception:
        try:
            return (
                "#ffffff"
                if settings.Get("global", "theme", "dark") == "light"
                else "#18181b"
            )
        except Exception:
            return "#18181b"

    return "#18181b"


def set_window_icon(image_path: str) -> None:
    """Set the ETS2LA window icon to a specified (.ico) image.

    :param str image_path: The path to the image.
    """
    try:
        hwnd = win32gui.FindWindow(None, variables.APPTITLE)
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(
            None, image_path, win32con.IMAGE_ICON, 0, 0, icon_flags
        )  # type: ignore

        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)  # type: ignore
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)  # type: ignore
    except Exception:
        pass


def color_title_bar(theme: Literal["dark", "light"] = "dark"):
    """Color the title bar based on the theme

    :param str theme: The theme to color the title bar with.
    """
    global dont_check_window_open

    sinceStart = time.perf_counter()

    colors = {"dark": 0x1B1818, "light": 0xFFFFFF}

    hwnd = 0
    timeout = settings.Get("global", "window_timeout", 10)
    while hwnd == 0:
        time.sleep(0.01)
        hwnd = win32gui.FindWindow(None, variables.APPTITLE)
        if time.perf_counter() - sinceStart > timeout:
            logging.error(
                _(
                    "Couldn't find / start the ETS2LA window. Is your PC powerful enough? Use https://app.ets2la.com if you think you should be able to run it."
                )
            )
            return

    dont_check_window_open = False

    try:
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 35, byref(c_int(colors[theme])), sizeof(c_int)
        )
        set_window_icon(variables.ICONPATH)
    except Exception as e:
        logging.error(_("Failed to set window attributes or icon.") + " " + str(e))


def check_if_window_still_open() -> bool:
    """Check if the window is still open or if it
    has been closed.

    :return bool: The window is open.
    """
    global last_window_position_time
    global window_position
    if dont_check_window_open:
        return True

    if os.name == "nt":
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
    """Check if a window with the specified name is open.

    :param str name: The name of the window.

    :return bool: The window is open.
    """
    if os.name == "nt":
        top_windows = []
        win32gui.EnumWindows(
            lambda hwnd, top_windows: top_windows.append(
                (hwnd, win32gui.GetWindowText(hwnd))
            ),
            top_windows,
        )
        for _hwnd, window_text in top_windows:
            if name in window_text:
                return True

        return False
    else:
        # TODO: Implement for linux
        return True


if os.name == "nt":

    def get_windows_scaling_factor() -> float:
        try:
            scale_factor = windll.shcore.GetScaleFactorForDevice(0)
            return scale_factor / 100.0
        except Exception:
            logging.exception("Failed to get Windows scaling factor")
            return 1.0  # Fallback to no scaling


queue: multiprocessing.JoinableQueue = variables.WINDOW_QUEUE


def set_on_top(state: bool):
    queue.put({"type": "stay_on_top", "state": state})
    queue.join()  # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value


def toggle_fullscreen():
    queue.put({"type": "fullscreen"})
    queue.join()  # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value


def get_on_top():
    queue.put({"type": "stay_on_top", "state": None})
    queue.join()  # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value


def minimize_window():
    queue.put({"type": "minimize"})
    queue.join()  # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value


def resize_window(width: int, height: int):
    # Get system scaling and adjust dimensions
    if os.name == "nt":
        scaling = get_windows_scaling_factor()
        scaled_width = int(width * scaling)
        scaled_height = int(height * scaling)
    else:
        scaled_width = width
        scaled_height = height

    queue.put({"type": "resize", "width": scaled_width, "height": scaled_height})
    queue.join()  # Wait for the queue to be processed
    value = queue.get()
    queue.task_done()
    return value


IS_TRANSPARENT = False


def set_transparency(value: bool):
    global IS_TRANSPARENT
    if os.name == "nt":
        if value:
            HWND = win32gui.FindWindow(None, variables.APPTITLE)
            win32gui.SetWindowLong(
                HWND,
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(HWND, win32con.GWL_EXSTYLE)
                | win32con.WS_EX_LAYERED,
            )

            transparency = settings.Get("global", "transparency_alpha", 0.8)
            if transparency is None:
                transparency = 0.8

            transparency = int(transparency * 255)
            winxpgui.SetLayeredWindowAttributes(
                HWND, win32api.RGB(0, 0, 0), transparency, win32con.LWA_ALPHA
            )
        else:
            HWND = win32gui.FindWindow(None, variables.APPTITLE)
            win32gui.SetWindowLong(
                HWND,
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(HWND, win32con.GWL_EXSTYLE)
                & ~win32con.WS_EX_LAYERED,
            )

        IS_TRANSPARENT = value
        settings.Set("global", "transparency", value)
    else:
        logging.warning(f"Transparency is not supported on this platform. ({os.name})")
    return IS_TRANSPARENT


def get_transparency():
    return IS_TRANSPARENT


def set_resizable(value: bool):
    if os.name == "nt":
        HWND = win32gui.FindWindow(None, variables.APPTITLE)
        style = win32gui.GetWindowLong(HWND, win32con.GWL_STYLE)

        color_title_bar()

        if value:
            new_style = style | win32con.WS_THICKFRAME
        else:
            # Reset the window style to the default
            new_style = style & ~win32con.WS_THICKFRAME

        win32gui.SetWindowLong(HWND, win32con.GWL_STYLE, new_style)
        # Force window to redraw
        win32gui.SetWindowPos(
            HWND,
            None,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOZORDER
            | win32con.SWP_FRAMECHANGED,
        )
    else:
        logging.warning(
            f"Window style modification not supported on this platform. ({os.name})"
        )
