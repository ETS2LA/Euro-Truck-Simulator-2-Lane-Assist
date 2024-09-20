import ETS2LA.variables as variables
import ETS2LA.backend.settings as settings
import requests
import json

def SendCrashReport(type:str, message:str, additional=None):
    """Will send a crash report to the main application server. This will then be forwarded to the developers on discord.

    Args:
        type (str): Crash type
        message (str): Crash message
        additional (_type_, optional): Additional text / information. Defaults to None.

    Returns:
        success (bool): False if not successful, True if successful
    """

    # Check if the message is empty
    if message.strip() == "":
        return False

    try:
        send_crash_reports = settings.Get("global", "send_crash_reports", True)
    except:
        send_crash_reports = True
    if send_crash_reports:

        try:
            additional = {
                "version": "V2.0.0",
                "os": variables.OS,
                "language": "not implemented",
                "custom": additional
            }
            
            
            jsonData = {
                "type": type,
                "message": message,
                "additional": additional
            }
            
            url = 'https://crash.tumppi066.fi/crash'
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(jsonData)
            try:
                response = requests.post(url, headers=headers, data=data)
            except:
                print("Could not connect to server to send crash report.")
            return response.status_code == 200
        except:
            import traceback
            traceback.print_exc()
            print("Crash report sending failed.")
            return False
    else:
        print("Crash detected, but crash reporting is disabled.")
        return False
