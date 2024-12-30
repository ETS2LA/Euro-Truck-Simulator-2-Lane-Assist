from ETS2LA.Networking.Servers.webserver import mainThreadQueue
from ETS2LA.Utils.version import CheckForUpdate, Update
from ETS2LA.UI import *

from datetime import datetime
import time

last_update_check = 0
last_updates = []
class Page(ETS2LAPage):
    dynamic = True
    url = "/updater"
    settings_target = "updater" 
    
    def update(self, *args, **kwargs):
        mainThreadQueue.append([Update, [], {}])
        
    def time_since(self, target_time):
        diff = time.time() - target_time
        if diff < 60:
            if int(diff) == 1:
                return "1 second ago"
            return f"{int(diff)} seconds ago"
        elif diff < 3600:
            if int(diff / 60) == 1:
                return "1 minute ago"
            return f"{int(diff / 60)} minutes ago"
        elif diff < 86400:
            if int(diff / 3600) == 1:
                return "1 hour ago"
            return f"{int(diff / 3600)} hours ago"
        else:
            if int(diff / 86400) == 1:
                return "1 day ago"
            return f"{int(diff / 86400)} days ago"
    
    def render(self):
        global last_update_check, last_updates
        
        if time.time() - last_update_check > 10:
            last_update_check = time.time()
            updates = CheckForUpdate()
            last_updates = updates
        else:
            updates = last_updates
            
        with Geist():
            with Padding(24):
                Label("Updater", classname=TITLE_CLASSNAME)
                Label("This page will show you the updates available. Currently under construction", classname=DESCRIPTION_CLASSNAME)
                
        return RenderUI()