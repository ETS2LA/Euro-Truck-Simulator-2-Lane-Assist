from ETS2LA.UI import *

from ETS2LA.networking.webserver import mainThreadQueue
from ETS2LA.utils.git import CheckForUpdate, Update

from datetime import datetime
import time

last_update_check = 0
class Page(ETS2LAPage):
    dynamic = True
    url = "/updater"
    settings_target = "updater"
    
    def update(self, *args, **kwargs):
        mainThreadQueue.append([Update, [], {}])
    
    def render(self):
        global last_update_check
        if time.time() - last_update_check > 60:
            last_update_check = time.time()
            updates = CheckForUpdate()
        else:
            updates = []
            
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
                                    Label(update["message"], size="sm", weight="semibold")
                                if update["description"] != "":
                                    Markdown(update["description"])
                                local_time = datetime.fromtimestamp(update["time"]).strftime("%Y-%m-%d %H:%M:%S")
                                Description(local_time, size="xs")
                
        return RenderUI()