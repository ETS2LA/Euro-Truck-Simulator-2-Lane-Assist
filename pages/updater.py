from ETS2LA.backend import settings
from ETS2LA.UI import *

from ETS2LA.networking.webserver import mainThreadQueue
from ETS2LA.utils.git import CheckForUpdate, Update

import time

class Page(ETS2LAPage):
    dynamic = True
    url = "/updater"
    settings_target = "updater"
    
    def update(self, *args, **kwargs):
        mainThreadQueue.append([Update, [], {}])
    
    def render(self):
        updates = CheckForUpdate()
        with Geist():
            with Padding(24):
                if updates == []:
                    Description("You have a local commit that is waiting to be pushed.")
                elif not updates:
                    Description("No updates available.")
                else:
                    reversed_updates = updates[::-1]
                    Button("Update", "", self.update, border=False)
                    Space(8)
                    Description(f"There are {len(updates)} update(s) available, here's a list from oldest to newest:")
                    Space(6)
                    with Group("vertical", gap=8):
                        for update in reversed_updates:
                            with Group("vertical", border=True):
                                with Group("horizontal"):
                                    Description(update["author"], size="xs")
                                    Label(update["message"], size="sm", weight="semibold")
                                Label(update["description"])
                                Description(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(update["time"])), size="xs")
                
        
        return RenderUI()