"""This file is used to communicate with the main app server. The file will not be used without consent from the user."""
import requests
import json
import src.settings as settings 
from src.translator import Translate

ALLOW_CRASH_REPORTS = settings.GetSettings("CrashReporter", "AllowCrashReports")
"""Whether or not crash reports are allowed to be sent to the developers. This will help us fix bugs faster. Defaults to False."""

if ALLOW_CRASH_REPORTS == None:
    from tkinter import messagebox
    if messagebox.askyesno("Crash reports", Translate("Do you want to allow crash reports to be sent to the developers? This will help us fix bugs faster.\n\nCrash reports are anonymous and will not contain any personal information")):
        ALLOW_CRASH_REPORTS = True
        settings.CreateSettings("CrashReporter", "AllowCrashReports", 1)
    else:
        settings.CreateSettings("CrashReporter", "AllowCrashReports", 0)

def SendCrashReport(type:str, message:str, additional=None):
    """Will send a crash report to the main application server. This will then be forwarded to the developers on discord.

    Args:
        type (str): Crash type
        message (str): Crash message
        additional (_type_, optional): Additional text / information. Defaults to None.

    Returns:
        success (bool): False if not successful, True if successful
    """
    try:
        if ALLOW_CRASH_REPORTS:
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
                print("Caould not connect to server to send crash report.")
            return response.status_code == 200
        else:
            print("Crash detected, but crash reports are not allowed to be sent.")
    except:
        print("Crash reports are not allowed to be sent.")
