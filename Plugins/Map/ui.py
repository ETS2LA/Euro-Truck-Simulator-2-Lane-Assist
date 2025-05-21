from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *

import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
import Plugins.Map.data as data

import json

class SettingsMenu(ETS2LAPage):
    url = "/settings/map"
    title = "Map"
    location = ETS2LAPageLocation.SETTINGS
    refresh_rate = 0.25

    def get_value_from_data(self, key: str):
        if "data" not in globals():
            return "N/A"
        if key in data.__dict__:
            return data.__dict__[key]
        return "Not Found"

    def handle_navigation(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("Map", "UseNavigation", True)
        settings.Set("Map", "UseNavigation", value)
        
    def handle_elevation(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("Map", "SendElevationData", False)
        settings.Set("Map", "SendElevationData", value)
        
    def handle_fps_notices(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("Map", "DisableFPSNotices", False)
        settings.Set("Map", "DisableFPSNotices", value)
    
    def handle_steering_data(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("Map", "ComputeSteeringData", True)
        settings.Set("Map", "ComputeSteeringData", value)
        
    def handle_drive_based_on_trailer(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("Map", "DriveBasedOnTrailer", True)
        settings.Set("Map", "DriveBasedOnTrailer", value)
        
    def handle_steering_smooth_time(self, *args):
        if args:
            value = args[0]
        else:
            value = settings.Get("Map", "SteeringSmoothTime", 0.2)
        settings.Set("Map", "SteeringSmoothTime", value)
    
    def handle_steering_smooth_time(self, value):
        settings.Set("Map", "SteeringSmoothTime", value)
        
    def handle_data_selection(self, value):
        if value:
            settings.Set("Map", "selected_data", value)
        else:
            settings.Set("Map", "selected_data", "")
            
    def handle_data_update(self):
        if self.plugin:
            self.plugin.trigger_data_update()
    
    def render(self):
        TitleAndDescription(
            title="map.settings.1.title",
            description="map.settings.1.description",
        )
        
        with Tabs():
            with Tab("map.settings.tab.general.name", container_style=styles.FlexVertical() + styles.Gap("20px")):
                CheckboxWithTitleDescription(
                    title="map.settings.use_navigation.name",
                    description="map.settings.use_navigation.description",
                    default=settings.Get("Map", "UseNavigation", True),
                    changed=self.handle_navigation,
                )
                CheckboxWithTitleDescription(
                    title="Send Elevation",
                    description="When enabled map will send elevation data to the frontend. This data is used to draw the ground in the visualization.",
                    default=settings.Get("Map", "SendElevationData", False),
                    changed=self.handle_elevation,
                )
                CheckboxWithTitleDescription(
                    title="Disable FPS Notices",
                    description="When enabled map will not notify of any FPS related issues.",
                    default=settings.Get("Map", "DisableFPSNotices", False),
                    changed=self.handle_fps_notices,
                )
                
            with Tab("map.settings.tab.steering.name", container_style=styles.FlexVertical() + styles.Gap("20px")):
                CheckboxWithTitleDescription(
                    title="map.settings.compute_steering_data.name",
                    description="map.settings.compute_steering_data.description",
                    default=settings.Get("Map", "ComputeSteeringData", True),
                    changed=self.handle_steering_data,
                )
                CheckboxWithTitleDescription(
                    title="map.settings.drive_based_on_trailer.name",
                    description="map.settings.drive_based_on_trailer.description",
                    default=settings.Get("Map", "DriveBasedOnTrailer", True),
                    changed=self.handle_drive_based_on_trailer,
                )
                SliderWithTitleDescription(
                    title="map.settings.steering_smooth_time.name",
                    description="map.settings.steering_smooth_time.description",
                    default=settings.Get("Map", "SteeringSmoothTime", 0.2),
                    min=0,
                    max=2,
                    step=0.1,
                    changed=self.handle_steering_smooth_time,
                )
                
            with Tab("Data", container_style=styles.FlexVertical() + styles.Gap("20px")):
                import Plugins.Map.utils.data_handler as dh
                index = dh.GetIndex()
                configs = {}
                for key, data in index.items():
                    try:
                        config = dh.GetConfig(data["config"])
                    except: pass
                    if config != {}:
                        configs[key] = config
                        
                with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Padding("0px")):
                    Text("NOTE!", styles.Classname("pl-4 font-semibold text-xs"))
                    Text("If you encounter an error after changing the changing the data please restart the plugin! If this doesn't resolve your issue then please contact the data creators or the developers on Discord!", styles.Description() + styles.Classname("pl-4 text-xs"))
        
                ComboboxWithTitleDescription(
                    title="Selected Data",
                    description="Please select the data you want to use. This will begin the download process and Map will be ready once the data is loaded.",
                    default=settings.Get("Map", "SelectedData", ""),
                    options=[config["name"] for config in configs.values()],
                    search=ComboboxSearch(
                        placeholder="Search data",
                        empty="No matching data found"
                    ),
                    changed=self.handle_data_selection,
                )
                
                ButtonWithTitleDescription(
                    title="Update Data",
                    description="Update the currently selected data, this can be helpful if the data is corrupted or there has been an update.",
                    text="Update",
                    action=self.handle_data_update
                )
                
                for key, data in index.items():
                    if key not in configs:
                        continue
                    
                    config = configs[key]
                    with Container(style=styles.FlexVertical() + styles.Gap("12px") + styles.Padding("16px") + styles.Classname("border rounded-md bg-input/10")):
                        with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Padding("0px")):
                            Text(config["name"], styles.Classname("font-semibold"))
                            Text(config["description"], styles.Description() + styles.Classname("text-xs"))
                            
                        with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Padding("0px")):
                            for title, credit in config["credits"].items():
                                with Container(style=styles.FlexHorizontal() + styles.Gap("4px") + styles.Padding("0px")):
                                    Text(title, styles.Description() + styles.Classname("text-xs"))
                                    Text(credit, styles.Classname("text-xs"))

                        with Container(style=styles.FlexHorizontal() + styles.Gap("4px") + styles.Padding("0px")):
                            Text("The", styles.Description() + styles.Classname("text-xs"))
                            Text("download size", styles.Description() + styles.Classname("text-xs"))
                            Text("for this data is", styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['packed_size'] / 1024 / 1024:.1f} MB", styles.Classname("text-xs"))
                            Text("that will unpack to a", styles.Description() + styles.Classname("text-xs"))
                            Text("total size", styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['size'] / 1024 / 1024:.1f} MB.", styles.Classname("text-xs"))
        
        #RefreshRate(0.25)
        #with Group("vertical", gap=14, padding=0):
        #    Title("map.settings.1.title")
        #    Description("map.settings.1.description")
        #
        #with TabView():
        #    with Tab("map.settings.tab.general.name"):
        #        Switch("map.settings.use_navigation.name", "UseNavigation", True, description="map.settings.use_navigation.description")
        #        Switch("Send Elevation", "SendElevationData", False, description="When enabled map will send elevation data to the frontend. This data is used to draw the ground in the visualization.")
        #        Switch("Disable FPS Notices", "DisableFPSNotices", False, description="When enabled map will not notify of any FPS related issues.")
        #        
        #    with Tab("map.settings.tab.steering.name"):
        #        Switch("map.settings.compute_steering_data.name", "ComputeSteeringData", True, description="map.settings.compute_steering_data.description")
        #        Switch("map.settings.drive_based_on_trailer.name", "DriveBasedOnTrailer", True, description="map.settings.drive_based_on_trailer.description")
        #        Slider("map.settings.steering_smooth_time.name", "SteeringSmoothTime", 0.2, 0, 2, 0.1, description="map.settings.steering_smooth_time.description", suffix=" s")
        #        
        #    with Tab("Data"):
        #        with EnabledLock():
        #            if self.plugin:
        #                import Plugins.Map.utils.data_handler as dh
        #                index = dh.GetIndex()
        #                configs = {}
        #                for key, data in index.items():
        #                    try:
        #                        config = dh.GetConfig(data["config"])
        #                    except: pass
        #                    if config != {}:
        #                        configs[key] = config
        #                    
        #                with Group("vertical", gap=2, padding=0):
        #                    Label("NOTE!", weight="semibold", size="xs", classname="pl-4")
        #                    Description("If you encounter an error after changing the changing the data please restart the plugin! If this doesn't resolve your issue then please contact the data creators or the developers on Discord!", size="xs", classname="pl-4")    
        #                Selector("Selected Data", "selected_data", "", [config["name"] for config in configs.values()], description="Please select the data you want to use. This will begin the download process and Map will be ready once the data is loaded.")
        #                Button("Update", "Update Data", self.plugin.trigger_data_update, description="Update the currently selected data, this can be helpful if the data is corrupted or there has been an update.", classname="bg-input/10")
        #                    
        #                for key, data in index.items():
        #                    if key not in configs:
        #                        continue
        #                    
        #                    config = configs[key]
        #                    with Group("vertical", gap=12, padding=16, border=True):
        #                        with Group("vertical", gap=2, padding=0):
        #                            Label(config["name"], weight="semibold")
        #                            Description(config["description"], size="xs")
        #                                                        
        #                        with Group("vertical", gap=4, padding=0):
        #                            for title, credit in config["credits"].items():
        #                                with Group("horizontal", gap=4, padding=0):
        #                                    Label(title, size="xs")
        #                                    Description(credit, size="xs")
#
        #                        with Group("horizontal", gap=4, padding=0):
        #                            Description("The", size="xs")
        #                            Label("download size", size="xs")
        #                            Description("for this data is", size="xs")
        #                            Description(f"{config['packed_size'] / 1024 / 1024:.1f} MB", size="xs")
        #                            Description("that will unpack to a", size="xs")
        #                            Label("total size", size="xs")
        #                            Description("of", size="xs")
        #                            Description(f"{config['size'] / 1024 / 1024:.1f} MB.", size="xs")
        #            else:
        #                Label("NOTE: When changing between ATS and ETS2 data you will need to restart the Map plugin after download!", weight="semibold")
        #                Selector("Selected Data", "selected_data", "", [], description="Please select the data you want to use. This will begin the download process and Map will be ready once the data is loaded.")
        #                Button("Update", "Update Data", self.get_value_from_data, description="Update the currently selected data, this can be helpful if the data is corrupted or there has been an update.")
        #                  
        #                            
        #    if variables.DEVELOPMENT_MODE:
        #        with Tab("Debug Data"):
        #            with EnabledLock():
        #                with Group("horizontal", gap=4):
        #                    with Group("vertical", gap=1):
        #                        Label("Map data:")
        #                        Space(0)
        #                        Description(f"Current coordinates: ({self.get_value_from_data('truck_x')}, {self.get_value_from_data('truck_z')})")
        #                        Description(f"Current sector: ({self.get_value_from_data('current_sector_x')}, {self.get_value_from_data('current_sector_y')})")
        #                        Description(f"Roads in sector: {len(self.get_value_from_data('current_sector_roads'))}")
        #                        Description(f"Prefabs in sector: {len(self.get_value_from_data('current_sector_prefabs'))}")
        #                        Description(f"Models in sector: {len(self.get_value_from_data('current_sector_models'))}")
        #                        try: Description(f"Last data update: {time.strftime('%H:%M:%S', time.localtime(self.get_value_from_data('external_data_time')))}")
        #                        except: Description(f"Last data update: N/A")
#
        #                    with Group("vertical", gap=1):
        #                        Label("Route data:")
        #                        Space(0)
        #                        Description(f"Is steering: {self.get_value_from_data('calculate_steering')}")
        #                        Description(f"Route points: {len(self.get_value_from_data('route_points'))}")
        #                        Description(f"Route plan elements: {len(self.get_value_from_data('route_plan'))}")
        #                        Description(f"Routing mode: {settings.Get('Map', 'RoutingMode')}")
        #                        Description(f"Navigation points: {len(self.get_value_from_data('navigation_points'))}")
        #                        Description(f"Has destination: {self.get_value_from_data('dest_company') is not None}")
#
        #                    with Group("vertical", gap=1):
        #                        Label("Backend data:")
        #                        Space(0)
        #                        try: Description(f"State: {self.plugin.state.text}, {self.plugin.state.progress:.0f}")
        #                        except: Description("State: N/A")
        #                        try: Description(f"FPS: {1/self.plugin.performance[-1][1]:.0f}")
        #                        except: Description("FPS: Still loading...")
        #                        
        #        with Tab("Development"):
        #            Switch("map.settings.6.name", "InternalVisualisation", False, description="map.settings.6.description")
        #            with EnabledLock():
        #                if self.plugin:
        #                    Button("Reload", "Reload Lane Offsets", description="Reload the lane offsets from the file. This will take a few seconds.", target=self.plugin.update_road_data)
        #                    # Add a button to update the offset configuration.
        #                    Button("Update the offset configuration", "Update Offset Config", description="Manually trigger the offset configuration update.", target=self.plugin.execute_offset_update)
        #                    Switch("Overide Lane Offsets", "Override Lane Offsets", False, description="When enabled, existing offsets will be overwritten in the file.")
        #                    Button("Clear Lane Offsets", "Clear Lane Offsets", description="Clear the lane offsets from the file. This will take a few seconds.", target=self.plugin.clear_lane_offsets)
        #                    import Plugins.Map.utils.road_helpers as rh
        #                    per_name = rh.per_name
        #                    rules = rh.rules
        #                    
        #                    with Group("vertical", padding=0, gap=8):
        #                        Label("Per Name", weight="semibold")
        #                        for name, rule in per_name.items():
        #                            with Group("horizontal", padding=0, gap=8):
        #                                Label(name)
        #                                Description(f"Offset: {rule}")
#
        #                    with Group("vertical", padding=0, gap=8):
        #                        Label("Lane Offsets", weight="semibold")
        #                        for name, rule in rules.items():
        #                            with Group("horizontal", padding=0, gap=8):
        #                                Label(name)
        #                                Description(f"Offset: {rule}")
        #                else:
        #                    Description("Plugin not loaded, cannot reload lane offsets.")
#
        #return RenderUI()
