import src.variables as variables
import win32gui, win32con, win32console

def RestoreConsole():
    """This will restore the console window."""
    try:
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
    except:
        print("There was an error restoring the console window.")

def HideConsole():
    """This will hide the console window."""
    try:
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
    except:
        print("There was an error hiding the console window.")