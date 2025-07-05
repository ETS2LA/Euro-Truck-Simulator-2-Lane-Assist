from ETS2LA.UI import *

from ETS2LA.Utils.translator import _
from ETS2LA.Utils.Game import path as game
from tkinter import filedialog

import logging
import psutil
import os

games = game.FindSCSGames()
game_versions = [game.GetVersionForGame(found_game) for found_game in games]
target_path = "\\bin\\win_x64\\plugins"

data_versions = os.listdir("ETS2LA/Assets/DLLs")
files_for_version = {}
for version in data_versions:
    files_for_version[version] = os.listdir(f"ETS2LA/Assets/DLLs/{version}")
    files_for_version[version].pop(files_for_version[version].index("sources.txt"))

def IsGameRunning():
    execs = ["amtrucks", "eurotrucks2"]
    for p in psutil.process_iter():
        for game in execs:
            try:
                if game in p.name():
                    return True
            except psutil.NoSuchProcess:
                pass # Usually indicates that a process has exited
        
    return False

def GetFilesForVersion(version: str) -> list[str]:
    if version not in files_for_version:
        return []
    return files_for_version[version]

def CheckIfInstalled(path: str, version: str, detailed: bool = False) -> bool | dict:
    files = GetFilesForVersion(version)
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
    url = "/settings/sdk"
    settings_target = "sdk_installation"
    onboarding_mode = False

    def CanContinue(self):
        for game in games:
            if CheckIfInstalled(game, game_versions[games.index(game)]):
                return True
        
        return False
    
    def OpenSources(self, version: str):
        if os.path.exists("ETS2LA/Assets/DLLs/" + version + "\\sources.txt"):
            os.startfile("ETS2LA/Assets/DLLs/" + version + "\\sources.txt")
        else:
            SendPopup("No sources found.", "error")
    
    def InstallSDK(self, game: str):
        version = game_versions[games.index(game)]
        if version == "Unknown":
            logging.warning(_("Could not find version for {game}, skipping installation").format(game=game))
            return
        
        try:
            if not CheckIfInstalled(game, version):
                logging.info(_("Installing SDKs for {game}").format(game=game))
                os.makedirs(game + target_path, exist_ok=True)
                files = GetFilesForVersion(version)
                for file in files:
                    with open(f"ETS2LA/Assets/DLLs/{version}/{file}", "rb") as f:
                        with open(game + target_path + "\\" + file, "wb") as g:
                            g.write(f.read())

                SendPopup(_("SDKs for {game} installed successfully.").format(game='ETS2 ' if 'Euro Truck Simulator 2' in game else 'ATS '), "success")
            else:
                logging.info(_("SDKs for {game} already installed, skipping installation").format(game=game))
        except Exception as e:
            SendPopup(_("Please make sure the game is closed and try again. {error}").format(error=e.args), "error")
            logging.error(_("Error installing SDKs for {game}, please make sure the game is closed.").format(game=game))
    
    def UninstallSDK(self, game: str):
        version = game_versions[games.index(game)]
        if version == "Unknown":
            logging.warning(_("Could not find version for {game}, skipping uninstallation").format(game=game))
            return
        
        try:
            if CheckIfInstalled(game, version):
                logging.info(_("Uninstalling SDKs for {game}").format(game=game))
                files = GetFilesForVersion(version)
                for file in files:
                    os.remove(game + target_path + "\\" + file)

                SendPopup(_("SDKs for {game} uninstalled successfully.").format(game='ETS2 ' if 'Euro Truck Simulator 2' in game else 'ATS '), "success")
            else:
                logging.info(_("SDKs for {game} not installed, skipping uninstallation").format(game=game))
        except Exception as e:
            SendPopup(_("Please make sure the game is closed and try again. {error}").format(error=e.args), "error")
            logging.error(_("Error uninstalling SDKs for {game}, please make sure the game is closed.").format(game=game))
    
    def AddGame(self):
        path = filedialog.askdirectory(title=_("Select the game directory"))
        version = game.GetVersionForGame(path)
        if version == "Unknown":
            SendPopup(_("Could not find version for the selected game, please select a valid game directory.").format(path=path), "error")
            logging.warning(_("Could not find version for {path}, skipping installation").format(path=path))
            return
        
        games.append(path)
        game_versions.append(version)
        SendPopup(_("Found game version {version}.").format(version=version), "success")
        
    def OpenPath(self, path: str):
        if os.path.exists(path):
            os.startfile(path)
        else:
            SendPopup(_("Path {path} does not exist.").format(path=path), "error")

    def render(self):
        if not self.onboarding_mode:
            TitleAndDescription(
                _("SDK Setup"),
                _("Check that you have the necessary DLLs installed for us to communicate with the game."),
            )
        
        with Container(styles.FlexVertical() + styles.Gap("24px")):
            if games == []:
                red_text = styles.Style()
                red_text.color = "var(--destructive)"
                red_text.font_weight = "bold"
                Text(_("We could not find any SCS games on your system. Please note that ETS2LA will only work with legitimate versions downloaded from Steam."), red_text)
                with Button(action=self.AddGame):
                    Text(_("Select directory manually"))
            else:
                running = IsGameRunning()

                for found_game, version in zip(games, game_versions):
                    not_supported = False
                    
                    file_install_status = []
                    if files_for_version.get(version) is None:
                        not_supported = True
                        is_installed = False
                    else:
                        file_install_status = CheckIfInstalled(found_game, version, detailed=True)
                        if isinstance(file_install_status, bool):
                            not_supported = True
                            file_install_status = []
                            is_installed = False
                        else:    
                            files = GetFilesForVersion(version)
                            is_installed = [file_install_status[file] for file in files] == [True] * len(files)
                        
                    
                    with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("rounded-md border p-4 bg-input/10")):
                        with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                            title = "ETS2 " if "Euro Truck Simulator 2" in found_game else "ATS "
                            title += version
                            Text(title, styles.Classname("font-semibold"))
                            Text(_("- Installed") if is_installed else _("- Not Installed"), styles.Description())
                        
                        with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                            with Button(action=self.OpenPath, name=found_game, type="link"):
                                Text(found_game, styles.Description() + styles.Classname("text-xs"))
                        
                        if not_supported:
                            red_text = styles.Style()
                            red_text.color = "var(--destructive)"
                            Text(_("This game version is not supported"), red_text)
                        
                        else:   
                            Space(styles.Height("4px"))
                            with Container(styles.FlexHorizontal() + styles.Gap("8px") + styles.Width("100%") + styles.Classname("justify-start w-full")):             
                                icon_style = styles.Style()
                                icon_style.color = "var(--muted-foreground)"
                                icon_style.width = "18px"
                                icon_style.height = "18px"
                                with Tooltip() as t:
                                    with t.trigger as tr:
                                        tr.style = styles.Classname("border rounded-md p-2 bg-input/10 hover:bg-input/30 transition-all")
                                        Icon("files", icon_style)
                                    with t.content:
                                        with Container(styles.FlexVertical() + styles.Gap("4px") + styles.Padding("4px")):
                                            if file_install_status == {}:
                                                Text(_("No files found."), styles.Description())
                                            else:
                                                text_style = styles.Style()
                                                text_style.color = "var(--foreground)"
                                                for file in file_install_status:
                                                    with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                                                        Text(file, text_style)
                                                        Text(_("- Installed") if file_install_status[file] else _("- Not Installed"), styles.Description())

                                                with Button(action=self.OpenSources, name=version, type="link", style=styles.Padding("12px 0px 0px 0px") + styles.Classname("w-max h-max") + styles.Gap("6px")):
                                                    Icon("file")
                                                    Text(_("File Sources"), styles.Classname("text-xs"))

                                if running:
                                    with Tooltip() as t:
                                        with t.trigger as tr:
                                            tr.style = styles.Classname("w-full")
                                            if is_installed:
                                                with Button(name=found_game, action=self.UninstallSDK, style=styles.Classname("default w-full"), enabled=not running):
                                                    Text(_("Uninstall SDKs"))
                                            else:
                                                with Button(name=found_game, action=self.InstallSDK, style=styles.Classname("default w-full"), enabled=not running):
                                                    Text(_("Install SDKs"))

                                        with t.content:
                                            text_style = styles.Style()
                                            text_style.color = "var(--foreground)"
                                            Text(_("Please close the game before installing or uninstalling SDKs."), text_style)

                                else:
                                    if is_installed:
                                        with Button(name=found_game, action=self.UninstallSDK, style=styles.Width("90.5%" if self.onboarding_mode else "93%")):
                                            Text(_("Uninstall SDKs"))
                                    else:
                                        with Button(name=found_game, action=self.InstallSDK, style=styles.Width("90.5%" if self.onboarding_mode else "93%")):
                                            Text(_("Install SDKs"))
