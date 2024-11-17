from ETS2LA.backend import settings
from ETS2LA.UI import *

from ETS2LA.utils.translator import Translate
import ETS2LA.utils.translator as translator
import time

contributors = [
    {"name": "Tumppi066", "description": Translate("about.tumppi066.description"), "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": Translate("about.glas42.description"), "links": [["Github", "https://github.com/Glas42"]]},
    {"name": "Cloud", "description": Translate("about.cloud.description"), "links": []},
    {"name": "DylDev", "description": Translate("about.dyldev.description"), "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "truckermudgeon", "description": Translate("about.truckersmudgeon.description"), "links": []},
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
    
    def render(self):
        with Geist():
            Space(20)
            with Padding(20):
                with Group("vertical"):
                    Title(Translate("about.about"))
                    Description(Translate("about.description"))
                    Space(2)
                    with Group("vertical", padding=0):
                        Title(Translate("about.developers"))

                        for contributor in contributors:
                            with Group("vertical", gap=6, padding=0):
                                with Group("horizontal", gap=10, padding=0):
                                    Label(contributor["name"])
                                    for link in contributor["links"]:
                                        Link(link[0], link[1], size="xs")
                                Description(contributor["description"])
                    
                    Space(12)
                    with Group("vertical", padding=0, gap=24):
                        Title(Translate("about.translation_credits"))
                        
                        for language in translator.LANGUAGES:
                            with Group("vertical", gap=6, padding=0):
                                with Group("horizontal", gap=10, padding=0):
                                    Label(language)
                                    Description("(" + translator.TranslateToLanguage("name_en", translator.GetCodeForLanguage(language)) + ")", size="xs")
                                credits = translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage(language))
                                if language != "English" and credits == translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage("English")):
                                    credits = Translate("about.no_credits")
                                Description(credits)
                                
                    Space(12)
                    with Group("vertical", padding=0, gap=16):
                        Title(Translate("about.support_development"))
                        with Group("vertical", gap=6, padding=0):
                            Description(Translate("about.kofi_description"))
                            Link("  Ko-Fi", "https://ko-fi.com/tumppi066")
                        with Group("vertical", gap=6, padding=0):
                            Description(Translate("about.contribute_description"))
                            Link("  Discord", "https://discord.gg/ETS2LA")
                            Link("  Github", "https://github.com/ETS2LA")
                        with Group("vertical", gap=6, padding=0):
                            Description(Translate("about.translate_description"))
                            Link("  Discord", "https://discord.gg/ETS2LA")
                    
        return RenderUI()