from ETS2LA.Utils.translator import Translate
from ETS2LA.Utils.Game import path as game
from ETS2LA.UI import *

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
        with Geist():
            with Padding(16):
                with Group("vertical", classname="gap-[14px] p-4"):
                    Label(Translate("sdk_install.title"), classname=TITLE_CLASSNAME)
                    Label(Translate("sdk_install.description"), classname=DESCRIPTION_CLASSNAME)

                if games != []:
                    all_installed = [CheckIfInstalled(game) for game in games] == [True] * len(games)

                    with Group("horizontal", classname="p-4 items-center gap-4"):
                        with Group("vertical", classname="gap-[6px]"):
                            Label(Translate("sdk_install.install" if not all_installed else "sdk_install.uninstall"), classname=TITLE_CLASSNAME)
                            Label(Translate("sdk_install.install_description" if not all_installed else "sdk_install.uninstall_description"), classname=DESCRIPTION_CLASSNAME)
                        Button(Translate("install" if not all_installed else "uninstall"), target=self.InstallSDKs if not all_installed else self.UninstallSDKs)
                
                with Group("vertical", classname="p-4 gap-4"):
                    if games == []:
                        Label(Translate("sdk_install.no_games"), classname=TITLE_CLASSNAME)
                    else:
                        Label(Translate("sdk_install.games"), classname=TITLE_CLASSNAME)
                        for game in games:
                            with Group("horizontal", border=True, classname="p-4 items-center"):
                                title = "ETS2 " if "Euro Truck Simulator 2" in game else "ATS "
                                title += Translate("sdk_install.installed") if CheckIfInstalled(game) else Translate("sdk_install.not_installed")
                                Label(title, classname=TITLE_CLASSNAME)
                                Label(game, classname=DESCRIPTION_CLASSNAME)

            return RenderUI()