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

def SendFeedback(message: str, username: str, fields: dict[str, str] = {}):
    """Will send a feedback message to the main application server. This will then be forwarded to the developers on discord.

    Args:
        message (str): The feedback message.
        username (str): The username of the user sending the feedback (e.g. Discord username or email address).
        fields (dict[str, str], optional): Additional fields to include in the feedback. Defaults to an empty dict. Key is field name, value is text.
    Returns:
        success (bool): False if not successful, True if successful
    """
    
    if message.strip() == "":
        return False
    
    if username.strip() == "":
        username = "anonymous"
        
    try:
        fields["ETS2LA Version"] = variables.METADATA["version"]
        fields["ETS2LA Language"] = settings.Get("global", "language", "English")
        
        jsonData = {
            "timestamp": int(time.time()),
            "user": username,
            "message": message,
            "fields": fields
        }
        
        url = 'https://api.ets2la.com/feedback'
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, headers=headers, json=jsonData)
        except:
            print("Could not connect to server to send feedback.")
            return False
        
        return response.status_code == 200
    except:
        import traceback
        traceback.print_exc()
        print("Feedback sending failed.")
        return False


def SendCrashReport(source: str, source_description: str, fields: dict[str, str] = {}):
    """Will send a crash report to the main application server. This will then be forwarded to the developers on discord.

    Args:
        source (str): The source of the crash report (e.g. "Backend", "AR Plugin", etc.)
        source_description (str): A description of the source (e.g. "This crash report occured in the main loop of the AR Plugin")
        fields (dict[str, str], optional): Additional fields to include in the crash report. Defaults to an empty dict. Key is field name, value is text.

    Returns:
        success (bool): False if not successful, True if successful
    """

    if source_description.strip() == "" or source.strip() == "":
        return False

    # Don't spam in dev mode.
    if variables.DEVELOPMENT_MODE:
        return False

    try: send_crash_reports = settings.Get("global", "send_crash_reports", True)
    except: send_crash_reports = True
        
    if send_crash_reports:
        try:
            fields["ETS2LA Version"] = variables.METADATA["version"]
            fields["ETS2LA Language"] = settings.Get("global", "language", "English")

            username = GetUsername()
            
            fields["User"] = username

            jsonData = {
                "timestamp": int(time.time()),
                "source": source,
                "source_description": source_description,
                "fields": fields
            }
            
            url = 'https://api.ets2la.com/crash/report'
            headers = {'Content-Type': 'application/json'}
            try:
                response = requests.post(url, headers=headers, json=jsonData)
            except:
                print("Could not connect to server to send crash report.")
                return False
            return response.status_code == 200
        except:
            import traceback
            # traceback.print_exc()
            # print("Crash report sending failed.")
            return False
    else:
        print("Crash detected, but crash reporting is disabled.")
        return False
    
def GetUsername(force_refresh = False):
    if username == "unknown":
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
        
    return "anonymous"    

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
        
last_unique_check = 0
last_unique_data = None
def GetUniqueUsers(interval: Literal["1h", "6h", "12h", "24h", "1w", "1m"] = "24h"):
    global last_unique_check, last_unique_data
    if time.perf_counter() - last_unique_check < 60:
        return last_unique_data
    
    url = URL + '/tracking/users'
    try:
        r = requests.get(url)
        last_unique_data = r.json()["data"]["unique"][interval]
        last_unique_check = time.perf_counter()
        return last_unique_data
    except:
        return 0
        
last_count_check = 0
last_count_data = None
def GetUserCount():
    global last_count_check, last_count_data
    if time.perf_counter() - last_count_check < 60:
        return last_count_data
    
    url = URL + '/tracking/users'
    try:
        r = requests.get(url)
        last_count_data = r.json()["data"]["online"]
        last_count_check = time.perf_counter()
        return last_count_data
    except:
        return 0
    
last_time_check = 0
last_time_data = None
def GetUserTime():
    global last_time_check, last_time_data
    if time.perf_counter() - last_time_check < 60:
        return last_time_data
    
    user_id, _, _ = GetCredentials()
    url = URL + f'/tracking/time/{user_id}'
    try:
        r = requests.get(url)
        last_time_data = r.json()["data"]["time_used"]
        last_time_check = time.perf_counter()
        return last_time_data
    except:
        return 0