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
    url = "/about"
    refresh_rate = 1
    value = 0
    
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
        
    def increment_value(self, *args, **kwargs):
        self.value += 1
        print(f"Value incremented to {self.value}")
        
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
            Text("about.description", styles.Description())
            Space(style=styles.Height("10px"))
            
            with Container(style=styles.FlexVertical()):
                Text("about.statistics", styles.Title())
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
                        with Container(style=styles.FlexVertical() + styles.Gap("2px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{Translate('about.statistics.not_logged_in')} ")
                            Text(Translate("about.statistics.anonymous_user_id", [str(user_id)]), styles.Description())
                    else:
                        with Container(style=styles.FlexVertical() + styles.Gap("2px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{Translate('about.statistics.logged_in')} ")
                            Text(Translate("about.statistics.welcome", [str(GetUsername())]), styles.Description())
        
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                    Text("about.developers", styles.Title())
                    for contributor in contributors:
                        with Container(style=styles.FlexVertical() + styles.Gap("2px")):
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px 0px 0px 0px") + styles.Classname("items-center")):
                                Text(contributor["name"], styles.PlainText())
                                for link in contributor["links"]:
                                    Link(link[0], link[1], style=styles.Classname("text-xs text-muted-foreground hover:underline"))
                            Text(contributor["description"], styles.Description())
                            
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                    Text("about.translation_credits", styles.Title())
                    for language in translator.LANGUAGES:
                        with Container(style=styles.FlexVertical() + styles.Gap("2px")):
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
                        with Container(style=styles.FlexVertical() + styles.Gap("2px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.kofi_description"), styles.Description())
                            Link("Ko-Fi", "https://ko-fi.com/tumppi066", style=styles.Classname("text-xs text-muted-foreground hover:underline") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("2px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.contribute_description"), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs text-muted-foreground hover:underline") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("2px") + styles.Padding("0px 0px 0px 0px")):
                            Text(Translate("about.translate_description"), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs text-muted-foreground hover:underline") + styles.Padding("0px 0px 0px 7px"))
                
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
                    
                    Text(f"Value: {self.value}", styles.Description())
                    with Button(self.increment_value):
                        Text("Increment Value")