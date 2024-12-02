from ETS2LA.UI import *

from ETS2LA.networking.webserver import mainThreadQueue
from ETS2LA.utils.git import CheckForUpdate, Update

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
                if updates == []:
                    Description("You have a local commit that is waiting to be pushed.")
                elif not updates:
                    Description("No updates available. (It might take up to a minute for the page to update after a new commit)")
                    Space(8)
                    Button("Update Anyway", "", self.update, border=False)
                else:
                    reversed_updates = updates[::-1]
                    Button("Update", "", self.update, border=False)
                    Space(8)
                    Description(f"There are {len(updates)} update(s) available, here's a list from oldest to newest:")
                    Space(6)
                    with Group("vertical", gap=8):
                        for update in reversed_updates:
                            with Group("vertical", border=True):
                                with Group("horizontal", padding=0):
                                    Description(update["author"], size="xs")
                                    with Group("horizontal", padding=0, gap=0, classname="flex justify-between"):
                                        Label(update["message"], size="sm", weight="semibold")
                                        Link("View Changes", update["url"], size="xs", weight="light")
                                if update["description"] != "":
                                    Markdown(update["description"])
                                local_time = datetime.fromtimestamp(update["time"]).strftime("%Y-%m-%d %H:%M:%S")
                                Description(local_time + f"  -  {self.time_since(update["time"])}", size="xs")
                
        return RenderUI()