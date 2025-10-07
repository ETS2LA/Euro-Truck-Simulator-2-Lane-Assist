from ETS2LA.Settings import GlobalSettings
import ETS2LA.variables as variables
from typing import Literal
import requests
import logging
import uuid
import time

URL = "https://api.ets2la.com"
user_id = None
token = None
username = "unknown"
settings = GlobalSettings()


def SendFeedback(message: str, username: str, fields: dict[str, str] = None):
    """Will send a feedback message to the main application server. This will then be forwarded to the developers on discord.

    Args:
        message (str): The feedback message.
        username (str): The username of the user sending the feedback (e.g. Discord username or email address).
        fields (dict[str, str], optional): Additional fields to include in the feedback. Defaults to an empty dict. Key is field name, value is text.

    Returns:
        success (bool): False if not successful, True if successful

    """
    if fields is None:
        fields = {}

    if message.strip() == "":
        return False

    if username.strip() == "":
        username = "anonymous"

    try:
        fields["ETS2LA Version"] = variables.METADATA["version"]
        fields["ETS2LA Language"] = settings.language

        jsonData = {
            "timestamp": int(time.time()),
            "user": username,
            "message": message,
            "fields": fields,
        }

        url = "https://api.ets2la.com/feedback"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, json=jsonData)
        except Exception:
            print("Could not connect to server to send feedback.")
            return False

        return response.status_code == 200
    except Exception:
        import traceback

        traceback.print_exc()
        print("Feedback sending failed.")
        return False


def SendCrashReport(
    source: str, source_description: str, fields: dict[str, str] = None
):
    """Will send a crash report to the main application server. This will then be forwarded to the developers on discord.

    Args:
        source (str): The source of the crash report (e.g. "Backend", "AR Plugin", etc.)
        source_description (str): A description of the source (e.g. "This crash report occured in the main loop of the AR Plugin")
        fields (dict[str, str], optional): Additional fields to include in the crash report. Defaults to an empty dict. Key is field name, value is text.

    Returns:
        success (bool): False if not successful, True if successful

    """
    if fields is None:
        fields = {}

    if source_description.strip() == "" or source.strip() == "":
        return False

    # Don't spam in dev mode.
    if variables.DEVELOPMENT_MODE:
        return False

    try:
        send_crash_reports = settings.send_crash_reports
    except Exception:
        send_crash_reports = True

    if send_crash_reports:
        try:
            fields["ETS2LA Version"] = variables.METADATA["version"]
            fields["ETS2LA Language"] = settings.language

            username = GetUsername()

            fields["User"] = username

            jsonData = {
                "timestamp": int(time.time()),
                "source": source,
                "source_description": source_description,
                "fields": fields,
            }

            url = "https://api.ets2la.com/crash/report"
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(url, headers=headers, json=jsonData)
            except Exception:
                print("Could not connect to server to send crash report.")
                return False
            return response.status_code == 200
        except Exception:
            # traceback.print_exc()
            # print("Crash report sending failed.")
            return False
    else:
        print("Crash detected, but crash reporting is disabled.")
        return False


def GetUsername(force_refresh=False):
    if username == "unknown" or force_refresh:
        user_id, token, success = GetCredentials()
        if success:
            url = URL + f"/user/{user_id}"
            headers = {"Authorization": f"Bearer {token}"}
            try:
                r = requests.get(url, headers=headers, timeout=5)
                return r.json()["data"]["username"]
            except Exception:
                logging.warning(
                    "Failed to get username, check your internet connection or login again to refresh your token."
                )
        else:
            logging.warning("Your token has expired, please log in again.")
            settings.token = None
            settings.user_id = None

    return "anonymous"


def GetCredentials():
    global user_id, token
    if not user_id:
        user_id = settings.user_id
        if not user_id:
            user_id = str(uuid.uuid4())
            settings.user_id = user_id

        token = settings.token

    return user_id, token, user_id is not None and token is not None


def Ping(data=[0]):  # noqa: B006 - This mutable default is intentional
    if time.time() - data[0] > 120:  # once every 2 minutes
        user_id, _, _ = GetCredentials()

        url = URL + f"/tracking/ping/{user_id}"
        try:
            requests.get(url)
        except Exception:
            pass

        data[0] = time.time()


last_unique_check = 0
last_unique_data = None


def GetUniqueUsers(interval: Literal["1h", "1d", "7d", "30d"] = "1d"):
    global last_unique_check, last_unique_data
    if time.perf_counter() - last_unique_check < 60:
        return last_unique_data

    url = URL + "/tracking/users"
    try:
        r = requests.get(url, timeout=10)
        last_unique_data = r.json()["data"]["unique"][interval]
        last_unique_check = time.perf_counter()
        return last_unique_data
    except Exception:
        return 0


last_count_check = 0
last_count_data = None


def GetUserCount():
    global last_count_check, last_count_data
    if time.perf_counter() - last_count_check < 60:
        return last_count_data

    url = URL + "/tracking/users"
    try:
        r = requests.get(url, timeout=10)
        last_count_data = r.json()["data"]["online"]
        last_count_check = time.perf_counter()
        return last_count_data
    except Exception:
        return 0


last_time_check = 0
last_time_data = None


def GetUserTimeInfo():
    global last_time_check, last_time_data
    if time.perf_counter() - last_time_check < 60:
        return last_time_data

    user_id, _, _ = GetCredentials()
    url = URL + f"/tracking/time/{user_id}"
    try:
        r = requests.get(url, timeout=10)
        last_time_data = r.json()["data"]
        last_time_check = time.perf_counter()
        return last_time_data
    except Exception:
        return 0
