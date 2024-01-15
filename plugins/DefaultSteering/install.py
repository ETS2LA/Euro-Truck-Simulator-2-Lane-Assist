requirements = ["opencv-python", "pygame", "keyboard"]
import os

def install():
    
    import subprocess
    from progress.spinner import MoonSpinner
    import time
    for requirement in requirements:
        spinner = MoonSpinner(f"Installing {requirement}... ")
        timer = time.time()
        process = subprocess.Popen(["pip", "install", "-q", "-q", requirement])
        while process.poll() is None:
            if time.time() - timer > 0.2:
                spinner.next()
                timer = time.time()
        spinner.finish()
        
    pass
