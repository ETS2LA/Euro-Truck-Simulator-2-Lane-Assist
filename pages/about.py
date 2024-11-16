from ETS2LA.backend import settings
from ETS2LA.UI import *

import time

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
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("Tumppi066")
                            Description("Lead developer and creator of ETS2LA")
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("Glas42")
                            Description('Navigation Detection, Traffic Light Detection, ETS2LA Lite, "co-owner"')
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("Cloud")
                            Description("Linux port, various improvements and bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("DylDev")
                            Description("Various additions and improvements, Object Detection AI models & development")
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("truckersmudgeon")
                            Description("Game data extraction and processing")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("DTheIcyDragon")
                            Description("Bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("Roman Sonnik")
                            Description("Bug fixes")
                            
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("Lun")
                            Description("Chinese translations, bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("atac_helicopter")
                            Description("Bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("ғʟᴇxғʟᴇxᴇɴ")
                            Description("Bug fixes")
                           
                        with Group("vertical", gap=6, padding=0):
                            Label("LookAtYourSkill")
                            Description("Bug fixes") 
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("mimi89999")
                            Description("scs-sdk-controller developer")
                        
                        with Group("vertical", gap=6, padding=0):
                            Label("zhaoyj")
                            Description("3D models for the visualization")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("MRUIAW")
                            Description("Bug fixes, Chinese translations")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("ViSzKe")
                            Description("Bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("ziakhan4505")
                            Description("C++ support, bug fixes")
                            
                        with Group("vertical", gap=6, padding=0):
                            Label("Piotrke")
                            Description("Game hooks")
                    
        return RenderUI()