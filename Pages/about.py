from ETS2LA.Networking.cloud import GetUserCount, GetUserTime, GetUniqueUsers, token, user_id, GetUsername
from ETS2LA.UI.utils import SendPopup
from ETS2LA.UI import *

from ETS2LA.Networking.Servers.webserver import mainThreadQueue
from Modules.SDKController.main import SCSController
from ETS2LA.Utils.translator import _, ngettext, languages, parse_language
from ETS2LA.Utils.umami import TriggerEvent
from ETS2LA.Utils.version import Update
from langcodes import Language 
import time

contributors = [
    {"name": "Tumppi066", "description": _("Lead developer and creator of ETS2LA, backend & frontend."), "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": _("Navigation Detection, Traffic Light Detection, ETS2LA Lite, 'co-owner'"), "links": [["Github", "https://github.com/OleFranz"]]},
    {"name": "DylDev", "description": _("Various additions and improvements, Object Detection AI models & development"), "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "Roccovax", "description": _("ETS2LA game-side SDK developer. Vehicles, Traffic Lights, Camera data and more direct from the game."), "links": [["Github", "https://github.com/DarioWouters"]]},
    {"name": "truckermudgeon", "description": _("Game data extraction and processing"), "links": []},
    {"name": "Cloud", "description": _("Linux & Unix Port, various improvements and bug fixes"), "links": []},
    {"name": "ziakhan4505", "description": _("ETS2LA SDK C++ developer, Linux & Unix Port, bug fixes"), "links": []},
    {"name": "WhyTrevorWhy", "description": _("Help with Navigate on ETS2LA & Map"), "links": []},
    {"name": "mimi89999", "description": _("scs-sdk-controller developer"), "links": []},
    {"name": "zhaoyj", "description": _("3D models for the visualization"), "links": []},
    {"name": "JimJokes", "description": _("Data extractor development, support for modded maps."), "links": []},
    {"name": "Lun", "description": _("Chinese translation, bug fixes"), "links": [["Discord", "https://discordapp.com/users/832636302402256898"]]},
    {"name": "MRUIAW", "description": _("Chinese translations, bug fixes"), "links": [["BiliBili", "https://space.bilibili.com/357816575"]]},
    {"name": "PiggyWu981", "description": _("Automatic offset calculations for the Map plugin."), "links": [["GitHub", "https://github.com/Piggywu981"], ["BiliBili", "https://space.bilibili.com/355054416"], ["Discord", "https://discordapp.com/users/763642553412223008"]]},
    {"name": "Sheng FAN", "description": _("Discord server support, Chinese-English translator developer."), "links": [["Github", "https://github.com/fred913"]]},
    {"name": "goodnightan", "description": _("Maintaining CN mirrors for ETS2LA services."), "links": [["BiliBili", "https://space.bilibili.com/525984002"]]},
    {"name": "Piotrke", "description": _("Game hooks"), "links": []},
    {"name": "DTheIcyDragon", "description": _("Bug fixes"), "links": []},
    {"name": "Roman Sonnik", "description": _("Bug fixes"), "links": [["Github", "https://github.com/RomanSonnik"]]},
    {"name": "atac_helicopter", "description": _("Bug fixes"), "links": []},
    {"name": "ғʟᴇxғʟᴇxᴇɴ", "description": _("Bug fixes"), "links": []},
    {"name": "LookAtYourSkill", "description": _("Bug fixes"), "links": []},
    {"name": "ViSzKe", "description": _("Bug fixes"), "links": []},
]

class Page(ETS2LAPage):
    url = "/about"
    
    def fix_wipers(self):
        print(_("Fixing wipers (5s timer)"))
        controller = SCSController()
        
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < 5:
            SendPopup(_("Fixing wipers in {0} seconds...").format(5 - int(time.perf_counter() - start_time)), "info")
            time.sleep(1)
            
        controller.wipers0 = True
        time.sleep(0.5)
        controller.wipers0 = False
        print(_("Wipers should be fixed now."))
        SendPopup(_("Wipers should be fixed now."), "success")

    def update(self, *args, **kwargs):
        print(_("Triggering update"))
        try:
            TriggerEvent("Update App")
        except:
            pass
        mainThreadQueue.append([Update, [], {}])
    
    def seconds_to_time(self, seconds):
        if seconds == 0:
            return ngettext("{0} minute", "{0} minutes", 0).format(0)

        hours = round(seconds // 3600)
        minutes = round((seconds % 3600) // 60)
        if hours == 0:
            return ngettext("{0} minute", "{0} minutes", minutes).format(minutes)
        elif minutes == 0:
            return ngettext("{0} hour", "{0} hours", hours).format(hours)
        else:
            return _("{0} and {1}").format(
                ngettext("{0} hour", "{0} hours", hours).format(hours),
                ngettext("{0} minute", "{0} minutes", minutes).format(minutes)
            )

    def render(self):
        with Container(style=styles.FlexVertical() + styles.Padding("80px 0px 0px 80px") + styles.MaxWidth("900px")):
            Text(_("About"), styles.Title())
            Space()
            Text(_("ETS2LA is a project that aims to provide an easy to use self driving solution for ETS2 and ATS, if you want to learn more then you can visit the github page or the wiki via the sidebar."), styles.Description())
            Space(style=styles.Height("14px"))
            
            with Container(style=styles.FlexVertical()):
                Text(_("Statistics"), styles.Title())
                Space()
                with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{_('Users online:')} ")
                        Text(_("{0} users").format(GetUserCount()), styles.Description())
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{_('Past 24 hours:')} ")
                        Text(_("{0} unique users").format(GetUniqueUsers()), styles.Description())
                    with Container(style=styles.FlexHorizontal()):
                        Text(f"{_('Your usage time:')} ")
                        Text(self.seconds_to_time(GetUserTime()), styles.Description())
                    if token is None:
                        with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{_('You are not logged in.')} ")
                            Text(_("Your anonymous user ID is: {0}").format(str(user_id)), styles.Description())
                    else:
                        with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                            Space(style=styles.Height("10px"))
                            Text(f"{_('You are logged in.')} ")
                            Text(_("Welcome back, {0}!").format(str(GetUsername())), styles.Description())

                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text(_("Contributors"), styles.Title())
                    for contributor in contributors:
                        with Container(style=styles.FlexVertical() + styles.Gap("4px")):
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px 0px 0px 0px") + styles.Classname("items-center")):
                                Text(contributor["name"], styles.PlainText())
                                for link in contributor["links"]:
                                    Link(link[0], link[1], style=styles.Classname("text-xs hover:underline"))
                            Text(contributor["description"], styles.Description())
                            
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text(_("Translations"), styles.Title())
                    for language in languages:
                        if not isinstance(language, Language):
                            continue
                        
                        with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Classname("items-start")):
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px 0px 0px 0px") + styles.Classname("items-center")):
                                Text(language.display_name(language.language).capitalize(), styles.PlainText())
                                Text("(" + language.display_name() + ")", styles.Description() + styles.Classname("text-xs"))
                            with Container(style=styles.FlexHorizontal() + styles.Gap("10px")):
                                Link(_("List Contributors"), f"https://weblate.ets2la.com/user/?q=translates:{parse_language(language)}%20contributes:ets2la/backend", styles.Classname("text-xs text-muted-foreground hover:underline"))
                                Text("-")
                                Link(_("Help Translate"), f"https://weblate.ets2la.com/projects/ets2la/backend/{parse_language(language)}", styles.Classname("text-xs text-muted-foreground hover:underline"))
                            
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                    Text(_("Support Development"), styles.Title())
                    with Container(style=styles.FlexVertical() + styles.Gap("10px")):
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text("• " + _("If you like the project and want to support the development, you can do so by donating via Ko-Fi."), styles.Description())
                            Link("Ko-Fi", "https://ko-fi.com/tumppi066", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text("• " + _("If you want to contribute, then I recommend joining the discord server and checking out the github page."), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                            Link("GitHub", "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                        with Container(style=styles.FlexVertical() + styles.Gap("6px") + styles.Padding("0px 0px 0px 0px")):
                            Text("• " + _("If you want to contribute to the translations, then you can do so by joining the discord and contacting a moderator."), styles.Description())
                            Link("Discord", "https://ets2la.com/discord", style=styles.Classname("text-xs hover:underline w-max") + styles.Padding("0px 0px 0px 7px"))
                
                Space(style=styles.Height("10px"))
                with Container(style=styles.FlexVertical() + styles.Gap("16px")):
                    Text(_("Utils"), styles.Title())
                    
                    ButtonWithTitleDescription(
                        self.fix_wipers,
                        title=_("Fix Wipers"),
                        description=_("Did your wipers get stuck? Click the button and alt tab to the game. They should turn off in 5 seconds."),
                        text=_("Activate")
                    )
                    
                    ButtonWithTitleDescription(
                        self.update,
                        title=_("Force an update"),
                        description=_("Do you think there should've been an update? Click this button and the app will restart and check for them."),
                        text=_("Update")
                    )
                    
            Space(style=styles.Height("60px"))