from ETS2LA.backend import settings
from ETS2LA.UI import *

import ETS2LA.utils.translator as translator
import ETS2LA.backend.sounds as sounds 

class Page(ETS2LAPage):
    dynamic = True
    url = "/settings/global"
    settings_target = "global"
    def render(self):
       Title("global.settings.1.title")
       Description("global.settings.1.description")
       Separator()
       
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
       
       Separator()
       
       with Group("vertical", gap=0):
              Selector("global.settings.8.name",
                     "language",
                     "English",
                     translator.LANGUAGES,
                     description="global.settings.8.description"
              )
              Description("language_credits")
              
       Separator()
              
       Input("global.settings.4.name",
              "frontend_port",
              "number",
              3005,
              description="global.settings.4.description"
       )
       
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
       
       Separator()
       
       Switch("global.settings.9.name",
              "frameless",
              True,
              description="global.settings.9.description"
       )
       
       Switch("global.settings.5.name",
              "use_fancy_traceback",
              True,
              description="global.settings.5.description"
       )
       
       Switch("global.settings.6.name",
              "send_crash_reports",
              True,
              description="global.settings.6.description"
       )
       
       Switch("global.settings.7.name",
              "debug_mode",
              True,
              description="global.settings.7.description"
       )
       
       return RenderUI()