"""

Logger, will replace the default "print" command with a custom one that will also log to a file.

Usage:
```
from src.logger import print
print("Something just happened!")
```
"""

import time
import sys, inspect
import os
import traceback
import colorama

printDebug = False
"""Whether to print debug information or not."""

GREEN = "\033[92m"
YELLOW = "\033[93m"
NORMAL = "\033[0m"
BLUE = "\033[94m"
RED = "\033[91m"

start = time.time()
lastMsg = ""
times = 0

# Clear the log file
try:
    with open("log.txt", "w") as f:
        f.truncate(0)
        f.write("")
except:
    sys.stdout.write(f"[{RED}ERROR{NORMAL}] [{YELLOW}logger.py{NORMAL}] - Failed to clear log file!")

# Initialize colors for the terminal
colorama.init()

startTime = time.time()

def print(text:str, end:str=""):
    """Standard print function that will add the time and the caller to the message and log it to a file.

    Args:
        text (str): Text to print and log.
        end (str, optional): Defaults to "".

    Raises:
        Exception: The log file is too big (>10mb).
    """
    global lastMsg
    global times
    
    timestr = str(round(time.time() - startTime, 3))
    while len(timestr.split(".")[1]) < 3:
        timestr += "0"
    date = BLUE + timestr + NORMAL
    
    if sys.platform == "win32":
        caller = inspect.stack()[1].filename
        if "plugins" in caller or "src" in caller:
            caller = GREEN + caller.split("\\")[-2] + YELLOW + "\\" + caller.split("\\")[-1] + NORMAL
        else:
            caller = YELLOW + caller.split("\\")[-1] + NORMAL  
    else:
        caller = inspect.stack()[1].filename
        if "plugins" in caller or "src" in caller:
            caller = GREEN + caller.split("/")[-2] + YELLOW + "/" + caller.split("/")[-1] + NORMAL
        else:
            caller = YELLOW + caller.split("/")[-1] + NORMAL  
    
    
    message = f"[{caller}]\t- {text}\n"
    

    if message == lastMsg:
        times += 1
        sys.stdout.write(f"[{date}] [-> {times}]\r")
        return
    else:
        if times > 0:
            with open("log.txt", "a") as f:
                f.write("[-> {}]".format(times))
        times = 0
        lastMsg = message
        message = f"[{date}] " + message 
    
    # Make sure the file is not too big
    try:
        size = os.path.getsize("log.txt")
        # 10MB
        if size > 10000000:
            sys.stdout.write(message + RED + "[ERROR] The log file is too big! (10mb) Saving paused! Please rerun the app!\n")
            raise Exception("Usually you have a problem if the log file is this big!")
        
        try:
            with open("log.txt", "a") as f:
                fileMessage = message
                # Remove the color tags from the message so that the file is easier to read
                fileMessage = fileMessage.replace(GREEN, "").replace(YELLOW, "").replace(NORMAL, "").replace(BLUE, "").replace(RED, "")
                f.write(fileMessage)
        except:
            pass
    except:
        try:
            # Check if the file exists
            if not os.path.exists("log.txt"):
                with open("log.txt", "w") as f:
                    f.write("")
        except:
            pass
    
    # Can't use print() because it will cause an infinite loop
    sys.stdout.write(message + end)
    if printDebug:
        traceback.print_exc()
    
    
if settings.GetSettings("Dev", "print_ui_events", False) == True:
    print("Logger initialized!")
        