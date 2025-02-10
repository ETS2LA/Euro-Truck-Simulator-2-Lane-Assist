from ETS2LA.Utils import settings
from ETS2LA.UI import *

from ETS2LA.Utils.translator import Translate
import ETS2LA.Handlers.sounds as sounds 
from ETS2LA.Utils.Game import path as game

import logging
import os

games = game.FindSCSGames()
target_path = "\\bin\\win_x64\\plugins"

files = os.listdir("ETS2LA/Assets/DLLs")
files.pop(files.index("sources.txt"))

def CheckIfInstalled(path: str):
    if not os.path.exists(path + target_path):
        return False

    for file in files:
        if not os.path.exists(path + target_path + "\\" + file):
            return False
    
    return True

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
            with Group("vertical", gap=14, padding=4):
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
                    for game in games:
                        with Group("horizontal", border=True):
                            title = "ETS2 " if "Euro Truck Simulator 2" in game else "ATS "
                            title += Translate("sdk_install.installed") if CheckIfInstalled(game) else Translate("sdk_install.not_installed")
                            Label(title)
                            Description(game)
                                        
        return RenderUI()