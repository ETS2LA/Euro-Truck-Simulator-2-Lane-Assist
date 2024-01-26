"""This file is used to communicate with the main app server. The file will not be used without consent from the user."""
import requests
import json

def SendCrashReport(type:str, message:str, additional=None):
    jsonData = {
        "type": type,
        "message": message,
        "additional": additional
    }
    url = 'https://crash.tumppi066.fi/crash'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(jsonData)
    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    return response.status_code == 200
