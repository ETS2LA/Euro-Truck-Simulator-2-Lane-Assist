import ETS2LA.variables as variables
import cv2

if variables.OS == "nt":
    from ctypes import windll, byref, sizeof, c_int
    import win32con, win32gui

WINDOWS = {}


def Initialize(Name="", TitleBarColor=(0, 0, 0), Normal=True, TopMost=True, Position=(None, None), Size=(None, None)):
    WINDOWS[Name] = {"TitleBarColor": TitleBarColor, "Normal": Normal, "TopMost": TopMost, "Position": Position, "Size": Size}


def CreateWindow(Name=""):
    if Name == "":
        return

    if WINDOWS[Name]["Normal"]:
        cv2.namedWindow(Name, cv2.WINDOW_NORMAL)

    if WINDOWS[Name]["TopMost"]:
        cv2.setWindowProperty(Name, cv2.WND_PROP_TOPMOST, 1)

    if WINDOWS[Name]["Position"][0] != None and WINDOWS[Name]["Position"][1] != None:
        cv2.moveWindow(Name, WINDOWS[Name]["Position"][0], WINDOWS[Name]["Position"][1])

    if WINDOWS[Name]["Size"][0] != None and WINDOWS[Name]["Size"][1] != None:
        cv2.resizeWindow(Name, WINDOWS[Name]["Size"][0], WINDOWS[Name]["Size"][1])

    if variables.OS == "nt":
        HWND = win32gui.FindWindow(None, Name)
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((WINDOWS[Name]["TitleBarColor"][0] << 16) | (WINDOWS[Name]["TitleBarColor"][1] << 8) | WINDOWS[Name]["TitleBarColor"][2])), sizeof(c_int))
        try:
            hicon = win32gui.LoadImage(None, f"{variables.PATH}Interface/assets/favicon.ico", win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
        except:
            pass


def Show(Name="", Frame=None):
    try:
        cv2.getWindowImageRect(Name)
    except:
        CreateWindow(Name)
    cv2.imshow(Name, Frame)
    cv2.waitKey(1)