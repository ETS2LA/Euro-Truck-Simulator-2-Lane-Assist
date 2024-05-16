"""This file will run all the plugin install scripts in addition to installing all requirements from requirements.txt."""
if __name__ == "__main__":
    # Find all folders in plugins/
    # Run install.py (install function) in each folder
    import os
    import sys
    import importlib.util

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    # Get the path to the requirements.txt file
    requirementsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    file = open(requirementsPath, "r")
    requirements = file.readlines()
    file.close()

    # Install all requirements
    print("Installing requirements...")
    for requirement in requirements:
        requirement = requirement.strip()
        if requirement != "":
            print(f"Installing {requirement}...")
            try:
                os.system(f"pip install {requirement}")
                print(f"{GREEN}SUCCESS: Installed {requirement}{RESET}")
            except:
                import traceback
                traceback.print_exc()
                print(f"{RED}ERROR: Failed to install {requirement}")
                print(f"{YELLOW}The app might still work, but this is usually not good.{RESET}")

    # Get the path to the plugins folder
    pluginsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")

    # Get all folders in the plugins folder
    plugins = [f.path for f in os.scandir(pluginsPath) if f.is_dir()]
    for plugin in plugins:
        # Get the install.py file in each folder
        installPath = os.path.join(plugin, "install.py")
        if os.path.exists(installPath):
            # Import the install.py file
            spec = importlib.util.spec_from_file_location("install", installPath)
            install = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(install)
            # Run the install function
            print(f"Running install script for {plugin}")
            try:
                install.install()
                print(f"{GREEN}SUCCESS: Ran install script for {plugin}{RESET}")
            except:
                import traceback
                traceback.print_exc()
                print(f"{RED}ERROR: Failed to run install script for {plugin}")
                print(f"{YELLOW}The plugin might still work, but this is usually not good.{RESET}")