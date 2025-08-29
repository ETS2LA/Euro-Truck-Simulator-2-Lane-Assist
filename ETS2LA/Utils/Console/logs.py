from ETS2LA.Utils.translator import _
from ETS2LA.Utils.Console.colors import *
import os

def ClearLogFiles(folder="logs"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for file in os.listdir(folder):
        if file.endswith(".log"):
            try:
                os.remove(os.path.join(folder, file))
            except Exception as e:
                print(f"{RED}{_('Error removing log files. Probably another running ETS2LA instance. Please close it and try again.')}\n{END}{file} - {e}")
                raise e

def CountErrorsAndWarnings(folder="logs"):
    print("\n" + _("Errors and warnings in the log files:"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    count = 0
    for file in os.listdir(folder):
        if file.endswith(".log"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                content = f.read()
                errors = content.count("ERR")
                warnings = content.count("WRN")
                if errors != 0 or warnings != 0:
                    count += 1
                    print()
                    print(f"{DARK_GRAY}┌─── {file}{END}")
                if errors != 0:
                    print(f"{DARK_GRAY}│{RED} {_('Errors: ')} {errors} {END}")
                if warnings != 0:
                    print(f"{DARK_GRAY}│{YELLOW} {_('Warnings: ')} {warnings} {END}")
                if errors != 0 or warnings != 0:
                    print(f"{DARK_GRAY}└───{END}")
                    
    if count == 0:
        print(f"{GREEN}{_('No errors or warnings found.')}{END}")