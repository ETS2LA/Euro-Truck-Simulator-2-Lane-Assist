"""This file serves as the overseer to ETS2LA. It allows the app to restart itself without user input."""
if __name__ == "__main__":
    import sys
    import os
    error = None
    # Import ETS2LA.core will import and run the app. Do that repeatedly in case of a crash.
    while True:
        try:
            import ETS2LA.core
            ETS2LA.core.run()
            if error is not None:
                print("ETS2LA has restarted successfully.")
                error = None
            else:
                print("ETS2LA has started successfully.")
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

            import traceback
            if traceback.format_exc() == error:
                print("ETS2LA has crashed with the same error. Send the above traceback to the developers.")
                if os.name == "nt":
                    os.system("taskkill /F /IM node.exe")
                else:
                    os.system("pkill -f node")
                input("Press enter to exit...")
                print("\033[91m" + "ETS2LA has been closed." + "\033[0m")
                sys.exit(0)
            
            print(f"ETS2LA has crashed with the following error:")
            traceback.print_exc()
            error = traceback.format_exc()
            print("\nAttempting to restart...")
            if os.name == "nt":
                    os.system("taskkill /F /IM node.exe")
            else:
                os.system("pkill -f node")
            continue
