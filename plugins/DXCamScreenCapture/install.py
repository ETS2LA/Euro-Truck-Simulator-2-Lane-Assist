requirements = ["https://github.com/AI-M-BOT/DXcam/archive/refs/heads/main.zip"]
import os

def install():
    
    if os.name == "nt":
        for requirement in requirements:
            os.system("pip install " + requirement)
        
    pass