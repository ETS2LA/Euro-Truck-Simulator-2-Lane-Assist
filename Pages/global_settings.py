from ETS2LA.Utils import settings
from ETS2LA.UI import *

import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.sounds as sounds 

import screeninfo

class Page(ETS2LAPage):
    dynamic = True
    url = "/settings/global"
    settings_target = "global"
    monitors = len(screeninfo.get_monitors()) - 1
    def render(self):
        with Group("vertical", gap=14, padding=0):
            Title("global.settings.1.title")
            Description("global.settings.1.description")
            #Separator()

        with TabView():
            with Tab("global.settings.ui"):
                Space(2)
                with Group("horizontal", gap=32, padding=0, border=False, classname="flex w-full justify-between text-start items-center"):
                    Slider("global.settings.10.name",
                        "width",
                        1280,
                        920,
                        2560,
                        10,
                        description="global.settings.10.description"
                    )

                    Slider("global.settings.11.name",
                        "height",
                        720,
                        480,
                        1440,
                        10,
                        description="global.settings.11.description"
                    )

                Slider("global.settings.12.name",
                    "transparency_alpha",
                    0.8,
                    0.4,
                    1,
                    0.05,
                    description="global.settings.12.description"
                )
                
                Space(8)

                with Group("vertical", gap=8, padding=0):
                    Selector("global.settings.8.name",
                        "language",
                        "English",
                        translator.LANGUAGES,
                        description="global.settings.8.description"
                    )
        
                    Description("credits", size="xs")

            with Tab("global.settings.audio"):
                Space(2)
                with Group("horizontal", gap=32, padding=0, border=False, classname="flex w-full justify-between text-start items-center"):
                    Selector("global.settings.2.name",
                        "soundpack",
                        sounds.SELECTED_SOUNDPACK, 
                        sounds.SOUNDPACKS,
                        description="global.settings.2.description"
                    )

                    Slider("global.settings.3.name",
                        "volume",
                        sounds.VOLUME * 100, # default 
                        0, # min
                        100, # max
                        5, # step
                        description="global.settings.3.description",
                        suffix="%"
                    )
    
            with Tab("global.settings.variables"):
                Space(2)
                if self.monitors != 0:
                    Slider("global.settings.13.name",
                        "display",
                        0,
                        0,
                        self.monitors,
                        1,
                        description="global.settings.13.description"
                    )
                Input("global.settings.14.name", "FOV", "number", 77, description="global.settings.14.description")
    
            with Tab("global.settings.misc"):
                Space(2)
                Input("global.settings.4.name",
                    "frontend_port",
                    "number",
                    3005,
                    description="global.settings.4.description"
                )
                
                Switch("global.settings.6.name",
                    "send_crash_reports",
                    True,
                    description="global.settings.6.description"
                )
                
                Switch("global.settings.5.name",
                    "use_fancy_traceback",
                    True,
                    description="global.settings.5.description"
                )

                Switch("global.settings.7.name",
                    "debug_mode",
                    True,
                    description="global.settings.7.description"
                )

                Switch("global.settings.16.name", "fireworks", True, description="global.settings.16.description")
        
                Switch("global.settings.15.name", "snow", True, description="global.settings.15.description")
    
        return RenderUI()