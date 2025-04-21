from ETS2LA.UI import *

from ETS2LA.Networking.Servers.webserver import mainThreadQueue
from ETS2LA.Utils.version import CheckForUpdate, Update
from ETS2LA.Utils.umami import TriggerEvent

from datetime import datetime
import time

last_update_check = 0
last_updates = []
class Page(ETS2LAPage):
    dynamic = True
    url = "/updater"
    settings_target = "updater" 
    
    def update(self, *args, **kwargs):
        try:
            TriggerEvent("Update App")
        except:
            pass
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
            
        with Container(styles.FlexVertical() + styles.Padding("24px") + styles.Gap("24px") + styles.Margin("30px 60px 60px 60px")):
            if updates == []:
                Text("You have a local commit that is waiting to be pushed.", styles.Description() + styles.Classname("text-xs"))
            elif not updates:
                Text("No updates available. (It might take up to a minute for the page to update after a new commit)", styles.Description())
                with Button(self.update):
                    Text("Update Anyway", styles.Classname("font-semibold"))
            else:
                with Button(self.update):
                    Text(f"Restart and apply {len(updates)} update(s)", styles.Classname("font-semibold"))
                Space(styles.Height("20px"))
                
                updates = updates[::-1]
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
            
        # RefreshRate(1)
        # with Geist():
        #     with Padding(24):
        #         Space(20)
        #         if updates == []:
        #             Description("You have a local commit that is waiting to be pushed.")
        #         elif not updates:
        #             Description("No updates available. (It might take up to a minute for the page to update after a new commit)")
        #             Space(8)
        #             Button("Update Anyway", "", self.update, border=False)
        #         else:
        #             reversed_updates = updates[::-1]
        #             Button(f"Restart and apply {len(updates)} update(s)", "", self.update, border=False)
        #             with Group("vertical", gap=24):
        #                 current_day = None
        #                 for update in reversed_updates:
        #                     try:
        #                         local_time = datetime.fromtimestamp(update["time"]).strftime("%Y-%m-%d %H:%M:%S")
        #                         if local_time.split(" ")[0] != current_day:
        #                             current_day = local_time.split(" ")[0]
        #                             Space(5)
        #                             with Group("horizontal", padding=0, classname="flex items-center", gap=0):
        #                                 with Group("horizontal", padding=0, gap=0, classname="border-b"):
        #                                     ...
        #                                 with Group("vertical", padding=0, gap=0, classname="items-center"):
        #                                     Description(local_time.split(" ")[0], size="xs", weight="bold")
        #                                 with Group("horizontal", padding=0, gap=0, classname="border-b"):
        #                                     ...
        #                             Space(5)
        #                             
        #                         with Group("vertical", border=True, classname="shadow-md bg-input/10"):
        #                             with Group("horizontal", padding=0, classname="items-center", gap=12):
        #                                 Description(update["author"], size="xs")
        #                                 with Group("horizontal", padding=0, gap=0, classname="flex justify-between"):
        #                                     Label(update["message"], size="sm", weight="semibold")
        #                                     Link("View Changes", update["url"], size="xs", weight="light")
        #                             if update["description"] != "":
        #                                 Markdown(update["description"])
        #                             Description(local_time + f"  -  {self.time_since(update['time'])}  -  {update['hash'][:9]}", size="xs")
        #                     except:
        #                         import traceback
        #                         Description(f"An error occurred while rendering this update.\n{traceback.format_exc()}", size="xs")
        #         
        # return RenderUI()