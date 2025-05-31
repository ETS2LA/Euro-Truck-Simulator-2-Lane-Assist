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
    
    show_sidebar = False

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
        
    def handle_show_sidebar(self):
        self.show_sidebar = not self.show_sidebar
        
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
        with Container(style=styles.FlexVertical() + styles.Width("400px")):
            Text("Welcome to ETS2LA!", styles.Title())
            Text("Let's get you setup with the basics right off the bat! Press the button below to continue.", styles.Description())
        
        with Button(action=self.increment_page):
            Text("Continue")
            
        with Container(style=styles.Classname("bottom-2 absolute left-0 right-0 text-center")):
            with Button(action=self.decrement_page, type="link"):
                Text("Skip Onboarding", styles.Description() + styles.Classname("text-xs"))
                
    def language(self):
        with Container(style=styles.FlexHorizontal() + styles.Classname("items-center") + styles.Width("800px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("400px")):
                Text("Language Selection", styles.Title())
                Text("Please select your preferred language for ETS2LA. This option can be changed later in the options. All our translations are community made!", styles.Description())
                Space()
                with Button(action=self.increment_page, style=styles.Classname("default w-full")):
                    Text("Continue")
                    
            with Container(style=styles.FlexVertical()):
                ComboboxWithTitleDescription(
                    title="Language",
                    description="Select your preferred language for ETS2LA.",
                    options=translator.LANGUAGES,
                    default=settings.Get("global", "language", default="English"),  # type: ignore
                    changed=self.change_language,
                    search=ComboboxSearch("Search Languages...", "Help us translate on discord!"),
                    style=styles.MinWidth("300px")
                )
                
                with Alert(style=styles.Padding("14px") + styles.Width("400px") + styles.Classname("default")):
                    with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                        style = styles.Style()
                        style.margin_top = "2px"
                        style.width = "1rem"
                        style.height = "1rem"
                        style.color = "var(--muted-foreground)"
                        Icon("info", style)
                        Text(translator.Translate("credits"), styles.Classname("text-muted-foreground"))
            
                
    def sdk_setup(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
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
                
            with Container(style=styles.FlexVertical() + styles.Width("470px")):
                Text("SDK Setup", styles.Title())
                Text("To get started, we need to set up the SDK. This will allow ETS2LA to interact with your game. To the right you will find a list of games, click install on one of them and then continue.", styles.Description())  
                Space()
                if not is_installed:
                    Text("Waiting for SDK installation...", styles.Description() + styles.Classname("text-xs"))
                else:
                    with Button(action=self.increment_page):
                        Text("Continue")

            sdk_page.render()

    def plugins(self):
        with Container(style=styles.FlexVertical() + styles.Width("520px")):
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
        with Container(style=styles.FlexVertical() + styles.Width("520px")):
            Text("Map Data", styles.Title())
            Text("ETS2LA uses pre-extracted map data from the game. We handle the data beforehand and you can then just download it as necessary. Please select the data you need for your current game version below.", styles.Description())
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
        with Container(style=styles.FlexVertical() + styles.Width("400px")):
            Text("Onboarding Complete!", styles.Title())
            Text("You have successfully completed the onboarding process. You can now start using ETS2LA. If you need help, feel free to join our Discord server.", styles.Description() + styles.MaxWidth("520px"))
            Space()
            with Button(action=self.handle_show_sidebar):
                Text("Finish")
            
        if self.show_sidebar:
            with Container(style=styles.FlexVertical() + styles.Classname("left-2 top-0 bottom-0 absolute items-center justify-center")):
                Text("<- Press this edge to open\n      and close the sidebar")

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
        
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            if self.page in pages:
                with Container(style=styles.FlexVertical() + styles.Classname("justify-center gap-4 text-left") + styles.Height("100vh")):
                    Text(f"0{self.page + 1} / 0{len(pages)}", styles.Classname("text-xs text-muted-foreground"))
                    pages[self.page]()
            else:
                with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                    Text("Page not found", style=styles.TextColor("red"))
                    with Button(action=self.decrement_page):
                        Text("Go back", styles.Classname("w-max"))