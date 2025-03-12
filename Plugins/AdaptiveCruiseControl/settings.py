from ETS2LA.UI import * 

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True
    plugin_name = "AdaptiveCruiseControl"
    def render(self):
        RefreshRate(1)
        Title("acc.settings.1.title")
        Description("acc.settings.1.description")
        Separator()
        with TabView():
            with Tab("Adaptive Cruise Control"):
                Selector("Aggressiveness", "aggressiveness", "Normal", ["Eco", "Normal", "Aggressive"], description="How aggressively the truck will accelerate and decelerate.")
                Selector("Following Distance", "following_distance", "Normal", ["Near", "Normal", "Far"], description="How far the truck will keep from the vehicle in front of it.")
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
                            Label("Maximum Acceleration:")
                            Description(str(round(max_accel, 1)) + " m/s²")
                        with Group("horizontal", padding=4):
                            Label("Maximum Deceleration:")
                            Description(str(round(comfort_decel, 1)) + " m/s²")
                        with Group("horizontal", padding=4):
                            Label("Gap to Vehicle in Front:")
                            Description(str(round(time_gap_seconds, 1)) + " seconds")

            with Tab("Speed Control"):
                Slider("Coefficient of friction", "MU", 0.5, 0.1, 1, 0.1, description="Controls the (imaginary) friction between the tires and the road. Lower values will make the truck slow down more, while higher values will make it go faster in turns.")
                Slider("acc.settings.7.name", "overwrite_speed", 50, 0, 130, 5, suffix="km/h", description="acc.settings.7.description")
                with EnabledLock():
                    Selector("acc.settings.5.name", "speed_offset_type", "Percentage", ["Percentage", "Absolute"], description="acc.settings.5.description")
                    type = self.settings.type
                    if not type:
                        type = "Percentage"
                        self.settings.type = type
                        
                    if self.settings.type is not None and self.settings.type == "Percentage":
                        Slider("acc.settings.3.name", "speed_offset", 0, -30, 30, 1, suffix="%", description="acc.settings.3.description")
                    else:
                        Slider("acc.settings.3.name", "speed_offset", 0, -30, 30, 1, suffix="km/h", description="acc.settings.3.description")
        return RenderUI()