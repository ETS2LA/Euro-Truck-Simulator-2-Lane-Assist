from ETS2LA.UI import *
from Modules.TruckSimAPI.main import Module
from ETS2LA.Utils.Values.numbers import SmoothedValue
import time

tsapi = Module(None)
fps = SmoothedValue("time", 1)

class Page(ETS2LAPage):
    url = "/telemetry"
    search_term = ""
    last_render = 0
    
    def color(self, text):
        if text == "True":
            return styles.TextColor("#55ee55")
        elif text == "False":
            return styles.TextColor("#ee5555")
        elif text.replace(".", "").replace("-", "").isnumeric():
            return styles.TextColor("#bbbbff")
        elif "[" in text or "]" in text:
            return styles.TextColor("#ffbbbb")
        else:
            return styles.TextColor("#eeee55")
            
    def update_search(self, search_term):
        self.search_term = search_term
            
    def render(self):
        telemetry = tsapi.run()
        
        with Container(styles.Padding("20px") + styles.FlexVertical() + styles.Gap("20px")):
            with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-center")):
                Input(
                    default="Search",
                    changed=self.update_search
                )
                if fps.get() != 0:
                    with Container(styles.Classname("border rounded-lg bg-input/30 p-2")):
                        Text(f"{1/fps.get():.1f}", styles.Classname("text-sm font-semibold min-w-max"))
            
            if not self.search_term or self.search_term.lower() in telemetry:
                with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("p-4 border rounded-lg bg-input/10")):
                    for key, value in telemetry.items():
                        if "placeHolder" in key:
                            continue
                        
                        if type(value) == dict:
                            break
                        
                        with Container(styles.FlexHorizontal() + styles.Gap("4px") + styles.Classname("p-2 rounded-lg bg-input/30")):
                            Text(key, styles.Classname("text-sm"))
                            Text(str(value), styles.Classname("text-sm") + self.color(str(value)))
                            
            for master, data in telemetry.items():
                if type(data) != dict:
                    continue
                
                in_master = False
                if self.search_term in master:
                    in_master = True
                
                found = False
                if not in_master and self.search_term:
                    for key, value in data.items():
                        if self.search_term.lower() in key.lower():
                            found = True
                            break
                        
                if not found and not in_master:
                    continue
                
                with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("p-4 border rounded-lg bg-input/10")):
                    Text(master, styles.Classname("text-lg font-semibold"))
                    Space()
                    for key, value in data.items():
                        if "placeHolder" in key:
                            continue
                        
                        if not in_master and self.search_term and self.search_term.lower() not in key.lower():
                            continue
                        
                        with Container(styles.FlexHorizontal() + styles.Gap("4px") + styles.Classname("p-2 rounded-lg bg-input/30")):
                            Text(key, styles.Classname("text-sm"))
                            value = value
                            if type(value) == float:
                                value = round(value, 2)
                                value = str(value).ljust(4, "0")
                                
                            Text(str(value), styles.Classname("text-sm") + self.color(str(value)))
                            
        cur_time = time.perf_counter()
        fps.smooth(cur_time - self.last_render)
        self.last_render = cur_time