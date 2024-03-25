"""This file serves as the overseer to ETS2LA. It allows the app to restart itself without user input."""
if __name__ == "__main__":
    error = None
    # Import ETS2LA.core will import and run the app. Do that repeatedly in case of a crash.
    while True:
        try:
            import ETS2LA.core
            if error is not None:
                print("ETS2LA has restarted successfully.")
                error = None
            else:
                print("ETS2LA has started successfully.")
        except Exception as e:
            if Exception == SystemExit or Exception == KeyboardInterrupt:
                print("ETS2LA has been stopped.")
                break

            import traceback
            if traceback.format_exc() == error:
                print("ETS2LA has crashed with the same error. Send the above traceback to the developers.")
                input("Press enter to exit...")
                break
            
            print(f"ETS2LA has crashed with the following error:")
            traceback.print_exc()
            error = traceback.format_exc()
            print("\nAttempting to restart...")
            continue