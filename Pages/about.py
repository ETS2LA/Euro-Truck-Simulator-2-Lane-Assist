from ETS2LA.Networking.cloud import GetUserCount, GetUserTime, GetUniqueUsers, token, user_id, GetUsername
from ETS2LA.UI.utils import SendPopup
from ETS2LA.Utils import settings
from ETS2LA.UI import *

from Modules.SDKController.main import SCSController
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
import time

contributors = [
    {"name": "Tumppi066", "description": Translate("about.tumppi066.description"), "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": Translate("about.glas42.description"), "links": [["Github", "https://github.com/OleFranz"]]},
    {"name": "Cloud", "description": Translate("about.cloud.description"), "links": []},
    {"name": "DylDev", "description": Translate("about.dyldev.description"), "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "Roccovax", "description": Translate("about.roccovax.description"), "links": [["Github", "https://github.com/DarioWouters"]]},
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
        print("Fixing wipers (5s timer)")
        controller = SCSController()
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < 5:
            SendPopup(f"Fixing wipers in {5 - int(time.perf_counter() - start_time)} seconds...", "info")
            time.sleep(1)
        controller.wipers0 = True
        time.sleep(0.5)
        controller.wipers0 = False
        print("Wipers should be fixed now.")
        SendPopup("Wipers should be fixed now.", "success")
    
    def seconds_to_time(self, seconds):
        hours = round(seconds // 3600)
        minutes = round((seconds % 3600) // 60)
        if hours == 0:
            return Translate("about.statistics.usage_time_value_minute", [str(minutes)])
        elif minutes == 0:
            return Translate("about.statistics.usage_time_value_hour", [str(hours)])
        else:
            return Translate("about.statistics.usage_time_value_hour_and_minute", [str(hours), str(minutes)])
    
    def render(self):
        RefreshRate(10)
        with Geist():
            Space(20)
            with Padding(20):
                with Group("vertical"):
                    Title(Translate("about.about"))
                    Description(Translate("about.description"))
                    Space(2)
                    with Group("vertical", padding=0):
                        Title(Translate("about.statistics"))
                        with Group("vertical", gap=6, padding=0):
                            with Group("horizontal", gap=10, padding=0):
                                Label(f"{Translate('about.statistics.users_online')} ")
                                Description(Translate("about.statistics.users_online_value", [str(GetUserCount())]))
                            with Group("horizontal", gap=10, padding=0):
                                Label(f"{Translate('about.statistics.past_24h')} ")
                                Description(Translate("about.statistics.past_24h_value", [str(GetUniqueUsers())]))
                            with Group("horizontal", gap=10, padding=0):
                                Label(f"{Translate('about.statistics.usage_time')} ")
                                Description(self.seconds_to_time(GetUserTime()))
                            if token is None:
                                Space(2)
                                Label(f"{Translate('about.statistics.not_logged_in')} ")
                                Description(Translate("about.statistics.anonymous_user_id", [str(user_id)]))
                            else:
                                Space(2)
                                Label(f"{Translate('about.statistics.logged_in')} ")
                                Description(Translate("about.statistics.welcome", [str(GetUsername())]))
                                
                    Space(1)
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
                                credits = translator.TranslateToLanguage("credits", translator.GetCodeForLanguage(language))
                                if language != "English" and credits == translator.TranslateToLanguage("credits", translator.GetCodeForLanguage("English")):
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
                            
                    Space(12)
                    with Group("vertical", padding=0, gap=16):
                        Title("Utils")
                        Button("Activate", "Fix wipers", self.fix_wipers, description="Did your wipers get stuck? Click the button and alt tab to the game. They should turn off in 5 seconds.")
                    
        return RenderUI()