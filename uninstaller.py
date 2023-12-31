import os
import sys
import shutil
import getpass

USERNAME = getpass.getuser()
PATH = os.path.dirname(os.path.realpath(__file__))

# STEP 1
# Delete the app folder
try:
    shutil.rmtree(PATH + r"\app", ignore_errors=True)
except:
    pass
input("Removed app folder, press enter to continue...")

# STEP 2 
# Delete the start menu entry
filename = "ETS2 Lane Assist.lnk"
try:
    os.remove(fr"C:\Users\{USERNAME}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\{filename}") 
except:
    pass
input("Removed start menu entry, press enter to continue...")

# STEP 3 
# TODO: Delete the ViGEmBus driver
# os.system(f"cd {PATH}")
# os.system("cd /venv/Lib/site-packages/vgamepad/win/vigem/install/x64")

# STEP 4
# Delete the venv folder
os.system(f"cd {PATH}")
try:
    shutil.rmtree(PATH + r"\venv")
except:
    pass
input("Removed venv folder, press enter to continue...")

# STEP 5
# Remove everything in the current folder
input("WARNING: This will delete everything in the current folder, press enter to continue...")
os.system(f"cd {PATH}")
os.system("del /f /q *")