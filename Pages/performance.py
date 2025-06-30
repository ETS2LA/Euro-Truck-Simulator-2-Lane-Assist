from ETS2LA.Handlers import plugins
from ETS2LA.UI import *
import threading
import win32pdh
import psutil
import time

class Page(ETS2LAPage):
    url = "/performance"
    refresh_rate = 1
    
    first_times = {}
    
    cpu_usage = []
    ram_usage = []
    
    def cpu_thread(self):
        while True:
            # This is some windows black magic... don't ask
            path = r"\Processor(_Total)\% Processor Time"
            hq = win32pdh.OpenQuery()
            hc = win32pdh.AddCounter(hq, path)
            
            win32pdh.CollectQueryData(hq)
            time.sleep(1)
            win32pdh.CollectQueryData(hq)
            
            # Get formatted value
            _, val = win32pdh.GetFormattedCounterValue(hc, win32pdh.PDH_FMT_DOUBLE)
            self.cpu_usage.append(round(val, 1))
            
            if len(self.cpu_usage) > 60:
                self.cpu_usage.pop(0)
    
    def ram_thread(self):
        while True:
            time.sleep(1)
            self.ram_usage.append(psutil.virtual_memory().percent)
            if len(self.ram_usage) > 60:
                self.ram_usage.pop(0)

    def __init__(self):
        super().__init__()
        threading.Thread(target=self.cpu_thread, daemon=True).start()
        threading.Thread(target=self.ram_thread, daemon=True).start()

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

    def list_to_data(self, data: list[float], name:str = "value") -> list[dict]:
        """Convert a list of floats to a list of dictionaries for graphing."""
        return [{"time": i, name: value} for i, value in enumerate(data)]

    def render(self):
        start_time = time.perf_counter()
        with Container(styles.FlexVertical() + styles.Classname("p-4")):
            with Tabs():
                with Tab("System"):
                    if len(self.cpu_usage) < 60 or len(self.ram_usage) < 60:
                        with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full")):
                            Text("Data is still being collected, please wait a few seconds for the graphs to stabilize.", styles.Description())
                        Space(styles.Height("24px"))
                        
                    with Container(styles.FlexHorizontal() + styles.Classname("gap-6")):
                        with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full h-full")):
                            with Container(styles.FlexHorizontal()):
                                Text("CPU Usage")
                                if self.cpu_usage:
                                    Text(f"{round(self.cpu_usage[-1])}%", styles.Description())
                            Graph(
                                data=self.list_to_data(self.cpu_usage, name="cpu"),
                                config={"cpu": {"label": "CPU Usage "}},
                                x=GraphAxisOptions("time"),
                                y=GraphAxisOptions("cpu", max=100, min=0),
                            )
                        with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full h-full")):
                            with Container(styles.FlexHorizontal()):
                                Text("RAM Usage")
                                if self.ram_usage:
                                    Text(f"{round(self.ram_usage[-1])}%", styles.Description())
                            Graph(
                                data=self.list_to_data(self.ram_usage, name="ram"),
                                config={"ram": {"label": "RAM Usage "}},
                                x=GraphAxisOptions("time"),
                                y=GraphAxisOptions("ram", max=100, min=0),
                            )
                        
                with Tab("Plugins"):
                    with Container(styles.FlexVertical() + styles.Classname("gap-6")):
                        running_plugins = [plugin for plugin in plugins.plugins if plugin.running]
                        if not running_plugins:
                            Text("No plugins are currently running.", styles.Description() + styles.Classname("font-bold"))
                        
                        for plugin in running_plugins:
                            try:
                                if not plugin.frametimes:   
                                    continue
                                
                                if plugin.description.name not in self.first_times:
                                    self.first_times[plugin.description.name] = plugin.frametimes[0]
                                
                                with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4")):
                                    with Container(styles.FlexHorizontal()):
                                        Text(plugin.description.name)
                                        Text(self.format_frametime(plugin.frametimes[-1], plugin.description.fps_cap), styles.Description())
                                    
                                    if plugin.frametimes[0] == self.first_times[plugin.description.name]:
                                        Text("Warning: Graph is still gathering data, please wait 60 seconds for it to stabilize.", styles.Description() + styles.Classname("text-xs"))

                                    graph_data = self.format_frametimes_to_graph_data(plugin.frametimes)
                                    graph_config = {
                                        "fps": {
                                            "label": "FPS ",
                                        }
                                    }
                                    Graph(
                                        data=graph_data,
                                        config=graph_config,
                                        x=GraphAxisOptions("time"),
                                        y=GraphAxisOptions("fps", max=plugin.description.fps_cap * 1.05, min=0),
                                        type="area",
                                        style=styles.MaxHeight("200px")
                                    )
                            except:
                                Text(f"Failed to render plugin {plugin.description.name}.", styles.Description() + styles.Classname("text-red-500"))

            Space(styles.Height("8px"))
            with Container(styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full")):
                Text("All displayed data is averaged over a second.", styles.Description())
                Text(f"This page took {(time.perf_counter() - start_time) * 1000:.2f} ms to render.", styles.Description())