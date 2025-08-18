"""
This file contains the runner for ETS2LA.
If you are looking for the actual entrypoint then you should
look at the core.py file in the ETS2LA folder.
"""

import os
import sys
import subprocess

if os.name == "nt":
    import ctypes
    try:
        if ctypes.windll.shell32.IsUserAnAdmin()():
            print("ERROR: ETS2LA is running with Administrator privileges.\n"
                "This is not recommended, as it may interfere with system behavior or cause unintended issues.\n"
                "Please restart ETS2LA without Administrator mode.")
            input("Press enter to exit...")
            sys.exit(1)
    except: pass

# This try/except block will either end in a successful import, update, or error
try: from ETS2LA.Utils.translator import _
except: # Ensure the current PATH contains the install directory.
    sys.path.append(os.path.dirname(__file__))
    try:
        from ETS2LA.Utils.translator import _
    except ModuleNotFoundError: # If modules are missing, this will trigger (generally tqdm)
        print("Import errors in ETS2LA/Utils/translator.py, this is a common sign of missing modules. An update will be triggered to install these modules.")
        subprocess.run("update.bat", shell=True, env=os.environ.copy())
        from ETS2LA.Utils.translator import _
    except Exception as e: # Unexpected error, print it and exit
        try:
            import traceback
            print(traceback.format_exc())
        except:
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
import ETS2LA.variables as variables
from ETS2LA.Utils import settings

import multiprocessing
import traceback
import importlib
import requests
import queue
import time
import git

LOG_FILE_FOLDER = "logs"

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
    if settings.Get("global", "frontend_mirror", "Auto") == "Auto":
        print(_("Testing mirrors..."))
        response_times = {}
        for mirror in variables.FRONTEND_MIRRORS:
            try:
                start = time.perf_counter()
                requests.get(mirror, timeout=5)
                end = time.perf_counter()
                response_times[mirror] = end - start
                print(_("- Reached {0} in {1:.0f}ms").format(
                    YELLOW + mirror + END, 
                    response_times[mirror] * 1000
                ))
            except requests.RequestException:
                response_times[mirror] = float('inf')
                print(_(" - Reached {0} in (TIMEOUT)").format(YELLOW + mirror + END))
            
        fastest_mirror = min(response_times, key=response_times.get) # type: ignore
        return fastest_mirror
    else:
        mirror = settings.Get("global", "frontend_mirror", "Auto")
        print(_("Using mirror from settings: {0}").format(YELLOW + mirror + END)) # type: ignore
        return mirror # type: ignore

def update_frontend() -> bool:
    did_update = EnsureSubmoduleExists(
        "Interface", 
        "https://github.com/ETS2LA/frontend.git", 
        download_updates=False if "--dev" in sys.argv else True,
        cdn_url="http://cdn.ets2la.com/frontend", 
        cdn_path="frontend-main"
    )
    
    if did_update:
        print(GREEN + _(" -- Running post download action for submodule:  Interface  -- ") + END)
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
            print(PURPLE + _("Running ETS2LA in development mode.") + END)

        if "--local" in sys.argv:
            update_frontend()
            print(PURPLE + _("Running UI locally") + END)

        elif "--frontend-url" not in sys.argv:
            url = get_fastest_mirror()
            if not url:
                print(RED + _("No connection to remote UI mirrors. Running locally.") + END)
                update_frontend()
                    
                if not "--local" in sys.argv:
                    sys.argv.append("--local")
                ETS2LA.variables.LOCAL_MODE = True
                
            elif ".cn" in url:
                if not "--china" in sys.argv:
                    sys.argv.append("--china")
                ETS2LA.variables.CHINA_MODE = True
                print(PURPLE + _("Running UI in China mode") + END)

            print("\n" + YELLOW + _("> Using mirror {0} for UI.").format(url) + END + "\n")
            sys.argv.append("--frontend-url")
            sys.argv.append(url)
        
        if "--no-console" in sys.argv:
            if "--no-ui" in sys.argv:
                print(RED + _("--no-console cannot be used in combination with --no-ui. The console will not close.") + END)
            else:
                print(PURPLE + _("Closing console after UI start.") + END)

        if "--no-ui" in sys.argv:
            print(PURPLE + _("Running in the background without a window.") + END)

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
    print(BLUE + _("ETS2LA Overseer started!") + END + "\n")

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
                print(YELLOW + _("ETS2LA is restarting...") + END)
                continue
            
            if e.args[0] == "Update":
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if "--dev" in sys.argv:
                    print(YELLOW + _("Skipping update due to development mode.") + END)
                    continue
                
                print(YELLOW + _("ETS2LA is updating...") + END)
                ExecuteCommand("update.bat")
                
                print(GREEN + _("Update done... restarting!") + END + "\n")
                reset()
                continue
            
            # At this point we're sure that this is a crash
            print(RED + _("ETS2LA has crashed!") + END)
            print(trace)
            
            # Crash reports currently do not work, disabled to save bandwidth
            '''
            try: cloud.SendCrashReport("ETS2LA 2.0 - Main", trace, additional=get_current_version_information)
            except: pass
            '''

            print(_("Send the above traceback to the developers."))
            reset()
            print(RED + _("ETS2LA has closed.") + END)
            input(_("Press enter to exit."))
            sys.exit(0)
        
        except queue.Empty:
            pass
        
# IGNORE: This comment is just used to trigger an update and clear 
#         the cache of the app for changes that don't necessarily 
#         happen inside of this repository (like the frontend).
# 
# Counter: 24