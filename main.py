try:
    from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
except:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
    
from ETS2LA.Utils.Console.logs import CountErrorsAndWarnings, ClearLogFiles
from ETS2LA.Utils.packages import CheckForMaliciousPackages, FixModule
from ETS2LA.Utils.submodules import EnsureSubmoduleExists
from ETS2LA.Utils.shell import ExecuteCommand
from Modules.SDKController.main import SCSController
from ETS2LA.Utils.Console.colors import *
import ETS2LA.Networking.cloud as cloud
import ETS2LA.variables as variables
from multiprocessing import Queue
from rich.console import Console
import multiprocessing
import traceback
import importlib
import requests
import queue
import time
import git
import sys
import os

LOG_FILE_FOLDER = "logs"    
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
console = Console()
controller = SCSController()

FixModule("norfair", "2.2.1", "git+https://github.com/Tumppi066/norfair.git")
FixModule("filterpy", "1.4.5", "git+https://github.com/rodjjo/filterpy.git")

def CloseNode():
    if os.name == "nt":
        ExecuteCommand("taskkill /F /IM node.exe > nul 2>&1")
    else:
        ExecuteCommand("pkill -f node > /dev/null 2>&1")

def Reset(clear_logs=True):
    CloseNode()
    CountErrorsAndWarnings()
    controller.reset()
    if clear_logs:
        ClearLogFiles()
        
def get_commit_url(repo, commit_hash):
    try:
        # Get the remote URL
        remote_url = repo.remotes.origin.url
        
        # Remove .git extension if present
        remote_url = remote_url.replace('.git', '')
        
        return remote_url + "/commit/" + commit_hash
    except:
        return ""
        
def get_current_version_information_dictionary():
    try:
        repo = git.Repo()
        current_hash = repo.head.object.hexsha
        current_branch = repo.active_branch.name
        return {
            "name": current_branch,
            "link": get_commit_url(repo, current_hash),
            "time": time.ctime(repo.head.object.committed_date)
        }
    except:
        return {
            "name": "Unknown",
            "link": "Unknown",
            "time": "Unknown"
        }

def ETS2LAProcess(exception_queue: Queue):
    try:
        if "--dev" in sys.argv:
            import ETS2LA.variables
            ETS2LA.variables.DEVELOPMENT_MODE = True
            print(f"{PURPLE}{Translate('main.development_mode')}{END}\n")
        
        if "--local" in sys.argv:
            import ETS2LA.variables
            did_update = EnsureSubmoduleExists("Interface", "https://github.com/ETS2LA/frontend.git", download_updates=True)
            if did_update:
                print(f"{GREEN} -- Running post download action for submodule: {YELLOW} Interface {GREEN} -- {END}")
                UpdateFrontendTranslations()
                ExecuteCommand("cd Interface && npm install && npm run build-local")
            ETS2LA.variables.LOCAL_MODE = True
            print(f"{PURPLE}{'Running UI locally'}{END}\n")
        else:
            try:
                requests.get("https://app.ets2la.com", timeout=1)
            except:
                print(f"{RED}{'No connection to remote UI (github). Running locally.'}{END}\n")
                import ETS2LA.variables
                did_update = EnsureSubmoduleExists("Interface", "https://github.com/ETS2LA/frontend.git", download_updates=True)
                if did_update:
                    print(f"{GREEN} -- Running post download action for submodule: {YELLOW} Interface {GREEN} -- {END}")
                    UpdateFrontendTranslations()
                    ExecuteCommand("cd Interface && npm install && npm run build-local")
                ETS2LA.variables.LOCAL_MODE = True
        
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
    print(f"{BLUE}{Translate('main.overseer_started')}{END}\n")
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
                Reset(clear_logs=False)
                sys.exit(0)

            if e.args[0] == "restart":
                Reset()
                print(YELLOW + Translate("main.restarting") + END)
                continue
            
            if e.args[0] == "Update":
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if variables.DEVELOPMENT_MODE == False:
                    print(YELLOW + Translate("main.updating") + END)
                    if os.name == "nt":
                        try:
                            ExecuteCommand("update.bat")
                        except: # Used Installer
                            try:
                                ExecuteCommand("cd code && cd app && update.bat")
                            except: 
                                # Backup for old installers
                                ExecuteCommand("cd .. && cd .. && cd code && cd app && update.bat")
                    else:
                        ExecuteCommand("sh update.sh")
                
                Reset()
                print("\n" + GREEN + Translate("main.update_done") + END + "\n")
                continue
            
            print(Translate("main.crashed"))
            
            try:
                console.print_exception()
            except:
                print(trace)
                print(Translate("main.legacy_traceback"))
            
            try: cloud.SendCrashReport("ETS2LA 2.0 - Main", trace, additional=get_current_version_information_dictionary())
            except: pass
            
            print(Translate("main.send_report"))
            Reset()
            print(RED + Translate("main.closed") + END)
            input(Translate("main.press_enter"))
            sys.exit(0)
        
        except queue.Empty:
            # No exception was found in the queue
            pass