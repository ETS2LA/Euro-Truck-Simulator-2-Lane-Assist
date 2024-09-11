try:
    from ETS2LA.utils.translator import Translate
except:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from ETS2LA.utils.translator import Translate
    
import ETS2LA.networking.cloud as cloud
from multiprocessing import Queue
from rich.console import Console
import multiprocessing
import traceback
import importlib
import queue
import sys
import os


LOG_FILE_FOLDER = "logs"    
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
DARK_GRAY = "\033[90m"
NORMAL = "\033[0m"

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
console = Console()

def CloseNode():
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
    print("\n" + Translate("main.errors_and_warnings"))
    if not os.path.exists(LOG_FILE_FOLDER):
        os.makedirs(LOG_FILE_FOLDER)
    
    count = 0
    for file in os.listdir(LOG_FILE_FOLDER):
        if file.endswith(".log"):
            with open(os.path.join(LOG_FILE_FOLDER, file), "r", encoding="utf-8") as f:
                content = f.read()
                errors = content.count("ERR")
                warnings = content.count("WRN")
                if errors != 0 or warnings != 0:
                    count += 1
                    print()
                    print(f"{DARK_GRAY}┌─── {file}{NORMAL}")
                if errors != 0:
                    print(f"{DARK_GRAY}│{RED} {Translate('main.errors')} {errors} {NORMAL}")
                if warnings != 0:
                    print(f"{DARK_GRAY}│{YELLOW} {Translate('main.warnings')} {warnings} {NORMAL}")
                if errors != 0 or warnings != 0:
                    print(f"{DARK_GRAY}└───{NORMAL}")
                    
    if count == 0:
        print(f"{GREEN}{Translate('main.no_errors_or_warnings')}{NORMAL}")

def ETS2LAProcess(exception_queue: Queue):
    try:
        CloseNode()
        ClearLogFiles()
        ETS2LA = importlib.import_module("ETS2LA.core")
        ETS2LA.run()
    except Exception as e:
        exception_queue.put(e)

if __name__ == "__main__":
    exception_queue = Queue()  # Create a queue for exceptions
    print(f"{BLUE}{Translate('main.overseer_started')}{NORMAL}\n")
    if "--dev" in sys.argv:
        import ETS2LA.variables
        ETS2LA.variables.DEVELOPMENT_MODE = True
        print(f"{PURPLE}{Translate('main.development_mode')}{NORMAL}\n")
    # Make sure NodeJS isn't already running and clear logs
    while True:
        process = multiprocessing.Process(target=ETS2LAProcess, args=(exception_queue,))
        process.start()
        process.join()
        
        try:
            # Check if there is an exception in the queue
            e = exception_queue.get_nowait()
            # Handle the exception from the child process here
            if e.args[0] == "exit":
                CloseNode()
                CountErrorsAndWarnings()
                sys.exit(0)

            if e.args[0] == "restart":
                CloseNode()
                CountErrorsAndWarnings()
                ClearLogFiles()
                print(YELLOW + Translate("main.restarting") + NORMAL)
                continue
            
            if e.args[0] == "Update":
                print(YELLOW + Translate("main.updating") + NORMAL)
                if os.name == "nt":
                    try:
                        os.system("update.bat")
                    except: # Used Installer
                        os.system("cd code && cd app && update.bat")
                else:
                    os.system("sh update.sh")
                
                CountErrorsAndWarnings()
                print("\n" + GREEN + Translate("main.update_done") + NORMAL + "\n")
                CloseNode()
                continue
            
            print(Translate("main.crashed"))
            try:
                console.print_exception()
            except:
                error = traceback.format_exception(type(e), e, e.__traceback__)
                traceback.print_exception(type(e), e, e.__traceback__)
                print(Translate("main.legacy_traceback"))
            try:
                cloud.SendCrashReport("ETS2LA 2.0 - Main", str(error))
            except: pass
            print(Translate("main.send_report"))
            CloseNode()
            CountErrorsAndWarnings()
            print(RED + Translate("main.closed") + NORMAL)
            input(Translate("main.press_enter"))
            sys.exit(0)
        
        except queue.Empty:
            # No exception was found in the queue
            pass