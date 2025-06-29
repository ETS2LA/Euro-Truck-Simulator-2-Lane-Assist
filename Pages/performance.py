from ETS2LA.Handlers import plugins
from ETS2LA.UI import *
import time

class Page(ETS2LAPage):
    url = "/performance"
    refresh_rate = 1
    
    first_times = {}

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
                            x_key="time",
                            y_key="fps",
                            type="area",
                            style=styles.MaxHeight("200px")
                        )
                except:
                    Text(f"Failed to render plugin {plugin.description.name}.", styles.Description() + styles.Classname("text-red-500"))
        
            Text("All displayed data is averaged over the last second.", styles.Description() + styles.Classname("mt-2"))
            Text(f"This page took {(time.perf_counter() - start_time) * 1000:.2f} ms to render.", styles.Description())