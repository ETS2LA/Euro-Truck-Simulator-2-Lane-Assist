requirements = ["opencv-python", "pygame", "keyboard"]
import os

def install():
    
    for requirement in requirements:
        os.system("pip install " + requirement)
        
    pass
