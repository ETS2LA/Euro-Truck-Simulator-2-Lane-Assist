import ETS2LA.variables as variables
import ETS2LA.utils.console as console
import subprocess
import threading
import os

RED = "\033[91m"
GREEN = "\033[92m"
NORMAL = "\033[0m"

def CheckPyTorch():
    path = os.path.dirname(os.path.dirname(variables.PATH)) + "\\"

    def UpdatePyTorch(command, module):
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
        print(GREEN + f"'{module}' has been updated." + NORMAL)

    if os.path.exists(path + "venv/Scripts/activate.bat"):
        result = subprocess.run("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip list", shell=True, capture_output=True, text=True)
        modules = result.stdout
        for module in modules.splitlines():
            if "torch " in module:
                if "cu" in module:
                    print(RED + "'torch' is installed with CUDA, please check yourself why the app is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torch', please don't close the app." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch --upgrade", "torch")).start()
            elif "torchvision " in module:
                if "cu" in module:
                    print(RED + "'torchvision' is installed with CUDA, please check yourself why the app is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torchvision', please don't close the app." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torchvision --upgrade", "torchvision")).start()
            elif "torchaudio " in module:
                if "cu" in module:
                    print(RED + "'torchaudio' is installed with CUDA, please check yourself why the app is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torchaudio', please don't close the app." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torchaudio --upgrade", "torchaudio")).start()

    else:

        print(RED + "The app is not installed in a virtual environment, please check yourself why PyTorch is not working." + NORMAL)
        console.RestoreConsole()