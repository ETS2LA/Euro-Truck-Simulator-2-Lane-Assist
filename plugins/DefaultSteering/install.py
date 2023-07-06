requirements = ["opencv-python"]
import os

def install():
    
    for requirement in requirements:
        os.system("pip install " + requirement)
        
    pass