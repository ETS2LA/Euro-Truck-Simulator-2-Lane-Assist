"""This file serves as the overseer to ETS2LA. It allows the app to restart itself without user input."""

if __name__ == "__main__":
    # Import ETS2LA.core will import and run the app. Do that repeatedly in case of a crash.
    while True:
        try:
            import ETS2LA.core
        except Exception as e:
            if Exception == SystemExit or Exception == KeyboardInterrupt:
                print("ETS2LA has been stopped.")
                break
            
            print(f"ETS2LA has crashed with the following error:")
            import traceback
            traceback.print_exc()
            print("Restarting...")
            continue