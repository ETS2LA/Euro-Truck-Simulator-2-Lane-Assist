requirements = ["requests"]
import os

# This fucntion will be run when the plugin is first discovered.
# It is recommended to download all requirements here!
def install():
    
    import subprocess
    from progress.spinner import MoonSpinner
    import time
    for requirement in requirements:
        spinner = MoonSpinner(f"Installing {requirement}... ")
        timer = time.time()
        try:
                process = subprocess.Popen(["pip", "install", "-q", "-q", requirement])
        except:
            os.system("whoami")
            print("Ignore the above text, for some reason the pip command failed, and I don't know why, but running whoami seems to fix it.\nPlease... if you know why this happens, do tell me.")
            process = subprocess.Popen(["pip", "install", "-q", "-q", requirement])
        while process.poll() is None:
            if time.time() - timer > 0.2:
                spinner.next()
                timer = time.time()
        spinner.finish()
        
    pass