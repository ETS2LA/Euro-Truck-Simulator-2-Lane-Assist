"""Here's the runner for ETS2LA.

ETS2LA is designed to be run from this file. This is a kind of
"overseer" that will handle updates and any ETS2LA crashes.

If you are looking for the actual **entrypoint** then you should
look at the core.py file in the ETS2LA folder.
"""

import os
import sys
import subprocess

if os.name == "nt":
    import ctypes

    try:
        if ctypes.windll.shell32.IsUserAnAdmin()():
            print(
                "ERROR: ETS2LA is running with Administrator privileges.\n"
                "This is not recommended, as it may interfere with system behavior or cause unintended issues.\n"
                "Please restart ETS2LA without Administrator mode."
            )
            input("Press enter to exit...")
            sys.exit(1)
    except Exception:
        pass

# This try/except block will either end in a successful import, update, or error
try:
    from ETS2LA.Utils.translator import _
except Exception:
    # Ensure the current PATH contains the install directory.
    sys.path.append(os.path.dirname(__file__))
    try:
        from ETS2LA.Utils.translator import _
    except (
        ModuleNotFoundError
    ):  # If modules are missing, this will trigger (generally tqdm)
        print(
            "Import errors in ETS2LA/Utils/translator.py, this is a common sign of missing modules. An update will be triggered to install these modules."
        )
        subprocess.run("update.bat", shell=True, env=os.environ.copy())
        from ETS2LA.Utils.translator import _
    except Exception as e:  # Unexpected error, print it and exit
        try:
            import traceback

            print(traceback.format_exc())
        except Exception:
            print(str(e))
        input("Press enter to exit...")
        sys.exit()

# Allow pygame to get control events in the background
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
# Hide pygame's support prompt
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from ETS2LA.Utils.Console.colors import RED, GREEN, BLUE, YELLOW, PURPLE, END
from ETS2LA.Utils.Console.logs import CountErrorsAndWarnings, ClearLogFiles
from ETS2LA.Utils.submodules import EnsureSubmoduleExists
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Networking.cloud as cloud
import ETS2LA.variables as variables
from ETS2LA.Settings import GlobalSettings

import multiprocessing
import traceback
import importlib
import requests
import queue
import time
import git

LOG_FILE_FOLDER = "logs"
settings = GlobalSettings()


def close_node() -> None:
    """Will kill all node instances."""
    if os.name == "nt":
        ExecuteCommand("taskkill /F /IM node.exe > nul 2>&1")
    else:
        ExecuteCommand("pkill -f node > /dev/null 2>&1")


def reset(clear_logs=True, page_process=None) -> None:
    """Reset ETS2LA.

    - Close any node instances,
    - Clear log files if needed,
    - Count errors and warnings,
    - Terminate the page process if given.
    """
    close_node()
    if page_process:
        if page.is_alive():
            page.terminate()

    CountErrorsAndWarnings()
    if clear_logs:
        try:
            ClearLogFiles()
        except Exception:
            exit()


def get_commit_url(repo: git.Repo, commit_hash: str) -> str:
    """Return the URL to the given commit hash."""
    try:
        remote_url = repo.remotes.origin.url
        remote_url = remote_url.replace(".git", "")

        return remote_url + "/commit/" + commit_hash
    except Exception:
        return ""


def get_current_version_information() -> dict:
    """Return the current git branch and commit hash."""
    try:
        repo = git.Repo()
        current_hash = repo.head.object.hexsha
        current_branch = repo.active_branch.name
        return {
            "name": current_branch,
            "link": get_commit_url(repo, current_hash),
            "time": time.ctime(repo.head.object.committed_date),
        }
    except Exception:
        return {"name": "Unknown", "link": "Unknown", "time": "Unknown"}


def get_fastest_mirror() -> str:
    """Find the fastest frontend mirror.

    - If setting is "Auto", ETS2LA will poll all servers.
    - If a specific mirror is set, that will be used directly.
    """

    if not settings.frontend_mirror or settings.frontend_mirror.strip() == "":
        settings.frontend_mirror = "Auto"

    if settings.frontend_mirror == "Auto":
        print(_("Testing mirrors..."))
        response_times = {}
        for mirror in variables.FRONTEND_MIRRORS:
            try:
                start = time.perf_counter()
                requests.get(mirror, timeout=5)
                end = time.perf_counter()
                response_times[mirror] = end - start
                print(
                    _("- Reached {0} in {1:.0f}ms").format(
                        YELLOW + mirror + END, response_times[mirror] * 1000
                    )
                )
            except requests.RequestException:
                response_times[mirror] = float("inf")
                print(_(" - Reached {0} in (TIMEOUT)").format(YELLOW + mirror + END))

        fastest_mirror = min(response_times, key=response_times.get)
        settings.frontend_mirror = fastest_mirror
        return fastest_mirror
    else:
        mirror = settings.frontend_mirror
        # print(_("Using mirror from settings: {0}").format(YELLOW + mirror + END))
        return mirror


def update_frontend() -> bool:
    """Update the frontend module if needed."""
    did_update = EnsureSubmoduleExists(
        "Interface",
        "https://github.com/ETS2LA/frontend.git",
        download_updates=False if "--dev" in sys.argv else True,
        cdn_url="http://cdn.ets2la.com/frontend",
        cdn_path="frontend-main",
    )

    if did_update:
        print(
            GREEN
            + _(" -- Running post download action for submodule:  Interface  -- ")
            + END
        )
        ExecuteCommand("cd Interface && npm install && npm run build-local")

    return did_update


def ets2la_process(
    exception_queue: multiprocessing.Queue, window_queue: multiprocessing.Queue
) -> None:
    """ETS2LA process.

    - This function will run ETS2LA with the given arguments.
    - It will also handle exceptions and updates to the submodules.

    The `exception_queue` is used to send exceptions back to the main process
    for handling (at the bottom of this file).
    """
    try:
        import ETS2LA.variables

        variables.WINDOW_QUEUE = window_queue

        if "--dev" in sys.argv:
            print(PURPLE + _("Running ETS2LA in development mode.") + END)

        if "--frontend-url" not in sys.argv:
            url = get_fastest_mirror()
            if not url:
                print(
                    RED
                    + _("No connection to remote UI mirrors. Running locally.")
                    + END
                )
                update_frontend()

                if "--local" not in sys.argv:
                    sys.argv.append("--local")
                ETS2LA.variables.LOCAL_MODE = True

            elif ".cn" in url:
                if "--china" not in sys.argv:
                    sys.argv.append("--china")
                ETS2LA.variables.CHINA_MODE = True
                print(PURPLE + _("Running UI in China mode") + END)

            print(
                "\n" + YELLOW + _("> Using mirror {0} for UI.").format(url) + END + "\n"
            )
            sys.argv.append("--frontend-url")
            sys.argv.append(url)
            variables.FRONTEND_URL = url

        if "--no-console" in sys.argv:
            if "--no-ui" in sys.argv:
                print(
                    RED
                    + _(
                        "--no-console cannot be used in combination with --no-ui. The console will not close."
                    )
                    + END
                )
            else:
                print(PURPLE + _("Closing console after UI start.") + END)

        close_node()
        try:
            ClearLogFiles()
        except Exception:
            exit()
        ETS2LA = importlib.import_module("ETS2LA.core")
        ETS2LA.run()

    except Exception as e:
        # Catch exit and restart seperately
        if str(e) != "exit" and str(e) != "restart":
            trace = traceback.format_exc()
            exception_queue.put((e, trace))
        else:
            exception_queue.put((e, None))


def window_process(window_queue: multiprocessing.Queue) -> None:
    """Run the ETS2LA window process."""
    try:
        import ETS2LA.variables

        variables.WINDOW_QUEUE = window_queue

        if "--no-ui" in sys.argv:
            print(PURPLE + _("Running in the background without a window.") + END)

        if "--local" in sys.argv:
            update_frontend()
            print(PURPLE + _("Running UI locally") + END)
            ETS2LA.variables.LOCAL_MODE = True

        elif "--frontend-url" not in sys.argv:
            url = get_fastest_mirror()
            if not url:
                sys.argv.append("--local")
                ETS2LA.variables.LOCAL_MODE = True

            sys.argv.append("--frontend-url")
            sys.argv.append(url)
            variables.FRONTEND_URL = url

        import ETS2LA.Window.window as window

        window.run()
    except Exception:
        trace = traceback.format_exc()
        print(RED + _("The window process has crashed!") + END)
        print(trace)


if __name__ == "__main__":
    window_queue = multiprocessing.JoinableQueue()
    exception_queue = multiprocessing.Queue()
    page = None
    print(BLUE + _("ETS2LA Overseer started!") + END + "\n")

    while True:
        get_fastest_mirror()

        if not page or not page.is_alive():
            page = multiprocessing.Process(
                target=window_process, args=(window_queue,), daemon=True
            )
            page.start()

        process = multiprocessing.Process(
            target=ets2la_process,
            args=(
                exception_queue,
                window_queue,
            ),
        )
        process.start()
        process.join()

        try:
            # Exit by process end / crash
            e, trace = exception_queue.get_nowait()

            if e.args[0] == "exit":
                reset(clear_logs=False, page_process=page)
                sys.exit(0)

            if e.args[0] == "restart":
                reset(page_process=page)
                print(YELLOW + _("ETS2LA is restarting...") + END)
                continue

            if e.args[0] == "Update":
                window_queue.put({"type": "update"})
                time.sleep(2)
                # Check if running with the --dev flag to prevent accidentally overwriting changes
                if "--dev" in sys.argv:
                    print(YELLOW + _("Skipping update due to development mode.") + END)
                    reset()
                    continue

                print(YELLOW + _("ETS2LA is updating...") + END)
                ExecuteCommand("update.bat")

                print(GREEN + _("Update done... restarting!") + END + "\n")
                reset()
                continue

            # At this point we're sure that this is a crash
            print(RED + _("ETS2LA has crashed!") + END)
            print(trace)

            try:
                cloud.SendCrashReport(
                    "Process Crash",
                    "The ETS2LA process itself has crashed.",
                    {
                        "Error": str(e),
                    },
                )
            except Exception:
                pass

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
# Counter: 26
