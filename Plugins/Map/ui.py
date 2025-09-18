from ETS2LA.UI import (
    styles,
    ETS2LAPage,
    ETS2LAPageLocation,
    TitleAndDescription,
    Tabs,
    Tab,
    Container,
    Text,
    Space,
    CheckboxWithTitleDescription,
    Checkbox,
    SliderWithTitleDescription,
    ComboboxWithTitleDescription,
    ComboboxSearch,
    ButtonWithTitleDescription,
    Slider,
)
from ETS2LA import variables

from Plugins.Map.settings import settings
from ETS2LA.Utils.translator import _
import Plugins.Map.data as data


class SettingsMenu(ETS2LAPage):
    url = "/settings/map"
    title = _("Map")
    location = ETS2LAPageLocation.SETTINGS
    refresh_rate = 10

    def get_value_from_data(self, key: str):
        if "data" not in globals():
            return "N/A"
        if key in data.__dict__:
            return data.__dict__[key]
        return _("Not Found")

    def handle_navigation(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.UseNavigation
        settings.UseNavigation = value

    def handle_elevation(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.SendElevationData
        settings.SendElevationData = value

    def handle_fps_notices(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.DisableFPSNotices
        settings.DisableFPSNotices = value

    def handle_steering_data(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.ComputeSteeringData
        settings.ComputeSteeringData = value

    def handle_drive_based_on_trailer(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.DriveBasedOnTrailer
        settings.DriveBasedOnTrailer = value

    def handle_steering_smooth_time(self, value):
        settings.SteeringSmoothTime = value

    def handle_data_selection(self, value):
        if value:
            settings.selected_data = value
        else:
            settings.selected_data = value

    def handle_traffic_side(self, value):
        if value:
            settings.traffic_side = value

    def handle_data_update(self):
        if self.plugin:
            self.plugin.trigger_data_update()

    def handle_road_quality_multiplier(self, value):
        if isinstance(value, str):
            value = float(value)

        settings.RoadQualityMultiplier = value
        data.road_quality_multiplier = value

    def handle_internal_visualisation(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.InternalVisualisation
        settings.InternalVisualisation = value

    def handle_override_lane_offsets(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.OverrideLaneOffsets
        settings.OverrideLaneOffsets = value

    def handle_auto_tolls(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.AutoTolls

        settings.AutoTolls = value

    def render(self):
        TitleAndDescription(
            title=_("Map Settings"),
            description=_(
                "Configure the settings for the Map plugin. Here you can adjust various options related to navigation, steering, and data handling."
            ),
        )

        with Tabs():
            with Tab(
                _("General"), container_style=styles.FlexVertical() + styles.Gap("20px")
            ):
                CheckboxWithTitleDescription(
                    title=_("Disable FPS Notices"),
                    description=_(
                        "When enabled map will not notify of any FPS related issues."
                    ),
                    default=settings.DisableFPSNotices,
                    changed=self.handle_fps_notices,
                )

                Text("Experimental Features", styles.Classname("font-semibold"))

                # Same as CheckBoxWithTitleDescription, but with custom experimental styling.
                with Container(
                    styles.FlexHorizontal()
                    + styles.Gap("16px")
                    + styles.Padding("14px 16px 16px 16px")
                    + styles.Classname(
                        "border rounded-md w-full "
                        + ("bg-input/30" if settings.AutoTolls else "bg-input/10")
                    ),
                    pressed=self.handle_auto_tolls,  # This allows for the entire container to act as the toggle
                ):
                    Checkbox(
                        default=settings.AutoTolls,  # type: ignore
                        changed=self.handle_auto_tolls,
                        style=styles.Margin("4px 0px 0px 0px"),
                    )
                    with Container(styles.FlexVertical() + styles.Gap("6px")):
                        with Container(styles.FlexHorizontal() + styles.Gap("6px")):
                            Text(
                                _("[Experimental]"),
                                styles.Classname("font-semibold text-muted-foreground"),
                            )
                            Text(
                                _("Automatic Tolls"), styles.Classname("font-semibold")
                            )
                        Text(
                            _(
                                "Attempt to automatically solve tolls. This may or may not work. Requires a restart to fully reload toll data."
                            ),
                            styles.Classname("text-xs text-muted-foreground"),
                        )

                # Same as SliderWithTitleDescription, but with custom experimental styling.
                with Container(
                    style=styles.FlexVertical()
                    + styles.Classname("border rounded-md p-4 w-full bg-input/10")
                    + styles.Gap("10px")
                ):
                    with Container(
                        style=styles.FlexHorizontal()
                        + styles.Classname("justify-between")
                    ):
                        with Container(styles.FlexHorizontal() + styles.Gap("6px")):
                            Text(
                                _("[Experimental]"),
                                styles.Classname("font-semibold text-muted-foreground"),
                            )
                            Text(
                                "Point Density Multiplier",
                                styles.Classname("font-semibold"),
                            )
                        Text(
                            f"{settings.RoadQualityMultiplier}x",
                            styles.Classname("text-muted-foreground"),
                        )
                    Slider(
                        min=0.5,
                        default=settings.RoadQualityMultiplier,
                        max=2,
                        step=0.1,
                        suffix="x",
                        changed=self.handle_road_quality_multiplier,
                    )
                    Text(
                        "Will either improve or degrade steering quality in tight turns. Will increase CPU and RAM usage, might decrease steering stability at high values.",
                        styles.Description() + styles.Classname("text-xs"),
                    )

                # CheckboxWithTitleDescription(
                #     title=_("Send Elevation"),
                #     description=_("When enabled map will send elevation data to the frontend. This data is used to draw the ground in the visualization. Experimental and very broken!"),
                #     default=settings.SendElevationData,
                #     changed=self.handle_elevation,
                # )

            with Tab(
                _("Steering"),
                container_style=styles.FlexVertical() + styles.Gap("20px"),
            ):
                CheckboxWithTitleDescription(
                    title=_("Compute Steering Data"),
                    description=_(
                        "When enabled map will compute and send steering data to the game."
                    ),
                    default=settings.ComputeSteeringData,
                    changed=self.handle_steering_data,
                )
                CheckboxWithTitleDescription(
                    title=_("Drive Based On Trailer"),
                    description=_(
                        "When enabled map will take into account the trailer when calculating the current steering point."
                    ),
                    default=settings.DriveBasedOnTrailer,
                    changed=self.handle_drive_based_on_trailer,
                )
                SliderWithTitleDescription(
                    title=_("Steering Smoothness"),
                    description=_(
                        "Set the time we average the steering data over. A value of 0.5 means that the steering from the last half a second is used to calculate the current value."
                    ),
                    default=settings.SteeringSmoothTime,
                    min=0,
                    max=2,
                    step=0.1,
                    changed=self.handle_steering_smooth_time,
                )

            with Tab(
                _("Data"), container_style=styles.FlexVertical() + styles.Gap("20px")
            ):
                import Plugins.Map.utils.data_handler as dh

                index = dh.GetIndex()
                configs = {}
                for key, data in index.items():
                    try:
                        config = dh.GetConfig(data["config"])
                    except Exception:
                        pass
                    if config != {}:
                        configs[key] = config

                with Container(
                    style=styles.FlexVertical()
                    + styles.Gap("4px")
                    + styles.Padding("0px")
                ):
                    Text(_("NOTE!"), styles.Classname("pl-4 font-semibold text-xs"))
                    Text(
                        _(
                            "If you encounter an error after changing the changing the data please restart the plugin! If this doesn't resolve your issue then please contact the data creators or the developers on Discord!"
                        ),
                        styles.Description() + styles.Classname("pl-4 text-xs"),
                    )

                ComboboxWithTitleDescription(
                    title=_("Selected Data"),
                    description=_(
                        "Please select the data you want to use. This will begin the download process and Map will be ready once the data is loaded."
                    ),
                    default=settings.selected_data,
                    options=[config["name"] for config in configs.values()],
                    search=ComboboxSearch(
                        placeholder=_("Search data"), empty=_("No matching data found")
                    ),
                    changed=self.handle_data_selection,
                )

                ButtonWithTitleDescription(
                    title=_("Update Data"),
                    description=_(
                        "Update the currently selected data, this can be helpful if the data is corrupted or there has been an update."
                    ),
                    text=_("Update"),
                    action=self.handle_data_update,
                )

                ComboboxWithTitleDescription(
                    title=_("Traffic Side"),
                    description=_(
                        "This will make the indicators behave correctly when lane changing in left handed or right handed countries."
                    ),
                    default=settings.traffic_side,
                    options=["Right", "Left", "Automatic"],
                    changed=self.handle_traffic_side,
                )

                for key, _data in index.items():
                    if key not in configs:
                        continue

                    config = configs[key]
                    with Container(
                        style=styles.FlexVertical()
                        + styles.Gap("12px")
                        + styles.Padding("16px")
                        + styles.Classname("border rounded-md bg-input/10")
                    ):
                        with Container(
                            style=styles.FlexVertical()
                            + styles.Gap("4px")
                            + styles.Padding("0px")
                        ):
                            Text(config["name"], styles.Classname("font-semibold"))
                            Text(
                                config["description"],
                                styles.Description() + styles.Classname("text-xs"),
                            )

                        with Container(
                            style=styles.FlexVertical()
                            + styles.Gap("4px")
                            + styles.Padding("0px")
                        ):
                            for title, credit in config["credits"].items():
                                with Container(
                                    style=styles.FlexHorizontal()
                                    + styles.Gap("4px")
                                    + styles.Padding("0px")
                                ):
                                    Text(
                                        title,
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                    Text(credit, styles.Classname("text-xs"))

                        with Container(
                            style=styles.FlexHorizontal()
                            + styles.Gap("4px")
                            + styles.Padding("0px")
                        ):
                            Text(
                                _("The download size for this data is"),
                                styles.Description() + styles.Classname("text-xs"),
                            )
                            Text(
                                f"{config['packed_size'] / 1024 / 1024:.1f} MB",
                                styles.Classname("text-xs"),
                            )
                            Text(
                                _("that will unpack to a total size of"),
                                styles.Description() + styles.Classname("text-xs"),
                            )
                            Text(
                                f"{config['size'] / 1024 / 1024:.1f} MB.",
                                styles.Classname("text-xs"),
                            )

            if variables.DEVELOPMENT_MODE:
                with Tab(
                    "Debug Data",
                    container_style=styles.FlexVertical() + styles.Gap("20px"),
                ):
                    with Container(
                        style=styles.FlexHorizontal()
                        + styles.Gap("4px")
                        + styles.Padding("0px")
                    ):
                        if self.plugin:
                            self.refresh_rate = 0.25
                            with Container(
                                style=styles.FlexVertical()
                                + styles.Gap("4px")
                                + styles.Padding("0px")
                            ):
                                Text("Map Data:")
                                Space()
                                Text(
                                    f"Current coordinates: ({self.get_value_from_data('truck_x')}, {self.get_value_from_data('truck_z')})",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Current sector: ({self.get_value_from_data('current_sector_x')}, {self.get_value_from_data('current_sector_y')})",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Roads in sector: {len(self.get_value_from_data('current_sector_roads'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Prefabs in sector: {len(self.get_value_from_data('current_sector_prefabs'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Models in sector: {len(self.get_value_from_data('current_sector_models'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )

                            with Container(
                                style=styles.FlexVertical()
                                + styles.Gap("4px")
                                + styles.Padding("0px")
                            ):
                                Text("Route Data:")
                                Space()
                                Text(
                                    f"Is steering: {self.get_value_from_data('calculate_steering')}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Route points: {len(self.get_value_from_data('route_points'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Route plan elements: {len(self.get_value_from_data('route_plan'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Navigation points: {len(self.get_value_from_data('navigation_points'))}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )
                                Text(
                                    f"Has destination: {self.get_value_from_data('dest_company') is not None}",
                                    styles.Description() + styles.Classname("text-xs"),
                                )

                            with Container(
                                style=styles.FlexVertical()
                                + styles.Gap("4px")
                                + styles.Padding("0px")
                            ):
                                Text("Backend Data:")
                                Space()
                                try:
                                    Text(
                                        f"State: {self.plugin.state.text}, {self.plugin.state.progress:.0f}",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                except Exception:
                                    Text(
                                        "State: N/A",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                try:
                                    Text(
                                        f"FPS: {1 / self.plugin.performance[-1][1]:.0f}",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                except Exception:
                                    Text(
                                        "FPS: Still loading...",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                        else:
                            self.refresh_rate = 10
                            Text(
                                "Plugin not loaded, cannot display debug data.",
                                styles.Description() + styles.Classname("text-xs"),
                            )

                with Tab(
                    "Development",
                    container_style=styles.FlexVertical() + styles.Gap("20px"),
                ):
                    if self.plugin:
                        CheckboxWithTitleDescription(
                            title="Internal Visualisation",
                            description="Enable internal visualisation for debugging.",
                            changed=self.handle_internal_visualisation,
                            default=settings.InternalVisualisation,
                        )
                        ButtonWithTitleDescription(
                            title="Reload Lane Offsets",
                            description="Reload the lane offsets from the file. This will take a few seconds.",
                            action=self.plugin.update_road_data,
                        )
                        # Add a button to update the offset configuration.
                        ButtonWithTitleDescription(
                            title="Update Per name",
                            description="Update the lane offsets for a specific name.",
                            action=self.plugin.execute_offset_update,
                        )
                        CheckboxWithTitleDescription(
                            title="Override Lane Offsets",
                            description="When enabled, existing offsets will be overwritten in the file.",
                            changed=self.handle_override_lane_offsets,
                            default=settings.OverrideLaneOffsets,
                        )
                        ButtonWithTitleDescription(
                            title="Generate Rules",
                            description="Generate rules for the roads based on the lane offsets.",
                            action=self.plugin.generate_rules,
                        )
                        ButtonWithTitleDescription(
                            title="Clear Rules",
                            description="Clear the generated rules.",
                            action=self.plugin.clear_rules,
                        )
                        ButtonWithTitleDescription(
                            title="Clear Per name",
                            description="Clear the lane offsets for a specific name.",
                            action=self.plugin.clear_lane_offsets,
                        )
                        import Plugins.Map.utils.road_helpers as rh

                        per_name = rh.per_name
                        rules = rh.rules

                        with Container(style=styles.FlexVertical() + styles.Gap("8px")):
                            Text(
                                "Per Name",
                                styles.Title() + styles.Classname("font-semibold"),
                            )
                            for name, rule in per_name.items():
                                with Container(
                                    style=styles.FlexHorizontal() + styles.Gap("8px")
                                ):
                                    Text(
                                        name,
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                    Text(
                                        f"Offset: {rule}",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                            Text(
                                "Lane Offsets",
                                styles.Title() + styles.Classname("font-semibold"),
                            )
                            for name, rule in rules.items():
                                with Container(
                                    style=styles.FlexHorizontal() + styles.Gap("8px")
                                ):
                                    Text(
                                        name,
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )
                                    Text(
                                        f"Offset: {rule}",
                                        styles.Description()
                                        + styles.Classname("text-xs"),
                                    )

                    else:
                        Text(
                            "Plugin not loaded, cannot reload lane offsets.",
                            styles.Description() + styles.Classname("text-xs"),
                        )
