requirements = ["https://github.com/AI-M-BOT/DXcam/archive/592acb7325e3a463ff1e186c5745dfdcec7e82b4.zip"]
import os

def install():
    
    if os.name == "nt":
        for requirement in requirements:
            os.system("pip install " + requirement)
        
    pass