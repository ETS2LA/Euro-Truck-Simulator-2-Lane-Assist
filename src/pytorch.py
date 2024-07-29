import src.variables as variables
import src.console as console
import subprocess
import threading
import time
import os

RED = "\033[91m"
GREEN = "\033[92m"
NORMAL = "\033[0m"

ALLOW_INSTALL = True

def CheckPyTorch():
    path = os.path.dirname(os.path.dirname(variables.PATH)) + "/"

    def UpdatePyTorch(command, module):
        global ALLOW_INSTALL
        while ALLOW_INSTALL == False:
            time.sleep(0.1)
        ALLOW_INSTALL = False
        command = str(command).replace("/", "\\")
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
        print(GREEN + f"'{module}' has been updated." + NORMAL)
        ALLOW_INSTALL = True

    if os.path.exists(path + "venv/Scripts/activate.bat"):
        result = subprocess.run("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip list", shell=True, capture_output=True, text=True)
        modules = result.stdout
        torch_found = False
        torchvision_found = False
        torchaudio_found = False
        for module in modules.splitlines():
            if "torch " in module:
                torch_found = True
                if "cu" in module:
                    try:
                        import torch
                    except Exception as ex:
                        if "fbgemm.dll" in str(ex):
                            print(RED + "'torch' is installed with CUDA, a possible fix might be to do the following things:" + NORMAL + "\n > Run the activate.bat in " + path.replace('\\', '/') + "\n > Run the command " + GREEN + "pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall" + NORMAL + "\n > Restart the app\n")
                        else:
                            print(RED + "'torch' is installed with CUDA, please check yourself or ask us on discord why pytorch with CUDA is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torch', please don't close the app, it could take a few minutes." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torch")).start()
            elif "torchvision " in module:
                torchvision_found = True
                if "cu" in module:
                    try:
                        import torchvision
                    except Exception as ex:
                        if "fbgemm.dll" in str(ex):
                            print(RED + "'torchvision' is installed with CUDA, a possible fix might be to do the following things:" + NORMAL + "\n > Run the activate.bat in " + path.replace('\\', '/') + "\n > Run the command " + GREEN + "pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall" + NORMAL + "\n > Restart the app\n")
                        else:
                            print(RED + "'torchvision' is installed with CUDA, please check yourself or ask us on discord why pytorch with CUDA is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torchvision', please don't close the app, it could take a few minutes." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torchvision")).start()
            elif "torchaudio " in module:
                torchaudio_found = True
                if "cu" in module:
                    try:
                        import torchaudio
                    except Exception as ex:
                        if "fbgemm.dll" in str(ex):
                            print(RED + "'torchaudio' is installed with CUDA, a possible fix might be to do the following things:" + NORMAL + "\n > Run the activate.bat in " + path.replace('\\', '/') + "\n > Run the command " + GREEN + "pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall" + NORMAL + "\n > Restart the app\n")
                        else:
                            print(RED + "'torchaudio' is installed with CUDA, please check yourself or ask us on discord why pytorch with CUDA is not working." + NORMAL)
                    console.RestoreConsole()
                else:
                    print(GREEN + "The app is working on a fix for the problem with 'torchaudio', please don't close the app, it could take a few minutes." + NORMAL)
                    threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torchaudio")).start()

        if torch_found == False:
            print(GREEN + "The app is working on a fix for the problem with 'torch', please don't close the app, it could take a few minutes." + NORMAL)
            threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torch")).start()
        if torchvision_found == False:
            print(GREEN + "The app is working on a fix for the problem with 'torchvision', please don't close the app, it could take a few minutes." + NORMAL)
            threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torchvision")).start()
        if torchaudio_found == False:
            print(GREEN + "The app is working on a fix for the problem with 'torchaudio', please don't close the app, it could take a few minutes." + NORMAL)
            threading.Thread(target=UpdatePyTorch, args=("cd " + path + "venv/Scripts & .\\activate.bat & cd " + path + " & pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --force-reinstall", "torchaudio")).start()

    else:

        print(RED + "The app is not installed in a virtual environment, please check yourself why PyTorch is not working." + NORMAL)
        console.RestoreConsole()