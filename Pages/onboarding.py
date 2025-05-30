from ETS2LA.UI import *
from ETS2LA.Utils import translator
from ETS2LA.Utils import settings

from Pages.sdk_installation import Page as SDKInstallPage
from Pages.sdk_installation import games, game_versions, files_for_version, CheckIfInstalled

sdk_page = SDKInstallPage()
sdk_page.onboarding_mode = True

class Page(ETS2LAPage):
    url = "/onboarding"
    page = 0
    
    # 2 = render loading page
    # 1 = start rendering
    # 0 = loading state done
    increment_and_load = 0

    def loading_increment(self):
        self.increment_and_load = 2

    def increment_page(self):
        self.page += 1

    def decrement_page(self):
        if self.page > 0:
            self.page -= 1
            
    def UninstallSDK(self, game: str):
        sdk_page.UninstallSDK(game)
        
    def InstallSDK(self, game: str):
        sdk_page.InstallSDK(game)
        
    def OpenSources(self, version: str):
        sdk_page.OpenSources(version)
        
    def AddGame(self):
        sdk_page.AddGame()
        
    def OpenPath(self, path: str):
        sdk_page.OpenPath(path)
        
    def handle_plugin_mode_change(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("global", "advanced_plugin_mode", False)
        settings.Set("global", "advanced_plugin_mode", value)

    def change_language(self, language: str):
        settings.Set("global", "language", language)
        
    def handle_data_selection(self, value):
        if value:
            settings.Set("Map", "selected_data", value)
        else:
            settings.Set("Map", "selected_data", "")

    def loading(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            Text("Loading...", styles.Title())
            Text("We are doing something that is taking a while. Just sit tight and relax!", styles.Description())

    def welcome(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            Text("Welcome to ETS2LA!", styles.Title())
            Text("Let's get you setup with the basics right off the bat!\nJust press the button below to continue.", styles.Description())
            
            with Button(action=self.increment_page):
                Text("Continue")
                
            with Container(style=styles.Classname("bottom-2 absolute left-0 right-0 text-center")):
                with Button(action=self.decrement_page, type="link"):
                    Text("Skip Onboarding", styles.Description() + styles.Classname("text-xs"))
                
    def language(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4") + styles.Height("100vh")):
            with Container(style=styles.FlexVertical() + styles.Classname("items-center") + styles.Width("520px")):
                ComboboxWithTitleDescription(
                    title="Language Selection",
                    description="Please select your preferred language for the application.",
                    default=settings.Get("global", "language", default="English"),  # type: ignore
                    options=translator.LANGUAGES,
                    changed=self.change_language,
                    side=Side.TOP,
                    search=ComboboxSearch("Search Languages...", "Help us translate on discord!"),
                    style=styles.MinWidth("200px")
                )
                Space()
                with Button(action=self.loading_increment, style=styles.Classname("default w-full")):
                    Text("Continue")
                
    def sdk_setup(self):
        with Container(style=styles.FlexVertical() + styles.Classname("relative justify-center gap-4 text-center items-center") + styles.Height("100vh")):
            with Container(style=styles.FlexVertical() + styles.Width("520px")):
                Text("SDK Setup", styles.Title())
                Text("To get started, we need to set up the SDK. This will allow ETS2LA to interact with your game. Below you will find a list of games, click install on one of them and then continue.", styles.Description())
                Space()
                sdk_page.render()
                
                is_installed = False
                for found_game, version in zip(games, game_versions):
                    if files_for_version.get(version) is None:
                        continue
                    else:
                        file_install_status = CheckIfInstalled(found_game, version, detailed=True)
                        files = files_for_version[version]
                        if isinstance(file_install_status, bool):
                            continue
                        
                        is_installed = [file_install_status[file] for file in files] == [True] * len(files)
                        if is_installed:
                            break
                        
                Space()
                if not is_installed:
                    Text("Waiting for SDK installation...", styles.Description() + styles.Classname("text-xs"))
                else:
                    with Button(action=self.increment_page):
                        Text("Continue")

    def plugins(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                Text("Plugins", styles.Title())
                Text("ETS2LA uses plugins to provide most of it's functionality. Below you can select between a simple mode, and an advanced mode. This can be changed later on in the settings.", styles.Description() + styles.MaxWidth("520px"))
                Space()
                with Container(style=styles.Classname("text-start w-full")):
                    CheckboxWithTitleDescription(
                        title="Advanced Plugin Mode",
                        description="Enables advanced plugin management features.",
                        default=settings.Get("global", "advanced_plugin_mode", False),
                        changed=self.handle_plugin_mode_change
                    )
                
                Space()
                with Button(action=self.loading_increment, style=styles.Classname("default w-full")):
                    Text("Continue")

    def map_data(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4") + styles.Height("100vh")):
            with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                Text("Map Data", styles.Title())
                Text("ETS2LA uses map data to provide a better experience. We extract the data before hand and you can then just download it as necessary. Please select the data you need for your current game version below.", styles.Description() + styles.Classname("text-center"))
                Space()
                
                import Plugins.Map.utils.data_handler as dh
                index = dh.GetIndex()
                configs = {}
                for key, data in index.items():
                    try: config = dh.GetConfig(data["config"])
                    except: continue
                    if config != {}:
                        configs[key] = config
                
                ComboboxWithTitleDescription(
                    title="Selected Data",
                    description="Select the data that matches your game and mods.",
                    default=settings.Get("Map", "SelectedData", ""),
                    options=[config["name"] for config in configs.values()],
                    search=ComboboxSearch(
                        placeholder="Search data",
                        empty="No matching data found"
                    ),
                    changed=self.handle_data_selection,
                )
                
                Space()
                with Button(action=self.increment_page, style=styles.Classname("default w-full")):
                    Text("Continue")

    def complete(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            with Container(style=styles.FlexVertical() + styles.Classname("left-2 top-0 bottom-0 absolute items-center justify-center")):
                Text("<- Press this edge to open / close the sidebar.")

    def render(self):
        pages = {
            0: self.welcome,
            1: self.language,
            2: self.sdk_setup,
            3: self.plugins,
            4: self.map_data,
            5: self.complete
        }
        
        if self.increment_and_load == 2:
            self.loading()
            self.increment_and_load = 1
            return
        
        elif self.increment_and_load == 1:
            self.increment_page()
            self.loading()
            self.increment_and_load = 0
            return
        
        if self.page in pages:
            pages[self.page]()
        else:
            with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
                with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                    Text("Page not found", style=styles.TextColor("red"))
                    with Button(action=self.decrement_page):
                        Text("Go back", styles.Classname("w-max"))