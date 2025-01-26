# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import * 
from Plugins.AR.classes import *
from ETS2LA.Events.classes import FinishedJob

# General imports
import ETS2LA.Utils.settings as settings
import time

class Plugin(ETS2LAPlugin):
    fps_cap = 5
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Camera"],
        listen=["*.py", "test.json"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    steering = False
    
    @events.on("ToggleSteering")
    def on_toggle_steering(self, state):
        print("Steering toggled:", state)
        self.steering = state
    
    def imports(self):
        ...

    def run(self):
        job = FinishedJob()
        class CargoDialog(ETS2LADialog):
            def render(self):
                with Form():
                    Title("Job finished!")
                    Description(f"Here are some stats:")
                    with TabView():
                        with Tab("General"):
                            Space(1)
                            with Group("vertical"):
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Cargo")
                                        Description(job.cargo)
                                    with Group("vertical"):
                                        Label("Cargo ID")
                                        Description(job.cargo_id)
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Unit mass")
                                        Description(round(job.unit_mass))
                                    with Group("vertical"):
                                        Label("Unit count")
                                        Description(round(job.unit_count))
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Starting time")
                                        Description(round(job.starting_time))
                                    with Group("vertical"):
                                        Label("Finished time")
                                        Description(round(job.finished_time))
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Delivery time")
                                        Description(round(job.delivered_delivery_time))
                                    with Group("vertical"):
                                        Label("Autoload used")
                                        Description(str(job.delivered_autoload_used))
                                        
                        with Tab("Computed"):
                            with Group("vertical"):
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Total weight")
                                        Description(str(round(job.unit_mass * job.unit_count)) + " kg")
                                    with Group("vertical"):
                                        Label("Total revenue")
                                        Description(str(round(job.delivered_revenue)) + " €")
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Revenue per km")
                                        if job.delivered_distance_km == 0 or job.delivered_revenue == 0:
                                            Description("0 €")
                                        else:
                                            Description(str(round(job.delivered_revenue / job.delivered_distance_km, 2)) + " €")
                                    with Group("vertical"):
                                        Label("Revenue per hour")
                                        if job.finished_time == 0 or job.delivered_revenue == 0:
                                            Description("0 €")
                                        else:
                                            Description(str(round(job.delivered_revenue / (job.finished_time / 60))) + " €")
                                with Group("horizontal"):
                                    with Group("vertical"):
                                        Label("Revenue per ton")
                                        if job.unit_mass == 0 or job.unit_count == 0:
                                            Description("0 €")
                                        else:
                                            Description(str(round(job.delivered_revenue / (job.unit_mass * job.unit_count / 1000))) + " €")
                                    with Group("vertical"):
                                        Label("Average speed")
                                        if job.finished_time == 0 or job.delivered_distance_km == 0:
                                            Description("0 km/h")
                                        else:
                                            Description(str(round(job.delivered_distance_km / ((job.finished_time - job.starting_time) / 60), 1)) + " km/h")
                            
                return RenderUI()   
            
        self.dialog(CargoDialog())          
        #print(self.modules.Camera.run())
        #time.sleep(0.5)