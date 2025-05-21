from ETS2LA.Networking.cloud import GetUserCount, GetUserTime, GetUniqueUsers, token, user_id, GetUsername
from ETS2LA.UI.utils import SendPopup
from ETS2LA.Utils import settings
from ETS2LA.UI import *

from ETS2LA.Networking.Servers.webserver import mainThreadQueue
from Modules.SDKController.main import SCSController
from ETS2LA.Utils.translator import Translate
import ETS2LA.Utils.translator as translator
from ETS2LA.Utils.umami import TriggerEvent
from ETS2LA.Utils.version import Update
import time

contributors = [
    {"name": "Tumppi066", "description": Translate("about.tumppi066.description"), "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": Translate("about.glas42.description"), "links": [["Github", "https://github.com/OleFranz"]]},
    {"name": "DylDev", "description": Translate("about.dyldev.description"), "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "Roccovax", "description": Translate("about.roccovax.description"), "links": [["Github", "https://github.com/DarioWouters"]]},
    {"name": "truckermudgeon", "description": Translate("about.truckersmudgeon.description"), "links": []},
    {"name": "Cloud", "description": Translate("about.cloud.description"), "links": []},
    {"name": "ziakhan4505", "description": Translate("about.ziakhan4505.description"), "links": []},
    {"name": "WhyTrevorWhy", "description": Translate("about.whytrevorwhy.description"), "links": []},
    {"name": "mimi89999", "description": Translate("about.mimi89999.description"), "links": []},
    {"name": "zhaoyj", "description": Translate("about.zhaoyj.description"), "links": []},
    {"name": "JimJokes", "description": Translate("about.jimjokes.description"), "links": []},
    {"name": "Lun", "description": Translate("about.lun.description"), "links": [["Discord", "https://discordapp.com/users/832636302402256898"]]},
    {"name": "MRUIAW", "description": Translate("about.mruiaw.description"), "links": [["BiliBili", "https://space.bilibili.com/357816575"]]},
    {"name": "PiggyWu981", "description": Translate("about.piggywu981.description"), "links": [["GitHub", "https://github.com/Piggywu981"], ["BiliBili", "https://space.bilibili.com/355054416"], ["Discord", "https://discordapp.com/users/763642553412223008"]]},
    {"name": "Sheng FAN", "description": Translate("about.shengfan.description"), "links": [["Github", "https://github.com/fred913"]]},
    {"name": "goodnightan", "description": Translate("about.goodnightan.description"), "links": []},
    {"name": "Piotrke", "description": Translate("about.piotrke.description"), "links": []},
    {"name": "DTheIcyDragon", "description": Translate("about.dtheicydragon.description"), "links": []},
    {"name": "Roman Sonnik", "description": Translate("about.romansonnik.description"), "links": [["Github", "https://github.com/RomanSonnik"]]},
    {"name": "atac_helicopter", "description": Translate("about.atac_helicopter.description"), "links": []},
    {"name": "ғʟᴇxғʟᴇxᴇɴ", "description": Translate("about.flexflexen.description"), "links": []},
    {"name": "LookAtYourSkill", "description": Translate("about.lookatyourskill.description"), "links": []},
    {"name": "ViSzKe", "description": Translate("about.viszke.description"), "links": []},
]

class Page(ETS2LAPage):
    url = "/about"
    
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
        
    def update(self, *args, **kwargs):
        print("Triggering update")
        try:
            TriggerEvent("Update App")
        except:
            pass
        mainThreadQueue.append([Update, [], {}])
    
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
        with Container(style=styles.FlexVertical() + styles.Padding("80px 0px 0px 80px") + styles.MaxWidth("900px")):
            Text("about.about", styles.Title())
            Space()
            Text("about.description", styles.Description())
            Space(style=styles.Height("14px"))
            
            with Container(style=styles.FlexVertical()):
                Text("about.statistics", styles.Title())
                Space()
                with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{Translate('about.statistics.users_online')} ")
                        Text(Translate("about.statistics.users_online_value", [str(GetUserCount())]), styles.Description())
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{Translate('about.statistics.past_24h')} ")
                        Text(Translate("about.statistics.past_24h_value", [str(GetUniqueUsers())]), styles.Description())
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{Translate('about.statistics.usage_time')} ")
                        Text(self.seconds_to_time(GetUserTime()), styles.Description())
                    if token is None:
                        with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{Translate('about.statistics.not_logged_in')} ")
                            Text(Translate("about.statistics.anonymous_user_id", [str(user_id)]), styles.Description())
                    else:
                        with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{Translate('about.statistics.logged_in')} ")
                            Text(Translate("about.statistics.welcome", [str(GetUsername())]), styles.Description())
        
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text("about.developers", styles.Title())
                    for contributor in contributors:
                        with Container(style=styles.FlexVertical() + styles.Gap("4px")):
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px 0px 0px 0px") + styles.Classname("items-center")):
                                Text(contributor["name"], styles.PlainText())
                                for link in contributor["links"]:
                                    Link(link[0], link[1], style=styles.Classname("text-xs hover:underline"))
                            Text(contributor["description"], styles.Description())
                            
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text("about.translation_credits", styles.Title())
                    for language in translator.LANGUAGES:
                        with Container(style=styles.FlexVertical() + styles.Gap("4px")):
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px 0px 0px 0px") + styles.Classname("items-center")):
                                Text(language, styles.PlainText())
                                Text("(" + translator.TranslateToLanguage("name_en", translator.GetCodeForLanguage(language)) + ")", styles.Description() + styles.Classname("text-xs"))
                            credits = translator.TranslateToLanguage("credits", translator.GetCodeForLanguage(language))
                            if language != "English" and credits == translator.TranslateToLanguage("credits", translator.GetCodeForLanguage("English")):
                                credits = Translate("about.no_credits")
                            Text(credits, styles.Description())
                            
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                    Text("about.support_development", styles.Title())
                    with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.kofi_description"), styles.Description())
                            Link("Ko-Fi", "https://ko-fi.com/tumppi066", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.contribute_description"), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                            Link("GitHub", "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.translate_description"), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text("Utils", styles.Title())
                    
                    ButtonWithTitleDescription(
                        self.fix_wipers,
                        title="Fix Wipers",
                        description="Did your wipers get stuck? Click the button and alt tab to the game. They should turn off in 5 seconds.",
                        text="Activate"
                    )
                    
                    ButtonWithTitleDescription(
                        self.update,
                        title="Force an update",
                        description="Do you think there should've been an update? Click this button and the app will restart and check for them.",
                        text="Update"
                    )