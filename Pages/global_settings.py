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
                
            with Tab("global.settings.audio"):
                ...
                
            with Tab("global.settings.variables"):
                ...
                
            with Tab("global.settings.misc"):
                ...
                
        #with Group("vertical", gap=14, padding=0):
        #    Title("global.settings.1.title")
        #    Description("global.settings.1.description")
        #    #Separator()
#
        #with TabView():
        #    with Tab("global.settings.ui"):
        #        with Group("horizontal", gap=24, padding=0, border=False, classname="flex w-full justify-between text-start items-center"):
        #            Slider("global.settings.10.name",
        #                "width",
        #                1280,
        #                500,
        #                2560,
        #                10,
        #                description="global.settings.10.description",
        #                suffix="px"
        #            )
#
        #            Slider("global.settings.11.name",
        #                "height",
        #                720,
        #                250,
        #                1440,
        #                10,
        #                description="global.settings.11.description",
        #                suffix="px"
        #            )
#
        #        Slider("global.settings.12.name",
        #            "transparency_alpha",
        #            0.8,
        #            0.4,
        #            1,
        #            0.05,
        #            description="global.settings.12.description"
        #        )
        #        
        #        with Group("vertical", gap=3, padding=0):
        #            text = translator.Translate("global.settings.8.description") + " " + translator.Translate("credits")
        #            Selector("global.settings.8.name",
        #                "language",
        #                "English",
        #                translator.LANGUAGES,
        #                description=text
        #            )
        #        
#
        #    with Tab("global.settings.audio"):
        #        with Group("horizontal", gap=24, padding=0, border=False, classname="flex w-full justify-between text-start items-center"):
        #            Selector("global.settings.2.name",
        #                "soundpack",
        #                sounds.SELECTED_SOUNDPACK, 
        #                sounds.SOUNDPACKS,
        #                description="global.settings.2.description"
        #            )
#
        #            Slider("global.settings.3.name",
        #                "volume",
        #                sounds.VOLUME * 100, # default 
        #                0, # min
        #                100, # max
        #                5, # step
        #                description="global.settings.3.description",
        #                suffix="%"
        #            )
        #            
        #        Toggle("Startup Sound", "startup_sound", True, description="Toggle the startup sound on or off. This plays every time the ETS2LA window is opened.")
    #
        #    with Tab("global.settings.variables"):
        #        if self.monitors != 0:
        #            Slider("global.settings.13.name",
        #                "display",
        #                0,
        #                0,
        #                self.monitors,
        #                1,
        #                description="global.settings.13.description"
        #            )
        #        Input("global.settings.14.name", "FOV", "number", 77, description="global.settings.14.description")
    #
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