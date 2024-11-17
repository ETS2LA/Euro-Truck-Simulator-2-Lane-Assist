from ETS2LA.backend import settings
from ETS2LA.UI import *

import ETS2LA.utils.translator as translator
import webbrowser
import time

contributors = [
    {"name": "Tumppi066", "description": "Lead developer and creator of ETS2LA", "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"], ["Ko-Fi", "https://ko-fi.com/tumppi066"]]},
    {"name": "Glas42", "description": 'Navigation Detection, Traffic Light Detection, ETS2LA Lite, "co-owner"', "links": [["Github", "https://github.com/Glas42"]]},
    {"name": "Cloud", "description": "Linux & Unix Port, various improvements and bug fixes", "links": []},
    {"name": "DylDev", "description": "Various additions and improvements, Object Detection AI models & development", "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "truckersmudgeon", "description": "Game data extraction and processing", "links": []},
    {"name": "DTheIcyDragon", "description": "Bug fixes", "links": []},
    {"name": "Roman Sonnik", "description": "Bug fixes", "links": [["Github", "https://github.com/RomanSonnik"]]},
    {"name": "Lun", "description": "Chinese translation, bug fixes", "links": [["Discord", "https://discordapp.com/users/832636302402256898"]]},
    {"name": "atac_helicopter", "description": "Bug fixes", "links": []},
    {"name": "ғʟᴇxғʟᴇxᴇɴ", "description": "Bug fixes", "links": []},
    {"name": "LookAtYourSkill", "description": "Bug fixes", "links": []},
    {"name": "mimi89999", "description": "scs-sdk-controller developer", "links": []},
    {"name": "zhaoyj", "description": "3D models for the visualization", "links": []},
    {"name": "MRUIAW", "description": "Bug fixes, Chinese translations", "links": []},
    {"name": "ViSzKe", "description": "Bug fixes", "links": []},
    {"name": "ziakhan4505", "description": "C++ support, Linux & Unix Port, bug fixes", "links": []},
    {"name": "Piotrke", "description": "Game hooks", "links": []},
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
                    Title("About")
                    Description("ETS2LA is a project that aims to provide an easy to use self driving solution for ETS2 and ATS, if you want to learn more then you can visit the github page or the wiki via the sidebar.")
                    Space(2)
                    with Group("vertical", padding=0):
                        Title("Developers / Contributors")

                        for contributor in contributors:
                            with Group("vertical", gap=6, padding=0):
                                with Group("horizontal", gap=10, padding=0):
                                    Label(contributor["name"])
                                    for link in contributor["links"]:
                                        Link(link[0], link[1], size="xs")
                                Description(contributor["description"])
                    
                    Space(12)
                    with Group("vertical", padding=0, gap=24):
                        Title("Translation Credits")
                        
                        for language in translator.LANGUAGES:
                            with Group("vertical", gap=6, padding=0):
                                with Group("horizontal", gap=10, padding=0):
                                    Label(language)
                                    Description("(" + translator.TranslateToLanguage("name_en", translator.GetCodeForLanguage(language)) + ")", size="xs")
                                credits = translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage(language))
                                if language != "English" and credits == translator.TranslateToLanguage("language_credits", translator.GetCodeForLanguage("English")):
                                    credits = "Language has no credits."
                                Description(credits)
                                
                    Space(12)
                    with Group("vertical", padding=0, gap=16):
                        Title("Support Development")
                        with Group("vertical", gap=6, padding=0):
                            Description("• If you like the project and want to support the development, you can do so by donating via Ko-Fi.")
                            Link("  Ko-Fi", "https://ko-fi.com/tumppi066")
                        with Group("vertical", gap=6, padding=0):
                            Description("• If you want to contribute, then I recommend joining the discord server and checking out the github page.")
                            Link("  Discord", "https://discord.gg/ETS2LA")
                            Link("  Github", "https://github.com/ETS2LA")
                        with Group("vertical", gap=6, padding=0):
                            Description("• If you want to contribute to the translations, then you can do so by joining the discord.")
                            Link("  Discord", "https://discord.gg/ETS2LA")
                    
        return RenderUI()