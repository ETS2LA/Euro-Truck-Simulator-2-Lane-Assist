from ETS2LA.Utils.translator import _
from ETS2LA.Handlers import plugins
from ETS2LA.UI import *
import multiprocessing
import pywintypes
import threading
import win32pdh
import logging
import psutil
import time
import os

# Has to be a class to not lag the main
# process when collecting data.
# (multiprocessed)
class PerformanceMetrics:
    output: multiprocessing.Queue
    def __init__(self, output: multiprocessing.Queue):
        self.output = output
        threading.Thread(target=self.cpu_thread, daemon=True).start()
        threading.Thread(target=self.ram_thread, daemon=True).start()
        while True:
            time.sleep(1) # Keep the process alive
        
    def cpu_thread(self):
        use_fallback = os.name != 'nt' # Linux automatically uses the fallback
        while True:
            if not use_fallback:
                try:
                    path = r"\Processor(_Total)\% Processor Time"
                    hq = win32pdh.OpenQuery()
                    hc = win32pdh.AddCounter(hq, path)

                    win32pdh.CollectQueryData(hq)
                    time.sleep(1)
                    win32pdh.CollectQueryData(hq)
                    
                    # Get formatted value
                    _, val = win32pdh.GetFormattedCounterValue(hc, win32pdh.PDH_FMT_DOUBLE)
                except pywintypes.error:
                    time.sleep(1)
                    logging.warning("Failed to get CPU usage from Windows Performance Counters. Falling back to psutil.")
                    use_fallback = True # Use the fallback if Windows says that AddCounter doesn't exist
                    continue
            else:
                val = psutil.cpu_percent(interval=1) # Can be a little less accurate

            self.output.put_nowait({
                "cpu" : round(val, 1)
            })
            
    def get_python_mem(self) -> float:
        total = 0
        for proc in psutil.process_iter():
            try:
                time.sleep(0.01)
                if "python" in proc.name().lower(): # backend
                    total += proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
        return total
    
    def ram_thread(self):
        last_ram = psutil.virtual_memory().percent
        last_ets2la_ram = self.get_python_mem()
        last_update = time.time()
        while True:
            time.sleep(1)
            
            if time.time() - last_update > 10:
                last_ram = psutil.virtual_memory().percent
                last_ets2la_ram = self.get_python_mem()
                last_update = time.time()
            
            self.output.put_nowait({
                "ram" : last_ram,
                "ets2la_ram" : round(last_ets2la_ram, 1)
            })

class Page(ETS2LAPage):
    url = "/performance"
    refresh_rate = 1
    
    first_times = {}
    
    cpu_usage : list[float] = []
    ram_usage : list[float] = []
    ets2la_mem_usage : list[float] = []

    def __init__(self):
        super().__init__()
        threading.Thread(target=self.performance_thread, daemon=True).start()

    def performance_thread(self):
        input = multiprocessing.Queue()
        self.metrics_process = multiprocessing.Process(
            target=PerformanceMetrics, args=(input,),
            daemon=True
        )
        self.metrics_process.start()
        while True:
            try:
                data = input.get(timeout=0.5)
                if "cpu" in data:
                    self.cpu_usage.append(data["cpu"])
                    if len(self.cpu_usage) > 60:
                        self.cpu_usage.pop(0)
                if "ram" in data:
                    self.ram_usage.append(data["ram"])
                    self.ets2la_mem_usage.append(data["ets2la_ram"])
                    if len(self.ram_usage) > 60:
                        self.ram_usage.pop(0)
                        self.ets2la_mem_usage.pop(0)
            except multiprocessing.queues.Empty:
                time.sleep(0.5)
                continue

    def format_frametime(self, frametime: float, max_fps: float) -> str:
        """Format the frametime in milliseconds."""
        fps = 1000 / frametime if frametime > 0 else 0
    
        if frametime < 10:
            formatted_time = f"{frametime:.2f}"
        elif frametime < 100:
            formatted_time = f"{frametime:.1f}"
        else:
            formatted_time = f"{frametime:.0f}"
        
        return f"{fps:.0f} / {max_fps:.0f} FPS ({formatted_time} ms)"

    def format_frametimes_to_graph_data(self, frametimes: list[float]):
        if not frametimes:
            return []
            
        graph_data = []
        for i, frametime in enumerate(frametimes):
            fps = 1000 / frametime if frametime > 0 else 0
            graph_data.append({
                "time": i,
                "fps": fps
            })
        
        return graph_data

    def render(self):
        start_time = time.perf_counter()
        with Container(styles.FlexVertical() + styles.Classname("p-4")):
            with Tabs():
                with Tab(_("System")):
                    if len(self.cpu_usage) < 60 or len(self.ram_usage) < 60:
                        with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full")):
                            Text(_("Data is still being collected, please wait a few seconds for the graphs to stabilize."), styles.Description())
                        Space(styles.Height("24px"))
                        
                    with Container(styles.FlexHorizontal() + styles.Classname("gap-6")):
                        with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full h-full relative") + styles.Height("320px")):
                            with Container(styles.FlexHorizontal() + styles.Classname("z-10 w-max")):
                                Text(_("CPU Usage"))
                                if self.cpu_usage:
                                    Text(f"{round(self.cpu_usage[-1])}%", styles.Description())
                                   
                            with Container(styles.Classname("absolute bottom-0 left-0 right-0")): 
                                Graph(
                                    data=[{"time": i, "cpu": value} for i, value in enumerate(self.cpu_usage)],
                                    config={"cpu": {"label": _("CPU Usage ")}},
                                    x=GraphAxisOptions("time"),
                                    y=GraphAxisOptions("cpu", max=100, min=0),
                                    style=styles.MaxHeight("270px"),
                                )
                                
                        with Container(styles.FlexVertical() + styles.Classname("relative border rounded-md p-4 w-full h-full") + styles.Height("320px")):
                            with Container(styles.FlexHorizontal() + styles.Classname("z-10 w-max")):
                                Text(_("RAM Usage"))
                                if self.ram_usage:
                                    Text(f"{round(self.ram_usage[-1])}%", styles.Description())
                                    
                            with Container(styles.Classname("absolute bottom-0 left-0 right-0")): 
                                Graph(
                                    data=[{"time": i, "ram": value, "ets2la_ram": self.ets2la_mem_usage[i] if len(self.ets2la_mem_usage) > i else 0} for i, value in enumerate(self.ram_usage)],
                                    config={"ram": {"label": _("RAM Usage ")}, "ets2la_ram": {"label": _("ETS2LA RAM Usage  ")}},
                                    x=GraphAxisOptions("time"),
                                    y=[GraphAxisOptions("ram", max=100, min=0), GraphAxisOptions("ets2la_ram", max=100, min=0, color="#395C5B")],
                                    style=styles.MaxHeight("270px"),
                                )

                with Tab(_("Plugins")):
                    with Container(styles.FlexVertical() + styles.Classname("gap-6")):
                        running_plugins = [plugin for plugin in plugins.plugins if plugin.running]
                        if not running_plugins:
                            Text(_("No plugins are currently running."), styles.Description() + styles.Classname("font-bold"))

                        for plugin in running_plugins:
                            try:
                                if not plugin.frametimes:   
                                    continue
                                
                                if plugin.description.id not in self.first_times:
                                    self.first_times[plugin.description.id] = plugin.frametimes[0]
                                
                                with Container(styles.FlexVertical() + styles.Classname("relative border rounded-md p-4") + styles.Height("200px")):
                                    with Container(styles.FlexHorizontal() + styles.Classname("z-10 w-max")):
                                        Text(plugin.description.name)
                                        with Tooltip() as t:
                                            with t.trigger as tr:
                                                tr.style = styles.Classname("w-max")
                                                Text(self.format_frametime(plugin.frametimes[-1], plugin.description.fps_cap), styles.Description())
                                            with t.content:
                                                try:
                                                    average = sum(plugin.frametimes) / len(plugin.frametimes) if plugin.frametimes else 0
                                                    maximum = max(plugin.frametimes) if plugin.frametimes else 0
                                                    minimum = min(plugin.frametimes) if plugin.frametimes else 0
                                                    
                                                    # Stutter is the percentage of the max fps between the minimum and maximum frametimes
                                                    max_fps = 1000 / minimum if minimum > 0 else 0
                                                    min_fps = 1000 / maximum if maximum > 0 else 0
                                                    stutter = ((max_fps - min_fps) / max_fps) * 100 if max_fps > 0 else 0
                                                
                                                    Text(f"Avg: {round(1000/average, 2) if average > 0 else 0} FPS", styles.Description())
                                                    Text(f"Min: {round(1000/maximum, 2) if maximum > 0 else 0} FPS", styles.Description())
                                                    Text(f"Max: {round(1000/minimum, 2) if minimum > 0 else 0} FPS", styles.Description())
                                                    Space(styles.Height("4px"))
                                                    Text(f"-> Stutter: {stutter:.2f}%")
                                                except:
                                                    pass
                                    
                                    if plugin.frametimes[0] == self.first_times[plugin.description.id]:
                                        Text(_("Warning: Graph is still gathering data, please wait 60 seconds for it to stabilize."), styles.Description() + styles.Classname("text-xs"))

                                    graph_data = self.format_frametimes_to_graph_data(plugin.frametimes)
                                    graph_config = {
                                        "fps": {
                                            "label": "FPS ",
                                        }
                                    }
                                    with Container(styles.Classname("absolute bottom-0 left-0 right-0")): 
                                        Graph(
                                            data=graph_data,
                                            config=graph_config,
                                            x=GraphAxisOptions("time"),
                                            y=GraphAxisOptions("fps", max=plugin.description.fps_cap, min=0),
                                            type="area",
                                            style=styles.MaxHeight("150px")
                                        )
                            except:
                                Text(_("Failed to render plugin {plugin_name}.", plugin_name=plugin.description.name), styles.Description() + styles.Classname("text-red-500"))

            Space(styles.Height("8px"))
            with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full")):
                Text(_("All displayed data is averaged over a second."), styles.Description())
                Text(_("This page took {time:.2f} ms to render.").format(time=(time.perf_counter() - start_time) * 1000), styles.Description())