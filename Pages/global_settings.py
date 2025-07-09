from ETS2LA.Utils import settings as utils_settings
from ETS2LA import variables
from ETS2LA.UI import *

import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.sounds as sounds 

import screeninfo

class Page(ETS2LAPage):
    url = "/settings/global"
    monitors = screeninfo.get_monitors()
    initial_high_priority = False
    
    def __init__(self):
        super().__init__()
        self.initial_high_priority = utils_settings.Get("global", "high_priority", default=True)
    
    def handle_width_change(self, width: int):
        utils_settings.Set("global", "width", width)
        
    def handle_height_change(self, height: int):
        utils_settings.Set("global", "height", height)
        
    def handle_alpha_change(self, alpha: float):
        utils_settings.Set("global", "transparency_alpha", alpha)
        
    def change_language(self, language: str):
        utils_settings.Set("global", "language", language)
    
    def change_soundpack(self, soundpack: str):
        utils_settings.Set("global", "soundpack", soundpack)
        
    def change_volume(self, volume: int):
        utils_settings.Set("global", "volume", volume)
        
    def change_startup_sound(self, *args):
        if args:
            startup_sound = args[0]
        else:
            startup_sound = not utils_settings.Get("global", "startup_sound", default=True)
            
        utils_settings.Set("global", "startup_sound", startup_sound)
    
    def change_monitor(self, monitor: str):
        if not monitor:
            return
        
        monitor_index = int(monitor.split(" ")[1])
        utils_settings.Set("global", "monitor", monitor_index)
        
    def change_port(self, port: int):
        if not port:
            return
        
        utils_settings.Set("global", "frontend_port", port)
        
    def handle_frameless_change(self, *args):
        if args:
            frameless = args[0]
        else:
            frameless = not utils_settings.Get("global", "frameless", default=False)
            
        utils_settings.Set("global", "frameless", frameless)
        
    def handle_crash_report_change(self, *args):
        if args:
            crash_report = args[0]
        else:
            crash_report = not utils_settings.Get("global", "send_crash_reports", default=True)
            
        utils_settings.Set("global", "send_crash_reports", crash_report)
        
    def handle_fancy_traceback_change(self, *args):
        if args:
            fancy_traceback = args[0]
        else:
            fancy_traceback = not utils_settings.Get("global", "use_fancy_traceback", default=True)
            
        utils_settings.Set("global", "use_fancy_traceback", fancy_traceback)
        
    def handle_debug_mode_change(self, *args):
        if args:
            debug_mode = args[0]
        else:
            debug_mode = not utils_settings.Get("global", "debug_mode", default=True)
            
        utils_settings.Set("global", "debug_mode", debug_mode)
        
    def handle_fireworks_change(self, *args):
        if args:
            fireworks = args[0]
        else:
            fireworks = not utils_settings.Get("global", "fireworks", default=True)
            
        utils_settings.Set("global", "fireworks", fireworks)
        
    def handle_snow_change(self, *args):
        if args:
            snow = args[0]
        else:
            snow = not utils_settings.Get("global", "snow", default=True)
            
        utils_settings.Set("global", "snow", snow)
        
    def handle_acceleration_fallback_change(self, *args):
        if args:
            acceleration_fallback = args[0]
        else:
            acceleration_fallback = not utils_settings.Get("global", "acceleration_fallback", default=False)

        utils_settings.Set("global", "acceleration_fallback", acceleration_fallback)
        
    def handle_high_priority_change(self, *args):
        if args:
            high_priority = args[0]
        else:
            high_priority = not utils_settings.Get("global", "high_priority", default=True)

        utils_settings.Set("global", "high_priority", high_priority)

    def render(self):
        TitleAndDescription(
            "global.settings.1.title",
            "global.settings.1.description",
        )
        
        with Tabs():
            with Tab("global.settings.ui", styles.FlexVertical() + styles.Gap("24px")):
                with Container(styles.FlexHorizontal() + styles.Gap("24px") + styles.Classname("justify-between")):
                    SliderWithTitleDescription(
                        title=translator.Translate("global.settings.10.name"),
                        description=translator.Translate("global.settings.10.description"),
                        min=500,
                        max=2560,
                        step=10,
                        default=utils_settings.Get("global", "width", default=720), # type: ignore
                        suffix="px",
                        changed=self.handle_width_change
                    )
                    
                    SliderWithTitleDescription(
                        title=translator.Translate("global.settings.11.name"),
                        description=translator.Translate("global.settings.11.description"),
                        min=250,
                        max=1440,
                        step=10,
                        default=utils_settings.Get("global", "height", default=720), # type: ignore
                        suffix="px",
                        changed=self.handle_height_change
                    )

                SliderWithTitleDescription(
                    title=translator.Translate("global.settings.12.name"),
                    description=translator.Translate("global.settings.12.description"),
                    min=0.4,
                    max=1,
                    step=0.05,
                    default=utils_settings.Get("global", "transparency_alpha", default=0.8), # type: ignore
                    suffix="",
                    changed=self.handle_alpha_change
                )
                
                ComboboxWithTitleDescription(
                    title="global.settings.8.name",
                    description=translator.Translate("global.settings.8.description"),
                    default=utils_settings.Get("global", "language", default="English"), # type: ignore
                    options=translator.LANGUAGES,
                    changed=self.change_language,
                    side=Side.TOP,
                    search=ComboboxSearch("Search Languages...", "Help us translate on discord!"),
                )
                
                with Alert(style=styles.Padding("14px")):
                    with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                        style = styles.Style()
                        style.margin_top = "2px"
                        style.width = "1rem"
                        style.height = "1rem"
                        style.color = "var(--muted-foreground)"
                        Icon("info", style)
                        Text(translator.Translate("credits"), styles.Classname("text-muted-foreground"))
                
            with Tab("global.settings.audio", container_style=styles.FlexVertical() + styles.Gap("24px")):
                with Container(styles.FlexHorizontal() + styles.Gap("24px") + styles.Classname("justify-between")):
                    ComboboxWithTitleDescription(
                        title=translator.Translate("global.settings.2.name"),
                        description=translator.Translate("global.settings.2.description"),
                        default=sounds.SELECTED_SOUNDPACK,
                        options=sounds.SOUNDPACKS,
                        changed=self.change_soundpack,
                    )
                    
                    SliderWithTitleDescription(
                        title=translator.Translate("global.settings.3.name"),
                        description=translator.Translate("global.settings.3.description"),
                        min=0,
                        max=100,
                        step=5,
                        default=int(sounds.VOLUME * 100),
                        suffix="%",
                        changed=self.change_volume,
                    )
                    
                state = utils_settings.Get("global", "startup_sound", default=True)
                CheckboxWithTitleDescription(
                    title="Startup Sound",
                    description="Toggle the startup sound on or off. This plays every time the ETS2LA window is opened.",
                    default=state, # type: ignore
                    changed=self.change_startup_sound,
                )
                
            with Tab("global.settings.variables", container_style=styles.FlexVertical() + styles.Gap("24px")):
                CheckboxWithTitleDescription(
                    title="Fallback to old acceleration method",
                    description="If you are experiencing issues with the truck not accelerating / braking properly, then you can enable this option to use another method. Please keep in mind that if the new one has gotten stuck, you might need to restart the game after toggling this.",
                    default=utils_settings.Get("global", "acceleration_fallback", default=False), # type: ignore
                    changed=self.handle_acceleration_fallback_change
                )
                
                high_priority = utils_settings.Get("global", "high_priority", default=True) # type: ignore
                CheckboxWithTitleDescription(
                    title="High Priority",
                    description="Run ETS2LA in high priority mode. This will tell your OS to give more CPU time to ETS2LA, which can improve performance at the cost of other applications.",
                    default=high_priority, # type: ignore
                    changed=self.handle_high_priority_change
                )
                
                if high_priority != self.initial_high_priority:
                    with Alert(style=styles.Padding("14px")):
                        with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                            style = styles.Style()
                            style.margin_top = "2px"
                            style.width = "1rem"
                            style.height = "1rem"
                            style.color = "var(--muted-foreground)"
                            Icon("warning", style)
                            Text("You need to restart ETS2LA to apply the priority change!", styles.Classname("text-muted-foreground"))
                
                # if self.monitors != 0:
                #     monitors = []
                #     for i, monitor in enumerate(self.monitors):
                #         if monitor.is_primary:
                #             monitors.append(f"Display {i} - {monitor.width}x{monitor.height} (Primary)")
                #         else:
                #             monitors.append(f"Display {i} - {monitor.width}x{monitor.height}")
                #     
                #     default = monitors[utils_settings.Get("global", "monitor", default=0)] # type: ignore
                #     ComboboxWithTitleDescription(
                #         title=translator.Translate("global.settings.13.name"),
                #         description=translator.Translate("global.settings.13.description"),
                #         default=default,
                #         options=monitors,
                #         changed=self.change_monitor,
                #     )
                
            with Tab("global.settings.misc", styles.FlexVertical() + styles.Gap("24px")):
                if variables.LOCAL_MODE:
                    port = utils_settings.Get("global", "frontend_port", default=3005) # type: ignore
                    InputWithTitleDescription(
                        title="global.settings.4.name",
                        description="global.settings.4.description",
                        default=port,
                        type=InputType.NUMBER,
                        changed=self.change_port,
                    )
                
                CheckboxWithTitleDescription(
                    title="global.settings.9.name",
                    description="global.settings.9.description",
                    default=utils_settings.Get("global", "frameless", default=False), # type: ignore
                    changed=self.handle_frameless_change
                )
                
                CheckboxWithTitleDescription(
                    title="global.settings.6.name",
                    description="global.settings.6.description",
                    default=utils_settings.Get("global", "send_crash_reports", default=True), # type: ignore
                    changed=self.handle_crash_report_change
                )
                
                CheckboxWithTitleDescription(
                    title="global.settings.5.name",
                    description="global.settings.5.description",
                    default=utils_settings.Get("global", "use_fancy_traceback", default=True), # type: ignore
                    changed=self.handle_fancy_traceback_change
                )
                
                CheckboxWithTitleDescription(
                    title="global.settings.7.name",
                    description="global.settings.7.description",
                    default=utils_settings.Get("global", "debug_mode", default=True), # type: ignore
                    changed=self.handle_debug_mode_change
                )
                
                Separator()
                with Container(styles.FlexHorizontal() + styles.Gap("24px") + styles.Classname("justify-between")):
                    CheckboxWithTitleDescription(
                        title="global.settings.16.name",
                        description="global.settings.16.description",
                        default=utils_settings.Get("global", "fireworks", default=True), # type: ignore
                        changed=self.handle_fireworks_change
                    )
                    
                    CheckboxWithTitleDescription(
                        title="global.settings.15.name",
                        description="global.settings.15.description",
                        default=utils_settings.Get("global", "snow", default=True), # type: ignore
                        changed=self.handle_snow_change
                    )
                    
                Space(styles.Height("24px"))