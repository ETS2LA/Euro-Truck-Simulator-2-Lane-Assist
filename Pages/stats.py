from ETS2LA.Handlers import plugins
from ETS2LA.UI import *
import psutil

class Page(ETS2LAPage):

    url = "/stats"
    refresh_rate = 5
    
    def get_all_python_process_mem_usage_percent(self):
        total = 0
        python = 0
        node = 0
        for proc in psutil.process_iter():
            try:
                if "python" in proc.name().lower(): # backend
                    total += proc.memory_percent()
                    python += proc.memory_percent()
                if "node" in proc.name().lower():   # frontend
                    total += proc.memory_percent()
                    node += proc.memory_percent()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return total, [python, node]
    
    def get_all_plugin_mem_usage_percent(self):
        by_plugin = {}
        pids = plugins.get_all_process_pids()
        for key, value in pids.items():
            by_plugin[key] = 0
            try:
                proc = psutil.Process(value)
                by_plugin[key] = proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return by_plugin
    
    def render(self):
        with Container(styles.FlexHorizontal() + 
                       styles.Classname("w-full border rounded-lg justify-center") + 
                       styles.Height("2.2rem") +
                       styles.Padding("0 4px 0 0") +
                       styles.Gap("4px")):
            
            with TooltipContent(id="ram_tooltip"):
                Markdown(f"```\n{round(psutil.virtual_memory().used / 1024 ** 3, 1)} GB / {round(psutil.virtual_memory().total / 1024 ** 3, 1)} GB\n```")
            
            with Tooltip(content="ram_tooltip"):
                Text(f"RAM: {round(psutil.virtual_memory().percent, 1)}%", style=styles.Description() + styles.Classname("text-xs"))
            
            process_mem, per_type = self.get_all_python_process_mem_usage_percent()
            tooltip_text = f"```\n┏ Python: {round(per_type[0] * psutil.virtual_memory().total / 100 / 1024 ** 3,1)} GB\n"
            try:
                for key, value in self.get_all_plugin_mem_usage_percent().items():
                    tooltip_text += f"┃  {key}: {round(value * psutil.virtual_memory().total / 100 / 1024 ** 3,1)} GB\n"
            except: pass
            tooltip_text += "┃\n"
            tooltip_text += f"┣ Node: {round(per_type[1] * psutil.virtual_memory().total / 100 / 1024 ** 3,1)} GB\n"
            tooltip_text += "┃\n"
            tooltip_text += f"┗ Total: {round(process_mem * psutil.virtual_memory().total / 100 / 1024 ** 3,1)} GB\n```"
            
            with TooltipContent(id="process_tooltip"):
                Markdown(tooltip_text)
            
            with Tooltip(content="process_tooltip"):
                Text(f"<- {round(process_mem, 1)}% ETS2LA", style=styles.Description() + styles.Classname("text-xs"))