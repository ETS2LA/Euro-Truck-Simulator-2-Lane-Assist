import src.variables as variables
import win32gui, win32con

def RestoreConsole():
    """This will restore the console window."""
    try:
        win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_RESTORE)
    except:
        print("There was an error restoring the console window.")

def HideConsole():
    """This will hide the console window."""
    try:
        if variables.CONSOLENAME == None:
            window_found = False
            target_text = "/venv/Scripts/python"
            top_windows = []
            win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
            for hwnd, window_text in top_windows:
                if target_text in window_text:
                    window_found = True
                    variables.CONSOLENAME = hwnd
                    break
            if window_found == False:
                print("Console window not found, unable to hide!")
            else:
                print(f"Console Name: {window_text}, Console ID: {hwnd}")
                win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_HIDE)
        else:
            win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_HIDE)
    except:
        print("There was an error hiding the console window.")