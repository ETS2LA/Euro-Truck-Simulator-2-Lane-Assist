from ETS2LA.UI import *

from ETS2LA.Networking.Servers.webserver import mainThreadQueue
from ETS2LA.Utils.version import CheckForUpdate, Update

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
        
        if time.perf_counter() - last_update_check > 10:
            last_update_check = time.perf_counter()
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
                    Button("Update Anyway", self.update, variant="outline")
                else:
                    reversed_updates = updates[::-1]
                    Button("Update", self.update, variant="outline")
                    Space(8)
                    Description(f"There are {len(updates)} update(s) available, here's a list from oldest to newest:")
                    Space(8)
                    with Group("vertical", classname="gap-3"):
                        current_day = None
                        for update in reversed_updates:
                            local_time = datetime.fromtimestamp(update["time"]).strftime("%Y-%m-%d %H:%M:%S")
                            if local_time.split(" ")[0] != current_day:
                                current_day = local_time.split(" ")[0]
                                Space(20)
                                with Group("horizontal", classname="flex items-center p-0 gap-0"):
                                    with Group("horizontal", classname="border-b p-0 gap-0 w-full"):
                                        ...
                                    with Group("vertical", classname="items-center p-0 gap-0 w-full"):
                                        Description(local_time.split(" ")[0], classname="text-xs font-bold")
                                    with Group("horizontal", classname="border-b p-0 gap-0 w-full"):
                                        ...
                                Space(20)
                            with Group("vertical", border=True, classname="p-3 flex flex-col gap-6"):
                                with Group("horizontal", classname="flex w-full gap-2 items-center"):
                                    Description(update["author"], classname="text-xs")
                                    with Group("horizontal", classname="flex justify-between p-0 gap-0 w-full"):
                                        Label(update["message"], classname="text-sm font-semibold")
                                        Label("View Changes", url=update["url"], classname="text-xs font-light pr-1")
                                if update["description"] != "":
                                    Markdown(update["description"])
                                Description(local_time + f"  -  {self.time_since(update['time'])}", classname="text-xs")
                
        return RenderUI()