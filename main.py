"""This file serves as the overseer to ETS2LA. It allows the app to restart itself without user input."""
if __name__ == "__main__":
    import sys
    import traceback
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # hide pygame welcome message before importing pygame module in any script
    # Import ETS2LA.core will import and run the app. Do that repeatedly in case of a crash.
    while True:
        try:
            import ETS2LA.core
            ETS2LA.core.run()
            print("ETS2LA has started successfully!")
        except Exception as e:
            if e.args[0] == "exit":
                if os.name == "nt":
                    os.system("taskkill /F /IM node.exe")
                else:
                    os.system("pkill -f node")
                print("\033[91m" + "ETS2LA has been closed." + "\033[0m")
                sys.exit(0)

            if e.args[0] == "restart":
                if os.name == "nt":
                    os.system("taskkill /F /IM node.exe")
                else:
                    os.system("pkill -f node")
                print("\033[93m" + "ETS2LA is restarting..." + "\033[0m")
                continue
            
            print(f"ETS2LA has crashed with the following error:")
            traceback.print_exc()
            error = traceback.format_exc()
            print("Send the above traceback to the developers.")
            if os.name == "nt":
                os.system("taskkill /F /IM node.exe")
            else:
                os.system("pkill -f node")
            print("\033[91m" + "ETS2LA has been closed." + "\033[0m")
            input("Press enter to exit...")
            sys.exit(0)