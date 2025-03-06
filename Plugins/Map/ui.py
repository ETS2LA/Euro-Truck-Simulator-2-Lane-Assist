from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *

import ETS2LA.Utils.settings as settings
import Plugins.Map.data as data

class SettingsMenu(ETS2LASettingsMenu):
    plugin_name = "Map"
    dynamic = True

    def get_value_from_data(self, key: str):
        if "data" not in globals():
            return "N/A"
        if key in data.__dict__:
            return data.__dict__[key]
        return "Not Found"

    def render(self):
        RefreshRate(0.25)
        Title("map.settings.1.title")
        Description("map.settings.1.description")
        Separator()
        with TabView():
            with Tab("General"):
                Switch("map.settings.2.name", "ComputeSteeringData", True, description="map.settings.2.description")
                Switch("Trailer Driving", "DriveBasedOnTrailer", True, description="Will move the 'driving point' towards the trailer at low speeds. This should fix some issues with the app cutting corners.")
                Slider("map.settings.11.name", "SteeringSmoothTime", 0.2, 0, 2, 0.1, description="map.settings.11.description")
                Switch("map.settings.6.name", "InternalVisualisation", False, description="map.settings.6.description")
                
            with Tab("Navigation"):
                Switch("Navigate on ETS2LA", "UseNavigation", True, description="Enable the automatic navigation features of ETS2LA.")
                routing_mode = settings.Get("Map", "RoutingMode")
                if not routing_mode or routing_mode not in ["shortest", "smallRoads"]:
                    routing_mode = "shortest"
                    settings.Set("Map", "RoutingMode", routing_mode)
                Selector("Routing Mode", "RoutingMode", routing_mode, ["shortest", "smallRoads"],
                        description="Choose between fastest routes (shortest) or scenic routes avoiding highways (smallRoads)")
                Slider("Auto accept threshold", "AutoAcceptThreshold", 100, 0, 200, 1, description="Automatically accept the route when the distance from the destination is below this value.", suffix="m")
                Slider("Auto deny threshold", "AutoDenyThreshold", 100, 0, 1000, 10, description="Automatically deny the route when the distance from the destination is above this value.", suffix="m")
            
            with Tab("Debug Data"):
                with EnabledLock():
                    with Group("horizontal", gap=4):
                        with Group("vertical", gap=1):
                            Label("Map data:")
                            Space(0)
                            Description(f"Current coordinates: ({self.get_value_from_data('truck_x')}, {self.get_value_from_data('truck_z')})")
                            Description(f"Current sector: ({self.get_value_from_data('current_sector_x')}, {self.get_value_from_data('current_sector_y')})")
                            Description(f"Roads in sector: {len(self.get_value_from_data('current_sector_roads'))}")
                            Description(f"Prefabs in sector: {len(self.get_value_from_data('current_sector_prefabs'))}")
                            Description(f"Models in sector: {len(self.get_value_from_data('current_sector_models'))}")
                            try: Description(f"Last data update: {time.strftime('%H:%M:%S', time.localtime(self.get_value_from_data('external_data_time')))}")
                            except: Description(f"Last data update: N/A")

                        with Group("vertical", gap=1):
                            Label("Route data:")
                            Space(0)
                            Description(f"Is steering: {self.get_value_from_data('calculate_steering')}")
                            Description(f"Route points: {len(self.get_value_from_data('route_points'))}")
                            Description(f"Route plan elements: {len(self.get_value_from_data('route_plan'))}")
                            Description(f"Routing mode: {settings.Get('Map', 'RoutingMode')}")
                            Description(f"Navigation points: {len(self.get_value_from_data('navigation_points'))}")
                            Description(f"Has destination: {self.get_value_from_data('dest_company') is not None}")

                        with Group("vertical", gap=1):
                            Label("Backend data:")
                            Space(0)
                            try: Description(f"State: {self.plugin.state.text}, {self.plugin.state.progress:.0f}")
                            except: Description("State: N/A")
                            try: Description(f"FPS: {1/self.plugin.performance[-1][1]:.0f}")
                            except: Description("FPS: Still loading...")

        return RenderUI()