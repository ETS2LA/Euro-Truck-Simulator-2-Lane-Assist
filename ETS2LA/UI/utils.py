from typing import Literal
import requests

def SendPopup(message: str, type: Literal["info", "warning", "error", "success"] = "info"):
    """ONLY USE THIS OUTSIDE OF PLUGINS. Use self.notify() inside plugins instead!

    :param str message: The message of the popup.
    :param Literal["info", "warning", "error", "success"] type: The popup type, defaults to "info"
    """
    try:
        requests.post("http://localhost:37520/api/popup", json={"text": message, "type": type}, timeout=0.1)
    except:
        return False
    
    return True