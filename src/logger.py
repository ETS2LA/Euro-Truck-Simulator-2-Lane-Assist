"""

Logger, will replace the default "print" command with a custom one that will also log to a file.

>>> from src.logger import print
>>> print("Something just happened!")

"""

import time
import sys, inspect
import os

GREEN = "\033[92m"
YELLOW = "\033[93m"
NORMAL = "\033[0m"
BLUE = "\033[94m"
RED = "\033[91m"

start = time.time()
lastMsg = ""
times = 0

# Clear the log file
with open("log.txt", "w") as f:
    f.truncate(0)
    f.write("")

def print(text):
    global lastMsg
    global times
    
    timestr = str(round(time.process_time(), 3))
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
    
    # Handle installing new requirements for plugins
    if "No module named" in message:
        from tkinter import messagebox
        if messagebox.askokcancel("Install?", "Detected missing dependency for a plugin ({}). Do you want to install it?\nRemember that a restart is necessary after installing!".format(message.split("'")[1])):
            os.system("pip install {}".format(message.split("'")[1]))

    if message == lastMsg:
        times += 1
        sys.stdout.write(f"[-> {times}]\r")
        return
    else:
        times = 0
        lastMsg = message
        message = f"[{date}] " + message 
    
    # Make sure the file is not too big
    size = os.path.getsize("log.txt")
    # 10MB
    if size > 10000000:
        sys.stdout.write(message + RED + "[ERROR] The log file is too big! (10mb) Saving paused! Please rerun the app!\n")
        raise Exception("Usually you have a problem if the log file is this big!")
    
    with open("log.txt", "a") as f:
        f.write(message)
    
    # Can't use print() because it will cause an infinite loop
    sys.stdout.write(message)
    
print("Logger initialized!")
        