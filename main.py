"""
This file contains the runner for ETS2LA.
If you are looking for the actual entrypoint then you should
look at the core.py file in the ETS2LA folder.
"""

import os

try:
    from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
except:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
    
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    
from ETS2LA.Utils.Console.logs import CountErrorsAndWarnings, ClearLogFiles
from ETS2LA.Utils.packages import CheckForMaliciousPackages, FixModule
from ETS2LA.Utils.submodules import EnsureSubmoduleExists
from ETS2LA.Utils.shell import ExecuteCommand
from Modules.SDKController.main import SCSController
from ETS2LA.Utils.Console.colors import *
import ETS2LA.Networking.cloud as cloud
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

LOG_FILE_FOLDER = "logs"    
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
console = Console()
controller = SCSController()

def close_node() -> None:
    """
    Close all NodeJS instances.
    """
    
    if os.name == "nt":
        ExecuteCommand("taskkill /F /IM node.exe > nul 2>&1")
    else:
        ExecuteCommand("pkill -f node > /dev/null 2>&1")

def reset(clear_logs=True) -> None:
    """
    Reset ETS2LA. 
    This means closing Node, clearing the logs and resetting the controller SDK.
    """
    close_node()
    CountErrorsAndWarnings()
    controller.reset()
    if clear_logs:
        ClearLogFiles()
        
def get_commit_url(repo: git.Repo, commit_hash: str) -> str:
    """
    Get a remote URL for the current commit hash.
    
    :param git.Repo repo: The git repository object.
    :param str commit_hash: The commit hash.
    
    :return str: The URL to the commit.
    """
    try:
        # Get the remote URL
        remote_url = repo.remotes.origin.url
        
        # Remove .git extension if present
        remote_url = remote_url.replace('.git', '')
        
        return remote_url + "/commit/" + commit_hash
    except:
        return ""
        
def get_current_version_information() -> dict:
    """
    Get the current version information.

    :return dict: The version information.
    ```
    {
        "name": "main",
        "link": "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist/commit/...
        "time": "Sun Mar 14 14:00:00 2021"
    }
    ```
    """
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

def ets2la_process(exception_queue: Queue) -> None:
    """
    The main ETS2LA process.
    - This function will run ETS2LA with the given arguments.
    - It will also handle exceptions and updates to the submodules.
    
    :param Queue exception_queue: The exception queue to send exceptions to.
    """
    try:
        import ETS2LA.variables
        
        if "--dev" in sys.argv:
            print(f"{PURPLE}{Translate('main.development_mode')}{END}\n")
        
        if "--local" in sys.argv:
            did_update = EnsureSubmoduleExists("Interface", "https://github.com/ETS2LA/frontend.git", download_updates=False if "--dev" in sys.argv else True,
                                               cdn_url="http://cdn.ets2la.com/frontend", cdn_path="frontend-main")
            if did_update:
                print(f"{GREEN} -- Running post download action for submodule: {YELLOW} Interface {GREEN} -- {END}")
                UpdateFrontendTranslations()
                ExecuteCommand("cd Interface && npm install && npm run build-local")
                print(f"\n{PURPLE}{'Running UI locally'}{END}\n")
            else:
                print(f"{PURPLE}{'Running UI locally'}{END}\n")
        
        if not "--local" in sys.argv:
            # Download the UI from the CDN in the case that there is no
            # github connection available.  
            try:
                requests.get("https://app.ets2la.com", timeout=1)
            except: 
                print(f"{RED}{'No connection to remote UI (github). Running locally.'}{END}\n")
                did_update = EnsureSubmoduleExists("Interface", "https://github.com/ETS2LA/frontend.git", download_updates=True,
                                                   cdn_url="http://cdn.ets2la.com/frontend", cdn_path="frontend-main")
                if did_update:
                    print(f"{GREEN} -- Running post download action for submodule: {YELLOW} Interface {GREEN} -- {END}")
                    UpdateFrontendTranslations()
                    ExecuteCommand("cd Interface && npm install && npm run build-local")
                ETS2LA.variables.LOCAL_MODE = True
        
        if "--no-console" in sys.argv:
            if "--no-ui" in sys.argv:
                print(f"{RED}{'--no-console cannot be used in combination with --no-ui. The console will not close.'}{END}\n")
            else:
                print(f"{PURPLE}{'Closing console after UI start.'}{END}\n")
            
        if "--no-ui" in sys.argv:
            print(f"{PURPLE}{'Running without UI.'}{END}\n")
        
        close_node()
        ClearLogFiles()
        ETS2LA = importlib.import_module("ETS2LA.core")
        ETS2LA.run()
        
    except Exception as e:
        # Send the traceback out via the exception queue.
        # This is to catch the exit and restart commands.
        if str(e) != "exit" and str(e) != "restart":
            trace = traceback.format_exc()
            exception_queue.put((e, trace))
        else:
            exception_queue.put((e, None))


if __name__ == "__main__":
    exception_queue = Queue()
    
    print(f"{BLUE}{Translate('main.overseer_started')}{END}\n")
    CheckForMaliciousPackages()
    
    while True:
        process = multiprocessing.Process(target=ets2la_process, args=(exception_queue,))
        process.start()
        process.join() # This will block until ETS2LA has closed.
        
        try:
            # Check if there is an exception in the queue
            e, trace = exception_queue.get_nowait()

            # Handle the exception from the child process here
            if e.args[0] == "exit":
                reset(clear_logs=False)
                sys.exit(0)

            if e.args[0] == "restart":
                reset()
                print(YELLOW + Translate("main.restarting") + END)
                continue
            
            if e.args[0] == "Update":
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if not "--dev" in sys.argv:
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
                    
                else:
                    print(YELLOW + "Skipping update due to development mode." + END)
                
                print("\n" + GREEN + Translate("main.update_done") + END + "\n")
                reset()
                continue
            
            # At this point we're sure that this is a crash
            # instead of a normal exit or restart.
            
            print(Translate("main.crashed"))
            
            try:
                console.print_exception()
            except:
                print(trace)
                print(Translate("main.legacy_traceback"))
            
            try: cloud.SendCrashReport("ETS2LA 2.0 - Main", trace, additional=get_current_version_information)
            except: pass
            
            print(Translate("main.send_report"))
            reset()
            print(RED + Translate("main.closed") + END)
            input(Translate("main.press_enter"))
            sys.exit(0)
        
        except queue.Empty:
            # No exception was found in the queue
            pass
        
# IGNORE: This comment is just used to trigger an update and clear 
#         the cache of the app for frontend changes or other changes that
#         don't necessarily have code changes.
# 
# Counter: 7