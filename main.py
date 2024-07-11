"""This file serves as the overseer to ETS2LA. It allows the app to restart itself without user input."""

import ETS2LA.networking.cloud as cloud
import traceback
from rich.console import Console
import sys
import os

# Remove the PyGame promopt on startup
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # hide pygame welcome message before importing pygame module in any script

# Variables
LOG_FILE_FOLDER = "logs"    
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
DARK_GRAY = "\033[90m"
NORMAL = "\033[0m"

console = Console()

def CloseNode():
    # Close NodeJS to stop the frontend
    if os.name == "nt":
        os.system("taskkill /F /IM node.exe > nul 2>&1")
    else:
        os.system("pkill -f node > /dev/null 2>&1")
    
def ClearLogFiles():
    if not os.path.exists(LOG_FILE_FOLDER):
        os.makedirs(LOG_FILE_FOLDER)
    for file in os.listdir(LOG_FILE_FOLDER):
        if file.endswith(".log"):
            os.remove(os.path.join(LOG_FILE_FOLDER, file))
            
def CountErrorsAndWarnings():
    print("\nErrors and warnings in the log files:")
    if not os.path.exists(LOG_FILE_FOLDER):
        os.makedirs(LOG_FILE_FOLDER)
    for file in os.listdir(LOG_FILE_FOLDER):
        if file.endswith(".log"):
            with open(os.path.join(LOG_FILE_FOLDER, file), "r") as f:
                content = f.read()
                errors = content.count("ERR")
                warnings = content.count("WRN")
                if errors != 0 or warnings != 0:
                    print()
                    print(f"{DARK_GRAY}┌─── {file}{NORMAL}")
                if errors != 0:
                    print(f"{DARK_GRAY}│{RED} Errors: {errors} {NORMAL}")
                if warnings != 0:
                    print(f"{DARK_GRAY}│{YELLOW} Warnings: {warnings} {NORMAL}")
                if errors != 0 or warnings != 0:
                    print(f"{DARK_GRAY}└───{NORMAL}")

if __name__ == "__main__":
    # Make sure NodeJS isn't already running and clear logs
    CloseNode()
    ClearLogFiles()
    
    # Import ETS2LA.core will import and run the app. Do that repeatedly in case of a crash.
    while True:
        try:
            import ETS2LA.core as ETS2LA
            ETS2LA.run()
        except Exception as e:
            if e.args[0] == "exit":
                CloseNode()
                CountErrorsAndWarnings()
                sys.exit(0)

            if e.args[0] == "restart":
                CloseNode()
                CountErrorsAndWarnings()
                print(RED + "ETS2LA is restarting..." + NORMAL)
                continue
            
            if e.args[0] == "Update":
                CloseNode()
                print(YELLOW + "ETS2LA is updating..." + NORMAL)
                # Run the update.bat / sh script
                if os.name == "nt":
                    os.system("update.bat")
                else:
                    os.system("sh update.sh")
                print(GREEN + "ETS2LA will now restart to update itself..." + NORMAL)
                # Open a new terminal window to run the updated version of ETS2LA
                os.system("start python main.py")
                sys.exit(0)
            
            print(f"ETS2LA has crashed with the following error:")
            error = traceback.format_exc()
            console.print_exception()
            try:
                cloud.SendCrashReport("ETS2LA 2.0 - Main", str(error))
            except: pass
            print("Send the above traceback to the developers.")
            CloseNode()
            CountErrorsAndWarnings()
            print(RED + "ETS2LA has been closed." + NORMAL)
            input("Press enter to exit...")
            sys.exit(0)