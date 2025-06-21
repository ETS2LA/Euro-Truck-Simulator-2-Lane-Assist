from ETS2LA.UI import * 
from ETS2LA.Utils import settings

class SettingsMenu(ETS2LAPage):
    url = "/settings/adaptivecruisecontrol"
    location = ETS2LAPageLocation.SETTINGS
    title = "plugins.adaptivecruisecontrol"
    refresh_rate = 0.5
    
    def handle_aggressiveness(self, value):
        settings.Set("AdaptiveCruiseControl", "aggressiveness", value)
        
    def handle_following_distance(self, value): 
        settings.Set("AdaptiveCruiseControl", "following_distance", value)
        
    def handle_ignore_traffic_lights(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AdaptiveCruiseControl", "ignore_traffic_lights")
        
        settings.Set("AdaptiveCruiseControl", "ignore_traffic_lights", value)
    def handle_ignore_speed_limit(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AdaptiveCruiseControl", "ignore_speed_limit")
        
        settings.Set("AdaptiveCruiseControl", "ignore_speed_limit", value)
    
    def handle_speed_offset_type(self, value):
        settings.Set("AdaptiveCruiseControl", "speed_offset_type", value)
        
        if value == "Percentage":
            settings.Set("AdaptiveCruiseControl", "speed_offset", 0)
        else:
            settings.Set("AdaptiveCruiseControl", "speed_offset", 0)
            
    def handle_speed_offset(self, value):
        if settings.Get("AdaptiveCruiseControl", "speed_offset_type") == "Percentage":
            settings.Set("AdaptiveCruiseControl", "speed_offset", value)
        else:
            settings.Set("AdaptiveCruiseControl", "speed_offset", value)
            
    def handle_coefficient_of_friction(self, value):
        settings.Set("AdaptiveCruiseControl", "MU", value)
        
    def handle_overwrite_speed(self, value):
        settings.Set("AdaptiveCruiseControl", "overwrite_speed", value)
    
    def render(self):
        TitleAndDescription(
            title="plugins.adaptivecruisecontrol",
            description="Adaptive Cruise Control (ACC) controls the speed of the truck based on information gathered from the game.",
        )
        
        with Tabs():
            with Tab("plugins.adaptivecruisecontrol", container_style=styles.FlexVertical() + styles.Gap("24px")):
                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    ComboboxWithTitleDescription(
                        options=["Eco", "Normal", "Aggressive"],
                        default=settings.Get("AdaptiveCruiseControl", "aggressiveness"),
                        title="acc.settings.aggressiveness.name",
                        description="acc.settings.aggressiveness.description",
                        changed=self.handle_aggressiveness,
                    )
                    
                    ComboboxWithTitleDescription(
                        options=["Near", "Normal", "Far"],
                        default=settings.Get("AdaptiveCruiseControl", "following_distance"),
                        title="acc.settings.following_distance.name",
                        description="acc.settings.following_distance.description",
                        changed=self.handle_following_distance,
                    )

                CheckboxWithTitleDescription(
                    title="acc.settings.ignore_traffic_lights.name",
                    description="acc.settings.ignore_traffic_lights.description",
                    changed=self.handle_ignore_traffic_lights,
                    default=settings.Get("AdaptiveCruiseControl", "ignore_traffic_lights"),
                )
                
            with Tab("acc.settings.tab.speed_control.name", container_style=styles.FlexVertical() + styles.Gap("24px")):
                CheckboxWithTitleDescription(
                    title="acc.settings.ignore_speed_limit.name",
                    description="acc.settings.ignore_speed_limit.description",
                    changed=self.handle_ignore_speed_limit,
                    default=settings.Get("AdaptiveCruiseControl", "ignore_speed_limit"),
                )

                SliderWithTitleDescription(
                    title="acc.settings.coefficient_of_friction.name",
                    description="acc.settings.coefficient_of_friction.description",
                    min=0.1,
                    max=1,
                    step=0.1,
                    default=settings.Get("AdaptiveCruiseControl", "MU"),
                    changed=self.handle_coefficient_of_friction,
                    suffix=" μ",
                )
                
                if settings.Get("AdaptiveCruiseControl", "ignore_speed_limit") != True:
                    SliderWithTitleDescription(
                        title="acc.settings.overwrite_speed.name",
                        description="acc.settings.overwrite_speed.description",
                        min=0,
                        max=130,
                        step=5,
                        default=settings.Get("AdaptiveCruiseControl", "overwrite_speed", 0),
                        changed=self.handle_overwrite_speed,
                        suffix=" km/h",
                    )
                        
                    with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                        ComboboxWithTitleDescription(
                            options=["Percentage", "Absolute"],
                            default=settings.Get("AdaptiveCruiseControl", "speed_offset_type", "Absolute"),
                            title="acc.settings.speed_offset_type.name",
                            changed=self.handle_speed_offset_type,
                            description="acc.settings.speed_offset_type.description",
                        )
                        
                        if settings.Get("AdaptiveCruiseControl", "speed_offset_type") == "Percentage":
                            SliderWithTitleDescription(
                                title="acc.settings.speed_offset.name",
                                description="acc.settings.speed_offset.description",
                                min=-30,
                                max=30,
                                step=1,
                                default=settings.Get("AdaptiveCruiseControl", "speed_offset"),
                                changed=self.handle_speed_offset,
                                suffix="%",
                            )
                        else:
                            SliderWithTitleDescription(
                                title="acc.settings.speed_offset.name",
                                description="acc.settings.speed_offset.description",
                                min=-30,
                                max=30,
                                step=1,
                                default=settings.Get("AdaptiveCruiseControl", "speed_offset"),
                                changed=self.handle_speed_offset,
                                suffix="km/h",
                            )