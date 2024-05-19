# https://stackoverflow.com/a/76060844
import win32gui
import win32con
import ETS2LA.backend.variables as variables
import os

def set_window_icon(image_path):
    hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(None, image_path, win32con.IMAGE_ICON, 0, 0, icon_flags)
    
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
    
def color_title_bar(theme:str):
    if os.name == "nt":
        import win32gui
        from ctypes import windll, c_int, byref, sizeof
        
        colors = {
            "dark": 0x0b0909,
            "light": 0xFFFFFF
        }
        
        hwnd = win32gui.FindWindow(None, f'ETS2LA - Tumppi066 & Contributors © {variables.YEAR}')
        returnCode = windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(colors[theme])), sizeof(c_int))