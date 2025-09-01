import ETS2LA.variables as variables
import cv2

if variables.OS == "nt":
    from ctypes import windll, byref, sizeof, c_int
    import win32con
    import win32gui
else:
    windll = None
    win32con = None
    win32gui = None

WINDOWS = {}


# MARK: Initialize()
def Initialize(
    Name="",
    TitleBarColor=(0, 0, 0),
    Normal=True,
    TopMost=True,
    Position=(None, None),
    Size=(None, None),
):
    """
    Initializes a window. Can handle multiple windows. The window will appear once Show() is called.

    Parameters
    ----------
    Name : str
        The name of the window.
    TitleBarColor : tuple
        The color of the title bar.
    Normal : bool
        Whether the window should be resizable or not.
    TopMost : bool
        Whether the window should be a topmost window or not.
    Position : tuple
        The position of the window.
    Size : tuple
        The size of the window.

    Returns
    -------
    None
    """
    WINDOWS[Name] = {
        "TitleBarColor": TitleBarColor,
        "Normal": Normal,
        "TopMost": TopMost,
        "Position": Position,
        "Size": Size,
    }


# MARK: CreateWindow()
# TODO: Fix type safety. Right now it's not an issue
#       but using type: ignore is not ideal.
def CreateWindow(Name=""):
    """
    Creates the window. Not meant to be called manually!

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    None
    """
    if Name == "":
        return

    if WINDOWS[Name]["Normal"]:
        cv2.namedWindow(Name, cv2.WINDOW_NORMAL)

    if WINDOWS[Name]["TopMost"]:
        cv2.setWindowProperty(Name, cv2.WND_PROP_TOPMOST, 1)

    if (
        WINDOWS[Name]["Position"][0] is not None
        and WINDOWS[Name]["Position"][1] is not None
    ):
        cv2.moveWindow(Name, WINDOWS[Name]["Position"][0], WINDOWS[Name]["Position"][1])

    if WINDOWS[Name]["Size"][0] is not None and WINDOWS[Name]["Size"][1] is not None:
        cv2.resizeWindow(Name, WINDOWS[Name]["Size"][0], WINDOWS[Name]["Size"][1])

    if variables.OS == "nt" and win32gui:
        HWND = win32gui.FindWindow(None, Name)
        windll.dwmapi.DwmSetWindowAttribute(
            HWND,
            35,
            byref(
                c_int(
                    (WINDOWS[Name]["TitleBarColor"][0] << 16)
                    | (WINDOWS[Name]["TitleBarColor"][1] << 8)
                    | WINDOWS[Name]["TitleBarColor"][2]
                )
            ),
            sizeof(c_int),
        )  # type: ignore
        hicon = win32gui.LoadImage(
            None,
            variables.ICONPATH,
            win32con.IMAGE_ICON,
            0,
            0,
            win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE,
        )  # type: ignore
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)  # type: ignore
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, hicon)  # type: ignore


# MARK: Show()
def Show(Name="", Frame=None):
    """
    Shows the frame in the window. The window must have been initialized using Initialize() first.

    Parameters
    ----------
    Name : str
        The name of the window.
    Frame : numpy.ndarray
        The frame to show.

    Returns
    -------
    None
    """
    try:
        cv2.getWindowImageRect(Name)
    except Exception:
        CreateWindow(Name)

    cv2.imshow(Name, Frame)  # type: ignore - Frame doesn't have a type, but importing numpy is not necessary.
    cv2.waitKey(1)
