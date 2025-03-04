# type: ignore
# TODO: Make this file type-safe.
#       Currently it's not due to the windows-specific code. 
import ETS2LA.variables as variables

if variables.OS == "nt":
    import win32gui, win32con, win32console
    import ctypes

def RestoreConsole():
    """This will restore the console window."""
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_RESTORE)
            else:
                try:
                    variables.CONSOLENAME = win32console.GetConsoleTitle()
                    variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                    win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_RESTORE)
                except Exception as e:
                    variables.CONSOLENAME = None
                    variables.CONSOLEHWND = None
                    print("\033[91m" + "Failed to restore console: " + "\033[0m" + str(e))
        else:
            print("\033[91m" + "Failed to restore console: " + "\033[0m" + "Unsupported OS")
    except Exception as e:
        print("There was an error restoring the console window: " + str(e))

def HideConsole():
    """This will hide the console window."""
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_HIDE)
            else:
                try:
                    variables.CONSOLENAME = win32console.GetConsoleTitle()
                    variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                    win32gui.ShowWindow(variables.CONSOLEHWND, win32con.SW_HIDE)
                except Exception as e:
                    variables.CONSOLENAME = None
                    variables.CONSOLEHWND = None
                    print("\033[91m" + "Failed to hide console: " + "\033[0m" + str(e))
        else:
            print("\033[91m" + "Failed to hide console: " + "\033[0m" + "Unsupported OS")
    except Exception as e:
        print("There was an error hiding the console window: " + str(e))
        RestoreConsole()

def CloseConsole():
    """This will close the console and stop the app."""
    try:
        if variables.OS == "nt":
            if variables.CONSOLEHWND != None and variables.CONSOLENAME != None:
                ctypes.windll.user32.PostMessageW(variables.CONSOLEHWND, 0x10, 0, 0)
            else:
                try:
                    variables.CONSOLENAME = win32console.GetConsoleTitle()
                    variables.CONSOLEHWND = win32gui.FindWindow(None, str(variables.CONSOLENAME))
                    ctypes.windll.user32.PostMessageW(variables.CONSOLEHWND, 0x10, 0, 0)
                except Exception as e:
                    variables.CONSOLENAME = None
                    variables.CONSOLEHWND = None
                    print("\033[91m" + "Failed to close console: " + "\033[0m" + str(e))
        else:
            print("\033[91m" + "Failed to close console: " + "\033[0m" + "Unsupported OS")
    except Exception as e:
        print("There was an error closing the console window: " + str(e))
        RestoreConsole()