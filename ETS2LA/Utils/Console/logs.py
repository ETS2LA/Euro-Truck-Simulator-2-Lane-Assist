from ETS2LA.Utils.translator import Translate
from ETS2LA.Utils.Console.colors import *
import os

def ClearLogFiles(folder="logs"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for file in os.listdir(folder):
        if file.endswith(".log"):
            os.remove(os.path.join(folder, file))
            
def CountErrorsAndWarnings(folder="logs"):
    print("\n" + Translate("main.errors_and_warnings"))
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
                    print(f"{DARK_GRAY}│{RED} {Translate('main.errors')} {errors} {END}")
                if warnings != 0:
                    print(f"{DARK_GRAY}│{YELLOW} {Translate('main.warnings')} {warnings} {END}")
                if errors != 0 or warnings != 0:
                    print(f"{DARK_GRAY}└───{END}")
                    
    if count == 0:
        print(f"{GREEN}{Translate('main.no_errors_or_warnings')}{END}")