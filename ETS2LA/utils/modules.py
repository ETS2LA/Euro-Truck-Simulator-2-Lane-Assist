import ETS2LA.variables as variables
import subprocess
import threading
import time
import os

RED = "\033[91m"
GREEN = "\033[92m"
NORMAL = "\033[0m"

ALLOW_INSTALL = True

def CheckPyTorch(runner):
    global max_threads, threads, updated
    max_threads = 0
    threads = []
    updated = 0
    path = os.path.dirname(os.path.dirname(os.path.dirname(variables.PATH))) + "/"

    def UpdatePyTorch(command, module):
        global max_threads, threads, updated
        global ALLOW_INSTALL
        while ALLOW_INSTALL == False:
            time.sleep(0.1)
        ALLOW_INSTALL = False
        runner.state = (f"Reinstalling '{module}' because of issues with the module. Please don't close the app, it could take a few minutes.")
        runner.state_progress = (updated + 0.5) / max_threads
        runner.UpdateState()
        command = str(command)
        subprocess.run(command, shell=True)
        updated += 1
        threads = threads[1:]
        ALLOW_INSTALL = True

    if os.path.exists(path + "venv/Scripts/activate.bat"):
        result = subprocess.run("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip list", shell=True, capture_output=True, text=True)
        modules = result.stdout
        torch_found = False
        torchvision_found = False
        torchaudio_found = False
        for module in modules.splitlines():
            if "torch " in module:
                torch_found = True
                try:
                    import torch
                except:
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torch")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torch==2.3.1 --force-reinstall", "torch")))
            elif "torchvision " in module:
                torchvision_found = True
                try:
                    import torchvision
                except:
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torchvision")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchvision==0.18.1 --force-reinstall", "torchvision")))
            elif "torchaudio " in module:
                torchaudio_found = True
                try:
                    import torchaudio
                except:
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torchaudio")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchaudio==2.3.1 --force-reinstall", "torchaudio")))

        if torch_found == False:
            threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torch==2.3.1 --force-reinstall", "torch")))
        if torchvision_found == False:
            threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchvision==0.18.1 --force-reinstall", "torchvision")))
        if torchaudio_found == False:
            threads.append(threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install torchaudio==2.3.1 --force-reinstall", "torchaudio")))

    else:

        if runner.ask("The app is not installed in a virtual environment, are you fine with the code installing torch 2.3.1, torchvision 0.18.1 and torchaudio 2.3.1 to be able to use the AI features?") == "Yes":
            result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
            modules = result.stdout
            torch_found = False
            torchvision_found = False
            torchaudio_found = False
            for module in modules.splitlines():
                if "torch " in module:
                    torch_found = True
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torch")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torch==2.3.1 --force-reinstall", "torch")))
                elif "torchvision " in module:
                    torchvision_found = True
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torchvision")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchvision==0.18.1 --force-reinstall", "torchvision")))
                elif "torchaudio " in module:
                    torchaudio_found = True
                    if "cu" in module:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall", "torchaudio")))
                    else:
                        threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchaudio==2.3.1 --force-reinstall", "torchaudio")))

            if torch_found == False:
                threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torch==2.3.1 --force-reinstall", "torch")))
            if torchvision_found == False:
                threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchvision==0.18.1 --force-reinstall", "torchvision")))
            if torchaudio_found == False:
                threads.append(threading.Thread(target=UpdatePyTorch, args=("pip install torchaudio==2.3.1 --force-reinstall", "torchaudio")))

    max_threads = len(threads)
    for thread in threads:
        thread.start()
        time.sleep(0.1)

    while True:
        any_thread_alive = False
        for thread in threads:
            if thread.is_alive():
                any_thread_alive = True
                break
        if any_thread_alive == False:
            break
        time.sleep(0.1)

    if max_threads > 0:
        runner.state = (f"The broken modules have been fixed, the AI features should work now.")
        runner.state_progress = 1
        runner.UpdateState()
        time.sleep(5)
        runner.state = "running"
        runner.state_progress = -1
        runner.UpdateState()


def CheckNumPy(runner):
    global max_threads, threads, updated
    max_threads = 0
    threads = []
    updated = 0
    path = os.path.dirname(os.path.dirname(os.path.dirname(variables.PATH))) + "/"

    def UpdateNumPy(command, module):
        global max_threads, threads, updated
        global ALLOW_INSTALL
        while ALLOW_INSTALL == False:
            time.sleep(0.1)
        ALLOW_INSTALL = False
        runner.state = (f"Reinstalling '{module}' because of issues with the module. Please don't close the app, it could take a few minutes.")
        runner.state_progress = (updated + 0.5) / max_threads
        runner.UpdateState()
        command = str(command)
        subprocess.run(command, shell=True)
        updated += 1
        threads = threads[1:]
        ALLOW_INSTALL = True

    if os.path.exists(path + "venv/Scripts/activate.bat"):
        result = subprocess.run("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip list", shell=True, capture_output=True, text=True)
        modules = result.stdout
        numpy_found = False
        for module in modules.splitlines():
            if "numpy " in module:
                numpy_found = True
                if module.replace("numpy", "").replace(" ", "") != "1.26.4":
                    threads.append(threading.Thread(target=UpdateNumPy, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install numpy==1.26.4 --force-reinstall", "numpy")))

        if numpy_found == False:
            threads.append(threading.Thread(target=UpdateNumPy, args=("cd " + path + "venv/Scripts & ./activate.bat & cd " + path + " & pip install numpy==1.26.4 --force-reinstall", "numpy")))

    else:

        result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
        modules = result.stdout
        numpy_found = False
        for module in modules.splitlines():
            if "numpy " in module:
                numpy_found = True
                if module.replace("numpy", "").replace(" ", "") != "1.26.4":
                    if runner.ask("The app is not installed in a virtual environment, are you fine with the code installing numpy 1.26.4 to be able to use the AI features?") == "Yes":
                        threads.append(threading.Thread(target=UpdateNumPy, args=("pip install numpy==1.26.4 --force-reinstall", "numpy")))

        if numpy_found == False:
            if runner.ask("The app is not installed in a virtual environment, are you fine with the code installing numpy 1.26.4 to be able to use the AI features?") == "Yes":
                threads.append(threading.Thread(target=UpdateNumPy, args=("pip install numpy==1.26.4 --force-reinstall", "numpy")))

    max_threads = len(threads)
    for thread in threads:
        thread.start()
        time.sleep(0.1)

    while True:
        any_thread_alive = False
        for thread in threads:
            if thread.is_alive():
                any_thread_alive = True
                break
        if any_thread_alive == False:
            break
        time.sleep(0.1)

    if max_threads > 0:
        runner.state = (f"The broken module has been fixed, the AI features should work now.")
        runner.state_progress = 1
        runner.UpdateState()
        time.sleep(5)
        runner.state = "running"
        runner.state_progress = -1
        runner.UpdateState()