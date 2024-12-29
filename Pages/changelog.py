from ETS2LA.Utils.version import GetHistory
from ETS2LA.UI import *

from datetime import datetime
import time

last_update_check = 0
last_updates = []
class Page(ETS2LAPage):
    dynamic = True
    url = "/changelog"
    settings_target = "changelog" 
        
    def time_since(self, target_time):
        diff = time.perf_counter() - target_time
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
        
        if time.perf_counter() - last_update_check > 10:
            last_update_check = time.perf_counter()
            updates = GetHistory()
            last_updates = updates
        else:
            updates = last_updates

        with Geist():
            with Padding(20):
                Label("Changelog", classname_preset=TitleClassname)
                Label("This page will shwo the 100 latest commits, currently under construction", classname_preset=DescriptionClassname)

        return RenderUI()