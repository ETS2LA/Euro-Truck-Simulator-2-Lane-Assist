requirements = ["evdev"]
import os

def install():
    
    if os.name != "nt":
        for requirement in requirements:
            os.system("pip install -q -q " + requirement)
        
    pass