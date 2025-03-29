from ETS2LA.UI import * 

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "AdaptiveCruiseControl"
    def render(self):
        RefreshRate(1)
        with Group("vertical", gap=14, padding=0):
            Title("plugins.adaptivecruisecontrol")
            Description("This plugin provides no description.")
        with TabView():
            with Tab("acc.settings.tab.acc.name"):
                with Group("horizontal", padding=0, gap=24):
                    Selector("acc.settings.aggressiveness.name", "aggressiveness", "Normal", ["Eco", "Normal", "Aggressive"], description="acc.settings.aggressiveness.description")
                    Selector("acc.settings.following_distance.name", "following_distance", "Normal", ["Near", "Normal", "Far"], description="acc.settings.following_distance.description")
                
                with EnabledLock():
                    if self.plugin is None:
                        max_accel = 1.5
                        comfort_decel = 1.5
                        time_gap_seconds = 1.5
                    else:
                        max_accel = self.plugin.max_accel
                        comfort_decel = self.plugin.comfort_decel
                        time_gap_seconds = self.plugin.time_gap_seconds
                        
                    with Group("vertical", padding=0, gap=8):
                        with Group("horizontal", padding=4):
                            Label("acc.settings.maximum_acceleration.name")
                            Description(str(round(max_accel, 1)) + " m/s²")
                        with Group("horizontal", padding=4):
                            Label("acc.settings.maximum_deceleration.name")
                            Description(str(round(comfort_decel, 1)) + " m/s²")
                        with Group("horizontal", padding=4):
                            Label("acc.settings.gap_to_vehicle_in_front.name")
                            Description(str(round(time_gap_seconds, 1)) + " seconds")

            with Tab("acc.settings.tab.speed_control.name"):
                Slider("acc.settings.coefficient_of_friction.name", "MU", 0.5, 0.1, 1, 0.1, description="acc.settings.coefficient_of_friction.description", suffix=" μ")
                Slider("acc.settings.overwrite_speed.name", "overwrite_speed", 50, 0, 130, 5, suffix=" km/h", description="acc.settings.overwrite_speed.description")
                with EnabledLock():
                    Selector("acc.settings.speed_offset_type.name", "speed_offset_type", "Percentage", ["Percentage", "Absolute"], description="acc.settings.speed_offset_type.description")
                    type = self.settings.type
                    if not type:
                        type = "Percentage"
                        self.settings.type = type
                        
                    if self.settings.type is not None and self.settings.type == "Percentage":
                        Slider("acc.settings.speed_offset.name", "speed_offset", 0, -30, 30, 1, suffix="%", description="acc.settings.speed_offset.description")
                    else:
                        Slider("acc.settings.speed_offset.name", "speed_offset", 0, -30, 30, 1, suffix="km/h", description="acc.settings.speed_offset.description")
        return RenderUI()
