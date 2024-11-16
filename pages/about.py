from ETS2LA.backend import settings
from ETS2LA.UI import *

import time

contributors = [
    {"name": "Tumppi066", "description": "Lead developer and creator of ETS2LA", "links": [["Github", "https://github.com/Tumppi066"], ["Youtube", "https://www.youtube.com/@Tumppi066"]]},
    {"name": "Glas42", "description": 'Navigation Detection, Traffic Light Detection, ETS2LA Lite, "co-owner"', "links": [["Github", "https://github.com/Glas42"]]},
    {"name": "Cloud", "description": "Linux & Unix Port, various improvements and bug fixes", "links": []},
    {"name": "DylDev", "description": "Various additions and improvements, Object Detection AI models & development", "links": [["Github", "https://github.com/DylDevs"], ["Youtube", "https://www.youtube.com/@DylDev"]]},
    {"name": "truckersmudgeon", "description": "Game data extraction and processing", "links": []},
    {"name": "DTheIcyDragon", "description": "Bug fixes", "links": []},
    {"name": "Roman Sonnik", "description": "Bug fixes", "links": [["Github", "https://github.com/RomanSonnik"]]},
    {"name": "Lun", "description": "Chinese translation, bug fixes", "links": []},
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
                    Space(4)
                    with Group("vertical", padding=0):
                        Title("Developers / Contributors")

                        for contributor in contributors:
                            with Group("vertical", gap=6, padding=0):
                                with Group("horizontal", gap=10, padding=0):
                                    Label(contributor["name"])
                                    for link in contributor["links"]:
                                        Link(link[0], link[1], size="xs")
                                Description(contributor["description"])
                    
        return RenderUI()