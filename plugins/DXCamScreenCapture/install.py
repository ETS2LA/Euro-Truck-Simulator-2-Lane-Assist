requirements = ["https://github.com/AI-M-BOT/DXcam/archive/592acb7325e3a463ff1e186c5745dfdcec7e82b4.zip"]
import os

def install():
    
    if os.name == "nt":
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