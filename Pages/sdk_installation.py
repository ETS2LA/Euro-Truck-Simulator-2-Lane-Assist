from ETS2LA.Utils import settings
from ETS2LA.UI import *

from ETS2LA.Utils.translator import Translate
from ETS2LA.Utils.Game import path as game
import ETS2LA.Handlers.sounds as sounds 

import logging
import os

games = game.FindSCSGames()
target_path = "\\bin\\win_x64\\plugins"

files = os.listdir("ETS2LA/Assets/DLLs")
files.pop(files.index("sources.txt"))

def CheckIfInstalled(path: str, detailed: bool = False) -> bool | dict:
    if not os.path.exists(path + target_path):
        if not detailed:
            return False
        
        return_dict = {}
        for file in files:
            return_dict[file] = False
        return return_dict

    return_dict = {}
    for file in files:
        if os.path.exists(path + target_path + "\\" + file):
            return_dict[file] = True
        else:
            if not detailed:
                return False
            
            return_dict[file] = False
    
    if not detailed:
        return True
    
    return return_dict

class Page(ETS2LAPage):
    dynamic = True
    url = "/setup/sdk"
    settings_target = "sdk_installation"
    
    def InstallSDKs(self, *args, **kwargs):
        for game in games:
            if not CheckIfInstalled(game):
                logging.info(f"Installing SDKs for {game}")
                os.makedirs(game + target_path, exist_ok=True)
                for file in files:
                    with open(f"ETS2LA/Assets/DLLs/{file}", "rb") as f:
                        with open(game + target_path + "\\" + file, "wb") as g:
                            g.write(f.read())
        
    def UninstallSDKs(self, *args, **kwargs):
        for game in games:
            if CheckIfInstalled(game):
                logging.info(f"Uninstalling SDKs for {game}")
                for file in files:
                    os.remove(game + target_path + "\\" + file)
    
    def render(self):
        RefreshRate(0.5)
        with Geist():
            with Group("vertical", gap=14, padding=0):
                Title(Translate("sdk_install.title"))
                Description(Translate("sdk_install.description"))
            if games != []:
                all_installed = [CheckIfInstalled(game) for game in games] == [True] * len(games)
                if not all_installed:
                    Button(Translate("install"), Translate("sdk_install.install"), self.InstallSDKs, description=Translate("sdk_install.install_description"))
                else:
                    Button(Translate("uninstall"), Translate("sdk_install.uninstall"), self.UninstallSDKs, description=Translate("sdk_install.uninstall_description"))
            with Group("vertical", padding=4):
                if games == []:
                    Label(Translate("sdk_install.no_games"))
                else:
                    Description(Translate("sdk_install.games"))
                    for found_game in games:
                        information = CheckIfInstalled(found_game, detailed=True)
                        if isinstance(information, bool):
                            continue
                        
                        is_installed = [information[file] for file in files] == [True] * len(files)
                        
                        with Group("vertical", border=True, gap=0):
                            with Group("horizontal", padding=0, gap=4):
                                title = "ETS2 " if "Euro Truck Simulator 2" in found_game else "ATS "
                                title += game.GetVersionForGame(found_game)
                                Label(title, size="sm")
                                Label(Translate("sdk_install.installed") if is_installed else Translate("sdk_install.not_installed"), size="xs")
                            
                            Space(4)
                            
                            with Group("horizontal", padding=0, gap=4):
                                Description("" + found_game)
                                
                            Space(20)
                            with Group("vertical", gap=4, padding=0):
                                for file in files:
                                    with Group("horizontal", padding=0, gap=4):
                                        Description(Translate("sdk_install.installed") if information[file] else Translate("sdk_install.not_installed"))    
                                        Label(file)
                                        
        return RenderUI()