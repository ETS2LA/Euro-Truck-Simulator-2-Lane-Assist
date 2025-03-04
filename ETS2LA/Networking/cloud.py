import ETS2LA.Utils.settings as settings
import ETS2LA.Events.classes as classes
import ETS2LA.variables as variables
from typing import Literal
import requests
import logging
import json
import uuid
import time

URL = "https://api.ets2la.com"
user_id = None
token = None
username = "unknown"

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

    # Check if running with the --dev flag to prevent spamming crash reports to the server
    if variables.DEVELOPMENT_MODE:
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
                "language": settings.Get("global", "language", "English"),
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
                return False
            return response.status_code == 200
        except:
            import traceback
            traceback.print_exc()
            print("Crash report sending failed.")
            return False
    else:
        print("Crash detected, but crash reporting is disabled.")
        return False
    
def GetUsername():
    user_id, token, success = GetCredentials()
    if success:
        url = URL + f'/user/{user_id}'
        headers = {
            "Authorization": f"Bearer {token}"
        }
        try:
            r = requests.get(url, headers=headers)
            return r.json()["data"]["username"]
        except Exception: pass
        
    return "unknown"    

def GetCredentials():
    global user_id, token
    if user_id is None:
        user_id = settings.Get("global", "user_id", str(uuid.uuid4()))
        if user_id == None:
            user_id = str(uuid.uuid4())
            settings.Set("global", "user_id", user_id)
            
        token = settings.Get("global", "token", None)
    
    return user_id, token, user_id is not None and token is not None

def StartedJob(job: classes.Job):
    user_id, token, success = GetCredentials()
    if success:
        url = URL + f'/user/{user_id}/job/started'
        headers = {
            'Authorization': f"Bearer {token}"
        }
        data = job.json()

        try:
            r = requests.post(url, headers=headers, json=data)
        except:
            print("Could not connect to server to send job data.")
            return False
        
        if r.json()["status"] == 200:
            logging.info("Successfully sent job data to the cloud.")
        else:
            logging.warning("Job data not saved, error: " + r.text)
        return r.json()["status"] == 200
    
    return False

def FinishedJob(job: classes.FinishedJob):
    user_id, token, success = GetCredentials()
    if success:
        url = URL + f'/user/{user_id}/job/finished'
        headers = {
            'Authorization': f"Bearer {token}"
        }
        data = job.json()

        try:
            r = requests.post(url, headers=headers, json=data)
        except:
            print("Could not connect to server to send job data.")
            return False
        
        if r.json()["status"] == 200:
            logging.info("Successfully sent job data to the cloud.")
        else:
            logging.warning("Job data not saved, error: " + r.text)
        return r.json()["status"] == 200
    
    return False

def CancelledJob(job: classes.CancelledJob):
    user_id, token, success = GetCredentials()
    if success:
        url = URL + f'/user/{user_id}/job/cancelled'
        headers = {
            'Authorization': f"Bearer {token}"
        }
        data = job.json()

        try:
            r = requests.post(url, headers=headers, json=data)
        except:
            print("Could not connect to server to send job data.")
            return False
        
        if r.json()["status"] == 200:
            logging.info("Successfully sent job data to the cloud.")
        else:
            logging.warning("Job data not saved, error: " + r.text)
        return r.json()["status"] == 200
    
    return False

def Ping(data = [0]):
    if time.time() - data[0] > 120: # once every 2 minutes
        user_id, _, _ = GetCredentials()
        
        url = URL + f'/tracking/ping/{user_id}'
        try:
            requests.get(url)
        except Exception: 
            pass
        
        data[0] = time.time()
        
def GetUniqueUsers(time: Literal["1h", "6h", "12h", "24h", "1w", "1m"] = "24h"):
    url = URL + '/tracking/users'
    try:
        r = requests.get(url)
        return r.json()["data"]["unique"][time]
    except:
        return 0
        
def GetUserCount():
    url = URL + '/tracking/users'
    try:
        r = requests.get(url)
        return r.json()["data"]["online"]
    except:
        return 0
    
def GetUserTime():
    user_id, _, _ = GetCredentials()
    url = URL + f'/tracking/time/{user_id}'
    try:
        r = requests.get(url)
        return r.json()["data"]["time_used"]
    except:
        return 0