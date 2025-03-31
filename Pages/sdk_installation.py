from ETS2LA.Utils import settings
from ETS2LA.UI import *

from ETS2LA.Utils.translator import Translate
from ETS2LA.Utils.Game import path as game
import ETS2LA.Handlers.sounds as sounds 

import logging
import os

games = game.FindSCSGames()
game_versions = [game.GetVersionForGame(found_game) for found_game in games]
target_path = "\\bin\\win_x64\\plugins"

data_versions = os.listdir("ETS2LA/Assets/DLLs")
files_for_version = {}
for version in data_versions:
    files_for_version[version] = os.listdir(f"ETS2LA/Assets/DLLs/{version}")
    files_for_version[version].pop(files_for_version[version].index("sources.txt"))

def CheckIfInstalled(path: str, version: str, detailed: bool = False) -> bool | dict:
    files = files_for_version[version]
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
        for game_to_install, version in zip(games, game_versions):
            if version == "Unknown":
                logging.warning(f"Could not find version for {game_to_install}, skipping installation")
                continue
            
            if not CheckIfInstalled(game_to_install, version):
                logging.info(f"Installing SDKs for {game_to_install}")
                os.makedirs(game_to_install + target_path, exist_ok=True)
                files = files_for_version[version]
                for file in files:
                    with open(f"ETS2LA/Assets/DLLs/{version}/{file}", "rb") as f:
                        with open(game_to_install + target_path + "\\" + file, "wb") as g:
                            g.write(f.read())
        
    def UninstallSDKs(self, *args, **kwargs):
        for game_to_install, version in zip(games, game_versions):
            if version == "Unknown":
                logging.warning(f"Could not find version for {game}, skipping uninstallation")
                continue
            
            if CheckIfInstalled(game_to_install, version):
                logging.info(f"Uninstalling SDKs for {game_to_install}")
                files = files_for_version[version]
                for file in files:
                    os.remove(game_to_install + target_path + "\\" + file)
    
    def render(self):
        RefreshRate(0.5)
        with Geist():
            with Group("vertical", gap=14, padding=0):
                Title(Translate("sdk_install.title"))
                Description(Translate("sdk_install.description"))
            if games != []:
                all_installed = [CheckIfInstalled(game, version) for game, version in zip(games, game_versions)] == [True] * len(games)
                if not all_installed:
                    Button(Translate("install"), Translate("sdk_install.install"), self.InstallSDKs, description=Translate("sdk_install.install_description"))
                else:
                    Button(Translate("uninstall"), Translate("sdk_install.uninstall"), self.UninstallSDKs, description=Translate("sdk_install.uninstall_description"))
            with Group("vertical", padding=4):
                if games == []:
                    Label(Translate("sdk_install.no_games"))
                else:
                    Description(Translate("sdk_install.games"))
                    for found_game, version in zip(games, game_versions):
                        information = CheckIfInstalled(found_game, version, detailed=True)
                        if isinstance(information, bool):
                            continue
                        
                        files = files_for_version[version]
                        is_installed = [information[file] for file in files] == [True] * len(files)
                        
                        with Group("vertical", border=True, gap=0):
                            with Group("horizontal", padding=0, gap=4, classname="items-center"):
                                title = "ETS2 " if "Euro Truck Simulator 2" in found_game else "ATS "
                                title += version
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