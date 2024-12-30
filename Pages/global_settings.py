import ETS2LA.Utils.translator as translator
import ETS2LA.Handlers.sounds as sounds 
from ETS2LA.UI import *

import screeninfo

class Page(ETS2LAPage):
    dynamic = True
    url = "/settings/global"
    settings_target = "global"
    monitors = len(screeninfo.get_monitors()) - 1
    def render(self):
        with Group("vertical",classname="gap-[14px]"):
            Label("global.settings.1.title", classname=TITLE_CLASSNAME)
            Label("global.settings.1.description", classname=DESCRIPTION_CLASSNAME)

        with TabView():
            with Tab("global.settings.ui"):
                Space(2)
                with Group("horizontal", "w-full justify-between text-start items-center gap-[32px]"):
                    Slider("global.settings.10.name", "width", 1280, 920, 2560, 10, description="global.settings.10.description")
                    Slider("global.settings.11.name", "height", 720, 480, 1440, 10, description="global.settings.11.description")

                Slider("global.settings.12.name", "transparency_alpha", 0.8, 0.4, 1, 0.05, description="global.settings.12.description")               
                Space(4)

                with Group("vertical"):
                    Selector("global.settings.8.name", "language", "English", translator.LANGUAGES, description="global.settings.8.description")
                    Label("language_credits", classname=DESCRIPTION_CLASSNAME)

            with Tab("global.settings.audio"):
                Space(2)
                with Group("vertical", "gap-4"):
                    Selector("global.settings.2.name", "soundpack", sounds.SELECTED_SOUNDPACK, sounds.SOUNDPACKS, description="global.settings.2.description")
                    Slider("global.settings.3.name", "volume", sounds.VOLUME * 100, 0, 100, 5, description="global.settings.3.description")
    
            with Tab("global.settings.variables"):
                Space(2)
                if self.monitors != 0:
                    Slider("global.settings.13.name", "display", 0, 0, self.monitors, 1, description="global.settings.13.description")
                Input("global.settings.14.name", "number", "FOV", 77, description="global.settings.14.description")
    
            with Tab("global.settings.misc"):
                Space(2)
                Input("global.settings.4.name", "number" "frontend_port", 3005, description="global.settings.4.description")
                Switch("global.settings.6.name", "send_crash_reports", True, description="global.settings.6.description")
                Switch("global.settings.5.name", "use_fancy_traceback", True, description="global.settings.5.description")
                Switch("global.settings.7.name", "debug_mode", True, description="global.settings.7.description")
                Switch("global.settings.16.name", "fireworks", True, description="global.settings.16.description")
                Switch("global.settings.15.name", "snow", True, description="global.settings.15.description")
    
        return RenderUI()