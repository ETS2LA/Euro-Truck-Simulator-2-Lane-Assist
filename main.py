"""
This file contains the runner for ETS2LA.
If you are looking for the actual entrypoint then you should
look at the core.py file in the ETS2LA folder.
"""

import os
import sys
import subprocess

# This try/except block will either end in a successful import, update, or error
try: from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
except: # Ensure the current PATH contains the install directory.
    sys.path.append(os.path.dirname(__file__))
    try: # It should work here
        from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
    except ModuleNotFoundError: # If modules are missing, this will trigger (generally tqdm)
        print("Import errors in ETS2LA/Utils/translator.py, this is a common sign of missing modules. An update will be triggered to install these modules.")
        subprocess.run("update.bat", shell=True, env=os.environ.copy())
        from ETS2LA.Utils.translator import Translate, UpdateFrontendTranslations
    except Exception as e: # Unkown error
        try: # Try to get the traceback for easier debugging
            import traceback
            print(traceback.format_exc())
        except: # If that fails, just print the exception
            print(str(e))
        input("Press enter to exit...")
        sys.exit()

# Allow pygame to get control events in the background
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
# Hide pygame's support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    
from ETS2LA.Utils.Console.logs import CountErrorsAndWarnings, ClearLogFiles
from ETS2LA.Utils.submodules import EnsureSubmoduleExists
from ETS2LA.Utils.shell import ExecuteCommand
from ETS2LA.Utils.Console.colors import *
import ETS2LA.Networking.cloud as cloud

import multiprocessing
import traceback
import importlib
import requests
import queue
import time
import git

LOG_FILE_FOLDER = "logs"
# TODO: REMEMBER TO UPDATE THE URL BEFORE RELEASE!
FRONTEND_MIRRORS = [
    #"https://app.ets2la.com",
    #"https://app.ets2la.cn",
    "https://beta.ets2la.com"
]

def close_node() -> None:
    if os.name == "nt":
        ExecuteCommand("taskkill /F /IM node.exe > nul 2>&1")
    else:
        ExecuteCommand("pkill -f node > /dev/null 2>&1")

def reset(clear_logs=True) -> None:
    close_node()
    CountErrorsAndWarnings()
    if clear_logs:
        ClearLogFiles()
        
def get_commit_url(repo: git.Repo, commit_hash: str) -> str:
    try:
        remote_url = repo.remotes.origin.url
        remote_url = remote_url.replace('.git', '')
        
        return remote_url + "/commit/" + commit_hash
    except:
        return ""
        
def get_current_version_information() -> dict:
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

def get_fastest_mirror() -> str:
    print(f"Testing mirrors...")
    response_times = {}
    for mirror in FRONTEND_MIRRORS:
        try:
            start = time.perf_counter()
            requests.get(mirror, timeout=5)
            end = time.perf_counter()
            response_times[mirror] = end - start
            print(f"- Reached {YELLOW}{mirror}{END} in {response_times[mirror] * 1000:.0f}ms")
        except requests.RequestException:
            response_times[mirror] = float('inf')
            print(f" - Reached {YELLOW}{mirror}{END} in (TIMEOUT)")
        
    fastest_mirror = min(response_times, key=response_times.get)
    return fastest_mirror

def update_frontend() -> bool:
    did_update = EnsureSubmoduleExists(
        "Interface", 
        "https://github.com/ETS2LA/frontend.git", 
        download_updates=False if "--dev" in sys.argv else True,
        cdn_url="http://cdn.ets2la.com/frontend", 
        cdn_path="frontend-main"
    )
    
    if did_update:
        print(f"{GREEN} -- Running post download action for submodule: {YELLOW} Interface {GREEN} -- {END}")
        # NOTE: REMOVE BRANCH SWITCH BEFORE RELEASE
        ExecuteCommand("cd Interface && git switch page_rewrite")
        UpdateFrontendTranslations()
        ExecuteCommand("cd Interface && npm install && npm run build-local")
    
    return did_update

def ets2la_process(exception_queue: multiprocessing.Queue) -> None:
    """
    The main ETS2LA process.
    - This function will run ETS2LA with the given arguments.
    - It will also handle exceptions and updates to the submodules.
    
    The `exception_queue` is used to send exceptions back to the main process
    for handling (at the bottom of this file).
    """
    try:
        import ETS2LA.variables
        
        if "--dev" in sys.argv:
            print(f"{PURPLE}{Translate('main.development_mode')}{END}\n")
        
        if "--local" in sys.argv:
            update_frontend()
            print(f"{PURPLE}{'Running UI locally'}{END}\n")
        
        elif "--frontend-url" not in sys.argv:
            url = get_fastest_mirror()
            if not url:
                print(f"{RED}{'No connection to remote UI mirrors. Running locally.'}{END}\n")
                update_frontend()
                    
                if not "--local" in sys.argv:
                    sys.argv.append("--local")
                ETS2LA.variables.LOCAL_MODE = True
                
            elif ".cn" in url:
                if not "--china" in sys.argv:
                    sys.argv.append("--china")
                ETS2LA.variables.CHINA_MODE = True
                print(f"{PURPLE}{'Running UI in China mode'}{END}\n")
                
            print(f"\n> Using mirror {YELLOW}{url}{END} for UI.\n")
            sys.argv.append("--frontend-url")
            sys.argv.append(url)
        
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
        # Catch exit and restart seperately
        if str(e) != "exit" and str(e) != "restart":
            trace = traceback.format_exc()
            exception_queue.put((e, trace))
        else:
            exception_queue.put((e, None))


if __name__ == "__main__":
    exception_queue = multiprocessing.Queue()
    print(f"{BLUE}{Translate('main.overseer_started')}{END}\n")
    
    while True:
        process = multiprocessing.Process(target=ets2la_process, args=(exception_queue,))
        process.start()
        process.join() # This will block until ETS2LA has closed.
        
        try:
            e, trace = exception_queue.get_nowait()

            if e.args[0] == "exit":
                reset(clear_logs=False)
                sys.exit(0)

            if e.args[0] == "restart":
                reset()
                print(YELLOW + Translate("main.restarting") + END)
                continue
            
            if e.args[0] == "Update":
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if "--dev" in sys.argv:
                    print(YELLOW + "Skipping update due to development mode." + END)
                    continue
                
                print(YELLOW + Translate("main.updating") + END)
                ExecuteCommand("update.bat")
                
                print("\n" + GREEN + Translate("main.update_done") + END + "\n")
                reset()
                continue
            
            # At this point we're sure that this is a crash
            print(Translate("main.crashed"))
            print(trace)
            
            # Crash reports currently do not work, disabled to save bandwidth
            '''
            try: cloud.SendCrashReport("ETS2LA 2.0 - Main", trace, additional=get_current_version_information)
            except: pass
            '''
            
            print(Translate("main.send_report"))
            reset()
            print(RED + Translate("main.closed") + END)
            input(Translate("main.press_enter"))
            sys.exit(0)
        
        except queue.Empty:
            pass
        
# IGNORE: This comment is just used to trigger an update and clear 
#         the cache of the app for changes that don't necessarily 
#         happen inside of this repository (like the frontend).
# 
# Counter: 18