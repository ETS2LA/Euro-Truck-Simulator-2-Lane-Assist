try:
    from ETS2LA.utils.translator import Translate 
except:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from ETS2LA.utils.translator import Translate
    
from modules.SDKController.main import SCSController
import ETS2LA.networking.cloud as cloud
from importlib.metadata import version
import ETS2LA.variables as variables
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
controller = SCSController()

malicious_packages = {
    "ultralytics": ["8.3.41", "8.3.42", "8.3.45", "8.3.46"]
}

def CheckForMaliciousPackages():
    for package in malicious_packages.keys():
        try:
            ver = version(package)
            if ver in malicious_packages[package]:
                print(RED + f"Your installed version of the '{package}' package might be malicious! Trying to remove it... (Package Version: {ver})" + NORMAL)
                os.system(f"pip uninstall {package} -y & pip cache purge & pip install {package} --force-reinstall")
                cloud.SendCrashReport(package, f"Successfully updated a malicious package.", f"From version {ver} to the latest version.")
                print(GREEN + f"Successfully updated the '{package}' package to the latest version." + NORMAL)
        except:
            cloud.SendCrashReport(package, "Update malicious package error.", traceback.format_exc())
            print(RED + f"Unable to check the version of the '{package}' package. Please update your '{package}' package manually if you have one of these versions installed: {malicious_packages[package]}" + NORMAL)

# Fix norfair and filterpy
needed_version = "2.2.1"
try:
    if version("norfair") < needed_version:
        os.system("pip install git+https://github.com/Tumppi066/norfair.git")
except:
    os.system("pip install git+https://github.com/Tumppi066/norfair.git")

needed_version = "1.4.5"
try:
    if version("filterpy") < needed_version:
        os.system("pip install git+https://github.com/rodjjo/filterpy.git")
except:
    os.system("pip install git+https://github.com/rodjjo/filterpy.git")


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
        if "--dev" in sys.argv:
            import ETS2LA.variables
            ETS2LA.variables.DEVELOPMENT_MODE = True
            print(f"{PURPLE}{Translate('main.development_mode')}{NORMAL}\n")
        
        CloseNode()
        ClearLogFiles()
        ETS2LA = importlib.import_module("ETS2LA.core")
        ETS2LA.run()
    except Exception as e:
        if str(e) != "exit" and str(e) != "restart":
            trace = traceback.format_exc()
            exception_queue.put((e, trace))
        else:
            exception_queue.put((e, None))

if __name__ == "__main__":
    exception_queue = Queue()  # Create a queue for exceptions
    print(f"{BLUE}{Translate('main.overseer_started')}{NORMAL}\n")
    CheckForMaliciousPackages()
    
    # Make sure NodeJS isn't already running and clear logs
    while True:
        process = multiprocessing.Process(target=ETS2LAProcess, args=(exception_queue,))
        process.start()
        process.join()
        
        try:
            # Check if there is an exception in the queue
            e, trace = exception_queue.get_nowait()

            # Handle the exception from the child process here
            if e.args[0] == "exit":
                CloseNode()
                CountErrorsAndWarnings()
                controller.reset()
                sys.exit(0)

            if e.args[0] == "restart":
                CloseNode()
                CountErrorsAndWarnings()
                ClearLogFiles()
                controller.reset()
                print(YELLOW + Translate("main.restarting") + NORMAL)
                continue
            
            if e.args[0] == "Update":
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if variables.DEVELOPMENT_MODE == False:
                    print(YELLOW + Translate("main.updating") + NORMAL)
                    if os.name == "nt":
                        try:
                            os.system("update.bat")
                        except: # Used Installer
                            try:
                                os.system("cd code && cd app && update.bat")
                            except: 
                                # Backup for old installers
                                os.system("cd .. && cd .. && cd code && cd app && update.bat")
                    else:
                        os.system("sh update.sh")
                
                CountErrorsAndWarnings()
                controller.reset()
                print("\n" + GREEN + Translate("main.update_done") + NORMAL + "\n")
                CloseNode()
                continue
            
            print(Translate("main.crashed"))
            try:
                console.print_exception()
            except:
                print(trace)
                print(Translate("main.legacy_traceback"))
            try:
                cloud.SendCrashReport("ETS2LA 2.0 - Main", trace)
            except: pass
            print(Translate("main.send_report"))
            CloseNode()
            CountErrorsAndWarnings()
            print(RED + Translate("main.closed") + NORMAL)
            controller.reset()
            input(Translate("main.press_enter"))
            sys.exit(0)
        
        except queue.Empty:
            # No exception was found in the queue
            pass