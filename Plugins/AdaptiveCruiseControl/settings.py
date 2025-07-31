from ETS2LA.UI import * 
from ETS2LA.Utils import settings
from ETS2LA.Utils.translator import _

class SettingsMenu(ETS2LAPage):
    url = "/settings/adaptivecruisecontrol"
    location = ETS2LAPageLocation.SETTINGS
    title = _("Adaptive Cruise Control")
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
    
    def handle_speed_offset_type(self, value):
        settings.Set("AdaptiveCruiseControl", "speed_offset_type", value)
        settings.Set("AdaptiveCruiseControl", "speed_offset", 0)

    def handle_speed_offset(self, value):
        settings.Set("AdaptiveCruiseControl", "speed_offset", value)
            
    def handle_coefficient_of_friction(self, value):
        settings.Set("AdaptiveCruiseControl", "MU", value)
        
    def handle_overwrite_speed(self, value):
        settings.Set("AdaptiveCruiseControl", "overwrite_speed", value)
        
    def handle_ignore_speed_limit(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AdaptiveCruiseControl", "ignore_speed_limit")
        
        settings.Set("AdaptiveCruiseControl", "ignore_speed_limit", value)
        
    def handle_pid_unlock(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AdaptiveCruiseControl", "unlock_pid")
        
        settings.Set("AdaptiveCruiseControl", "unlock_pid", value)
        
    def handle_pid_kp(self, value):
        settings.Set("AdaptiveCruiseControl", "pid_kp", value)
        
    def handle_pid_ki(self, value):
        settings.Set("AdaptiveCruiseControl", "pid_ki", value)
        
    def handle_pid_kd(self, value):
        settings.Set("AdaptiveCruiseControl", "pid_kd", value)
    
    def render(self):
        TitleAndDescription(
            title=_("Adaptive Cruise Control"),
            description=_("Adaptive Cruise Control (ACC) controls the speed of the truck based on information gathered from the game."),
        )
        
        with Tabs():
            with Tab(_("Adaptive Cruise Control"), container_style=styles.FlexVertical() + styles.Gap("24px")):
                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    ComboboxWithTitleDescription(
                        options=["Eco", "Normal", "Aggressive"],
                        default=settings.Get("AdaptiveCruiseControl", "aggressiveness"),
                        title=_("Aggressiveness"),
                        description=_("How aggressively should the ACC follow the car in front and change the speedlimit?"),
                        changed=self.handle_aggressiveness,
                    )
                    
                    ComboboxWithTitleDescription(
                        options=["Near", "Normal", "Far"],
                        default=settings.Get("AdaptiveCruiseControl", "following_distance"),
                        title=_("Following Distance"),
                        description=_("How far should the ACC keep from the vehicle in front?"),
                        changed=self.handle_following_distance,
                    )

                CheckboxWithTitleDescription(
                    title=_("Ignore Traffic Lights"),
                    description=_("Whether the ACC should ignore traffic lights. Please note that this will, as it says ignore the traffic lights."),
                    changed=self.handle_ignore_traffic_lights,
                    default=settings.Get("AdaptiveCruiseControl", "ignore_traffic_lights"),
                )

            with Tab(_("Speed Control"), container_style=styles.FlexVertical() + styles.Gap("24px")):
                ignore_speed_limit = settings.Get("AdaptiveCruiseControl", "ignore_speed_limit")
                CheckboxWithTitleDescription(
                    title=_("Ignore Speed Limit"),
                    description=_("Whether the ACC should ignore the speed limit."),
                    changed=self.handle_ignore_speed_limit,
                    default=ignore_speed_limit
                )

                SliderWithTitleDescription(
                    title=_("Coefficient of Friction"),
                    description=_("The coefficient of friction used for the ACC calculations. Higher values allow the truck to drive faster in curves."),
                    min=0.1,
                    max=1,
                    step=0.1,
                    default=settings.Get("AdaptiveCruiseControl", "MU"),
                    changed=self.handle_coefficient_of_friction,
                    suffix=" μ",
                )
                
                SliderWithTitleDescription(
                    title=_("Speed when game speed limit is 0"),
                    description=_("The speed to drive when the game tells us that the speed limit is 0 km/h."),
                    min=0,
                    max=130,
                    step=5,
                    default=settings.Get("AdaptiveCruiseControl", "overwrite_speed", 0),
                    changed=self.handle_overwrite_speed,
                    suffix=" km/h",
                )
                
                if ignore_speed_limit != True:        
                    with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                        speed_offset_type = settings.Get("AdaptiveCruiseControl", "speed_offset_type", "Absolute")
                        ComboboxWithTitleDescription(
                            options=["Percentage", "Absolute"],
                            default=speed_offset_type,
                            title=_("Speed Offset Type"),
                            changed=self.handle_speed_offset_type,
                            description=_("Select the type of speed offset to apply."),
                        )
                        
                        SliderWithTitleDescription(
                            title=_("Speed Offset"),
                            description=_("The speed offset to apply to all speedlimits. Please note that you can also change this dynamically with the keybinds in the controls."),
                            min=-30,
                            max=30,
                            step=1,
                            default=settings.Get("AdaptiveCruiseControl", "speed_offset"),
                            changed=self.handle_speed_offset,
                            suffix="%" if speed_offset_type == "Percentage" else "km/h",
                        )
                            
            with Tab(_("PID"), container_style=styles.FlexVertical() + styles.Gap("24px")):
                unlocked = settings.Get("AdaptiveCruiseControl", "unlock_pid", False)
                CheckboxWithTitleDescription(
                    title=_("Unlock PID"),
                    description=_("You can unlock the PID settings to adjust them manually. This isn't recommended unless you know what a PID is and how you can tune it correctly."),
                    changed=self.handle_pid_unlock,
                    default=unlocked,
                )
                
                if unlocked:
                    SliderWithTitleDescription(
                        title=_("PID Kp"),
                        description=_("Are we there yet? No? Then we need to accelerate more! (Proportional gain for the PID controller.)"),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.Get("AdaptiveCruiseControl", "pid_kp", 0.30),
                        changed=self.handle_pid_kp,
                    )
                    SliderWithTitleDescription(
                        title=_("PID Ki"),
                        description=_("Has it been a while since we were there? Then we need to accelerate more! (Integral gain for the PID controller.)"),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.Get("AdaptiveCruiseControl", "pid_ki", 0.08),
                        changed=self.handle_pid_ki,
                    )
                    SliderWithTitleDescription(
                        title=_("PID Kd"),
                        description=_("How fast are we approaching the target? If we are approaching too fast, we need to decelerate more! (Derivative gain for the PID controller.)"),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.Get("AdaptiveCruiseControl", "pid_kd", 0.05),
                        changed=self.handle_pid_kd,
                    )

                Text(_("This video visually explains how a PID controller works. Please watch it fully if you are not familiar with them."), style=styles.Description())
                with Container(styles.FlexHorizontal() + styles.Width("100%") + styles.Height("400px")):
                    Youtube("qKy98Cbcltw")