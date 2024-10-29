import os
if os.name == 'nt':
    import win32gui

def CheckIfWindowOpen(name):
    top_windows = []
    win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
    for hwnd, window_text in top_windows:
        if name in window_text:
            return True
        
    return False