from ETS2LA.backend import settings
from ETS2LA.UI import *
import psutil

class Page(ETS2LAPage):
    dynamic = False
    url = "/stats"
    settings_target = "stats"
    
    def get_all_python_process_mem_usage_percent(self):
        total = 0
        for proc in psutil.process_iter():
            try:
                if "python" in proc.name().lower():
                    total += proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return total
    
    def render(self):
        with Padding(0):
            with Geist():
                with Group("horizontal", gap=0, padding=4, classname="flex justify-between w-full"):
                    Description(f"RAM: {round(psutil.virtual_memory().percent):02}%", size="xs")
                    Description(f"Python: {round(self.get_all_python_process_mem_usage_percent()):02}%", size="xs")
                    
        return RenderUI()