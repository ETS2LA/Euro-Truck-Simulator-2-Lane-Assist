from ETS2LA.Utils import settings as utils_settings
from ETS2LA.UI import *

import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.sounds as sounds 

import screeninfo

class Page(ETS2LAPage):

    url = "/settings/global"
    monitors = len(screeninfo.get_monitors()) - 1
    
    def handle_width_change(self, width: int):
        utils_settings.Set("global", "width", width)
        
    def handle_height_change(self, height: int):
        utils_settings.Set("global", "height", height)
        
    def handle_alpha_change(self, alpha: float):
        utils_settings.Set("global", "transparency_alpha", alpha)
        
    def change_language(self, language: str):
        print(f"Language changed to {language}")
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
        
        monitor_index = int(monitor.split(" ")[-1])
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
    
    def render(self):
        
        with Container(styles.FlexVertical()):
            Text("global.settings.1.title", styles.Title())
            Text("global.settings.1.description", styles.Description())
        
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
                
            if self.monitors != 0:
                with Tab("global.settings.variables"):
                    monitors = [f"Display {i}" for i in range(self.monitors + 1)]
                    default = "Display " + str(utils_settings.Get("global", "monitor", default=0))
                    ComboboxWithTitleDescription(
                        title=translator.Translate("global.settings.13.name"),
                        description=translator.Translate("global.settings.13.description"),
                        default=default,
                        options=monitors,
                        changed=self.change_monitor,
                    )
                
            with Tab("global.settings.misc", styles.FlexVertical() + styles.Gap("24px")):
                port = utils_settings.Get("global", "frontend_port", default=3005) # type: ignore
                with Container(style=styles.FlexHorizontal() + styles.Gap("16px") + styles.Padding("14px 16px 16px 16px") + styles.Classname("border justify-between items-center rounded-md w-full bg-input/10")):
                    with Container(style=styles.FlexVertical()):
                        Text("global.settings.4.name", styles.Classname("font-semibold"))
                        Text("global.settings.4.description", styles.Classname("text-xs") + styles.Description())
                    Input(
                        default=port,
                        changed=self.change_port,
                        type=InputType.NUMBER,
                        style=styles.MaxWidth("200px"),
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
                
                
                
        #with Group("vertical", gap=14, padding=0):
        #    Title("global.settings.1.title")
        #    Description("global.settings.1.description")
        #    #Separator()
#
        #with TabView():
        #    with Tab("global.settings.misc"):
        #        
        #        
        #        Input("global.settings.4.name",
        #            "frontend_port",
        #            "number",
        #            3005,
        #            description="global.settings.4.description"
        #        )
        #        
        #        Toggle("global.settings.9.name", "frameless", True, description="global.settings.9.description")
#
        #        Toggle("global.settings.6.name",
        #            "send_crash_reports",
        #            True,
        #            description="global.settings.6.description"
        #        )
        #        
        #        Toggle("global.settings.5.name",
        #            "use_fancy_traceback",
        #            True,
        #            description="global.settings.5.description"
        #        )
#
        #        Toggle("global.settings.7.name",
        #            "debug_mode",
        #            True,
        #            description="global.settings.7.description"
        #        )
#
        #        Toggle("global.settings.16.name", "fireworks", True, description="global.settings.16.description")
        #
        #        Toggle("global.settings.15.name", "snow", True, description="global.settings.15.description")
    #
        #return RenderUI()