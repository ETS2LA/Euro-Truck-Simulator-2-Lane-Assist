from ETS2LA.UI import *

from ETS2LA.Utils.version import GetHistory

from datetime import datetime
import logging
import time
import os

ran_fetch = False
last_updates = []
last_update_check = 0

class Page(ETS2LAPage):
    dynamic = True
    url = "/changelog"
    settings_target = "changelog" 
        
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
        global last_update_check, last_updates, ran_fetch
        
        if not ran_fetch:
            logging.info("Fetching changelog and possible changes.")
            os.system("git fetch --prune --quiet")
            logging.info("Changelog fetched.")
            ran_fetch = True
        
        if time.perf_counter() - last_update_check > 10:
            last_update_check = time.perf_counter()
            updates = GetHistory()
            last_updates = updates
        else:
            updates = last_updates

        with Container(styles.FlexVertical() + styles.Padding("24px") + styles.Gap("24px") + styles.Margin("60px")):
            current_day = None
            for update in updates[:20]:
                
                local_time = datetime.fromtimestamp(update["time"]).strftime("%Y-%m-%d %H:%M:%S")
                if local_time.split(" ")[0] != current_day:
                    current_day = local_time.split(" ")[0]
                    border_bottom = styles.Classname("border-b w-full")
                    with Container(styles.FlexHorizontal() + styles.Padding("0")+ styles.Classname("justify-between items-center")):
                        with Container(styles.FlexHorizontal() + styles.Padding("0") + border_bottom):
                            ...
                        with Container(styles.FlexVertical() + styles.Padding("0")):
                            Text(local_time.split(" ")[0], styles.Classname("text-xs font-bold min-w-max") + styles.Description())
                        with Container(styles.FlexHorizontal() + styles.Padding("0") + border_bottom):
                            ...
                            
                with Container(styles.FlexVertical() + styles.Classname("shadow-md bg-input/10 border rounded-md p-4")):
                    with Container(styles.FlexHorizontal() + styles.Padding("0") + styles.Classname("items-center")):
                        Text(update["author"], styles.Description() + styles.Classname("text-xs"))
                        with Container(styles.FlexHorizontal() + styles.Padding("0") + styles.Classname("flex justify-between w-full")):
                            Text(update["message"], styles.Classname("text-sm font-semibold"))
                            Link("View Changes", update["url"], styles.Classname("text-xs font-light"))
                              
                    if update["description"] != "":
                        Markdown(update["description"])
                        
                    Space(styles.Height("4px"))
                    Text(local_time + f"  -  {self.time_since(update['time'])}  -  {update['hash'][:9]}", styles.Description() + styles.Classname("text-xs"))
                    
            Text("Only the last 20 updates are shown. For more, please check the repository.", styles.Description() + styles.Classname("text-xs"))