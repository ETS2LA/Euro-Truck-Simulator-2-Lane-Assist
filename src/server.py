"""This file is used to communicate with the main app server. The file will not be used without consent from the user."""
import requests
import json
import time
import os
import src.settings as settings 
from src.translator import Translate
import src.variables as var
import src.helpers as helpers
from src.logger import print

ALLOW_CRASH_REPORTS = settings.GetSettings("CrashReporter", "AllowCrashReports")
"""Whether or not crash reports are allowed to be sent to the developers. This will help us fix bugs faster. Defaults to False."""

if ALLOW_CRASH_REPORTS == None:
    from tkinter import messagebox
    if messagebox.askyesno("Crash reports", Translate("Do you want to allow crash reports to be sent to the developers? This will help us fix bugs faster.\n\nCrash reports are anonymous and will not contain any personal information")):
        ALLOW_CRASH_REPORTS = True
        settings.CreateSettings("CrashReporter", "AllowCrashReports", True)
    else:
        settings.CreateSettings("CrashReporter", "AllowCrashReports", False)
        ALLOW_CRASH_REPORTS = False
        
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
        if ALLOW_CRASH_REPORTS:
            
            additional = {
                "version": var.VERSION,
                "os": var.OS,
                "language": settings.GetSettings("User Interface", "DestinationLanguage"),
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
        else:
            print("Crash detected, but crash reports are not allowed to be sent.")
            import traceback
            traceback.print_exc()
    except:
        import traceback
        traceback.print_exc()
        print("Crash report sending failed.")

def GetMotd():
    """Get the message of the day from the main application server. This will be shown to the user when the app is opened.

    Returns:
        str: Message of the day
    """
    
    # if not ALLOW_CRASH_REPORTS:
    #     return "Please enable crash reporting to fetch MOTD."
    
    try:
        #url = 'https://crash.tumppi066.fi/motd'
        #response = json.loads(requests.get(url, timeout=1).text)
        return "The V1 server backend has been shut down. V2 is available via the discord server. A full release should come out in February."
    except:
        return "Could not get server message."
    
def GetUserCount():
    """Get the amount of users using the app. This will be shown to the user when the app is opened.

    Returns:
        str: User count
    """
    
    if not ALLOW_CRASH_REPORTS:
        return "Please enable crash reporting to fetch user count."
    
    try:
        url = 'https://crash.tumppi066.fi/usercount'
        response = json.loads(requests.get(url, timeout=1).text)
        return response["usercount"]
    except:
        return "Could not get user count."
    
def Ping():
    """Will send a ping to the server, doesn't send any data."""
    try:
        last_ping = float(settings.GetSettings("User Interface", "last_ping", 0))
        current_time = time.time()
        if last_ping + 59 < current_time:
            url = 'https://crash.tumppi066.fi/ping'
            requests.get(url, timeout=1)
            settings.CreateSettings("User Interface", "last_ping", str(current_time))
    except:
        pass
