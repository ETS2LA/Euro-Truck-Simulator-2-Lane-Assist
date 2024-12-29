from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
from ETS2LA.UI.utils import SendPopup
from ETS2LA.UI import *

from Modules.SDKController.main import SCSController

import time

contributors = [
    {"name": "Tumppi066", "description": Translate("about.tumppi066.description"), "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": Translate("about.glas42.description"), "links": [["Github", "https://github.com/Glas42"]]},
    {"name": "Cloud", "description": Translate("about.cloud.description"), "links": []},
    {"name": "DylDev", "description": Translate("about.dyldev.description"), "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "truckermudgeon", "description": Translate("about.truckersmudgeon.description"), "links": []},
    {"name": "WhyTrevorWhy", "description": Translate("about.whytrevorwhy.description"), "links": []},
    {"name": "mimi89999", "description": Translate("about.mimi89999.description"), "links": []},
    {"name": "zhaoyj", "description": Translate("about.zhaoyj.description"), "links": []},
    {"name": "Lun", "description": Translate("about.lun.description"), "links": [["Discord", "https://discordapp.com/users/832636302402256898"]]},
    {"name": "ziakhan4505", "description": Translate("about.ziakhan4505.description"), "links": []},
    {"name": "MRUIAW", "description": Translate("about.mruiaw.description"), "links": []},
    {"name": "Piotrke", "description": Translate("about.piotrke.description"), "links": []},
    {"name": "DTheIcyDragon", "description": Translate("about.dtheicydragon.description"), "links": []},
    {"name": "Roman Sonnik", "description": Translate("about.romansonnik.description"), "links": [["Github", "https://github.com/RomanSonnik"]]},
    {"name": "atac_helicopter", "description": Translate("about.atac_helicopter.description"), "links": []},
    {"name": "ғʟᴇxғʟᴇxᴇɴ", "description": Translate("about.flexflexen.description"), "links": []},
    {"name": "LookAtYourSkill", "description": Translate("about.lookatyourskill.description"), "links": []},
    {"name": "ViSzKe", "description": Translate("about.viszke.description"), "links": []},
]

class Page(ETS2LAPage):
    dynamic = True
    url = "/about"
    settings_target = "about"
    
    def fix_wipers(self):
        print("Fixing wipers in 5s")
        start_time = time.perf_counter()
        controller = SCSController()
        while time.perf_counter() - start_time < 5:
            SendPopup(f"Fixing wipers in {5 - int(time.perf_counter() - start_time)} seconds...", "info")
            time.sleep(1)
        controller.wipers0 = True
        time.sleep(0.5)
        controller.wipers0 = False
        print("Fixed wipers!")
        SendPopup("Fixed wipers!", "success")
        
    def render(self):
        with Geist():
            Space(30)
            with Padding(20):
                with Group("vertical"):
                    Label(Translate("about.about"), classname_preset=TitleClassname)
                    Space(5)
                    Label(Translate("about.description"), classname_preset=DescriptionClassname)

                    Space(20)
                    with Group("vertical", classname="gap-4"):
                        Label(Translate("about.developers"), classname_preset=TitleClassname)
                        for contributor in contributors:
                            with Group("vertical", classname="gap-2"):
                                with Group("horizontal", classname="gap-4"):
                                    Label(contributor["name"])
                                    for link in contributor["links"]:
                                        Label(link[0], url=link[1], classname="text-xs")
                                Label(contributor["description"], classname_preset=DescriptionClassname)
                    
                    Space(20)
                    with Group("vertical", classname="gap-4"):
                        Label(Translate("about.translation_credits"), classname_preset=TitleClassname)
                        for language in translator.LANGUAGES:
                            with Group("vertical", classname="gap-2"):
                                with Group("horizontal", classname="gap-3"):
                                    Label(language)
                                    Label("(" + translator.TranslateToLanguage("name_en", translator.GetCodeForLanguage(language)) + ")", classname="text-xs")
                                credits = translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage(language))
                                if language != "English" and credits == translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage("English")):
                                    credits = Translate("about.no_credits")
                                Label(credits, classname_preset=DescriptionClassname)
                                
                    Space(20)
                    with Group("vertical", classname="gap-2"):
                        Label(Translate("about.support_development"), classname_preset=TitleClassname)
                        with Group("vertical", classname="gap-2"):
                            Label(Translate("about.kofi_description"), classname_preset=DescriptionClassname)
                            Label("  Ko-Fi", url="https://ko-fi.com/tumppi066")
                        with Group("vertical", classname="gap-2"):
                            Label(Translate("about.contribute_description"), classname_preset=DescriptionClassname)
                            Label("  Discord", url="https://discord.gg/ETS2LA")
                            Label("  Github", url="https://github.com/ETS2LA")
                        with Group("vertical", classname="gap-2"):
                            Label(Translate("about.translate_description"), classname_preset=DescriptionClassname)
                            Label("  Discord", url="https://discord.gg/ETS2LA")
                            
                    Space(20)
                    with Group("vertical", classname="gap-4"):
                        Label("Utils", classname_preset=TitleClassname)
                        ButtonGroup("Fix Wipers", "Did your wipers get stuck? Click the button and alt tab to the game. They should turn off in 5 seconds.", "Fix", self.fix_wipers)
                    
        return RenderUI()