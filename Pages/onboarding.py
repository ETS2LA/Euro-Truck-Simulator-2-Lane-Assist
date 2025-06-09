from ETS2LA.UI import *
from ETS2LA.Utils import translator
from ETS2LA.Utils import settings
from ETS2LA.Window.window import get_transparency, get_on_top 
import time

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
    
    def handle_skip_onboarding(self):
        SendPopup("If you've done the onboarding before, you know how to exit. ETS2LA will not work without doing the onboarding once.")
        
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
            
    def handle_width_change(self, value):
        settings.Set("global", "width", value)
        
    def handle_height_change(self, value):
        settings.Set("global", "height", value)

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
            with Button(action=self.handle_skip_onboarding, type="link"):
                Text("Skip Onboarding", styles.Description() + styles.Classname("text-xs"))
        
        offset = styles.Style()
        offset.margin_bottom = "55px"
        offset.margin_right = "16px"
        with Container(style=styles.Classname("bottom-0 absolute right-0 text-center flex gap-2 items-center") + offset):
            Text("You can change the theme here!", styles.Description() + styles.Classname("text-xs text-muted-foreground"))
            icon_style = styles.Style()
            icon_style.margin_top = "2px"
            icon_style.width = "1.2rem"
            icon_style.height = "1.2rem"
            icon_style.color = "var(--muted-foreground)"
            Icon("arrow-down", icon_style)
                
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
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text("Plugins", styles.Title())
                Text("ETS2LA uses plugins to provide most of it's functionality. You can select between a simple mode, and an advanced mode. This can be changed later on in the settings.", styles.Description() + styles.MaxWidth("520px"))
                Space()
                with Button(action=self.loading_increment, style=styles.Classname("default w-full")):
                    Text("Continue")
                    
            with Container(style=styles.Classname("text-start") + styles.Width("550px") + styles.FlexVertical() + styles.Gap("12px")):
                CheckboxWithTitleDescription(
                    title="Advanced Plugin Mode",
                    description="Enables advanced plugin management features.",
                    default=settings.Get("global", "advanced_plugin_mode", False),
                    changed=self.handle_plugin_mode_change
                )
                with Alert(style=styles.FlexVertical() + styles.Padding("14px") + styles.Width("550px") + styles.Classname("default") + styles.Gap("6px")):
                    with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                        if not settings.Get("global", "advanced_plugin_mode", False):
                            style = styles.Style()
                            style.margin_top = "-4px"
                            style.width = "2rem"
                            style.height = "2rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            Markdown("Keeping **Advanced Plugin Mode** disabled is recommended, however advanced users who want to select plugins themselves might want it enabled.", styles.Classname("text-muted-foreground"))
                        else:
                            style = styles.Style()
                            style.margin_top = "-12px"
                            style.width = "3rem"
                            style.height = "3rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            Markdown("**Advanced Plugin Mode** unlocks manual control of enabled plugins. It also lets you download more plugins from other repositories. Keep in mind that these 3rd party plugins are not *officially* supported by ETS2LA.", styles.Classname("text-muted-foreground"))
                    

    def map_data(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text("Map Data", styles.Title())
                Text("ETS2LA uses pre-extracted map data from the game. We handle the data beforehand and you can then just download it as necessary. Please select the data you need for your current game version below.", styles.Description())
                Space()
                data = settings.Get("Map", "selected_data")
                if data:
                    with Button(action=self.increment_page):
                        Text("Continue")
                else:
                    Text("Waiting for data selection...", styles.Description() + styles.Classname("text-xs"))
            
            import Plugins.Map.utils.data_handler as dh
            index = dh.GetIndex()
            configs = {}
            for key, data in index.items():
                try: config = dh.GetConfig(data["config"])
                except: continue
                if config != {}:
                    configs[key] = config
            
            with Container(style=styles.FlexVertical() + styles.Width("600px")):
                current = settings.Get("Map", "selected_data", "")
                ComboboxWithTitleDescription(
                    title="Selected Data",
                    description="Select the data that matches your game and mods.",
                    default=current,
                    options=[config["name"] for config in configs.values()],
                    search=ComboboxSearch(
                        placeholder="Search data",
                        empty="No matching data found"
                    ),
                    changed=self.handle_data_selection,
                )
                
                if current:
                    config = [config for config in configs.values() if config["name"] == current]
                    if config:
                        config = config[0]
                    else:
                        return
                    
                    with Container(style=styles.FlexVertical() + styles.Gap("12px") + styles.Padding("16px") + styles.Classname("border rounded-md bg-input/10")):
                        with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Padding("0px")):
                            Text(config["name"], styles.Classname("font-semibold"))
                            Text(config["description"], styles.Description() + styles.Classname("text-xs"))
                            
                        with Container(style=styles.FlexVertical() + styles.Gap("4px") + styles.Padding("0px")):
                            for title, credit in config["credits"].items():
                                with Container(style=styles.FlexHorizontal() + styles.Gap("4px") + styles.Padding("0px")):
                                    Text(title, styles.Description() + styles.Classname("text-xs"))
                                    Text(credit, styles.Classname("text-xs"))

                        with Container(style=styles.FlexHorizontal() + styles.Gap("4px") + styles.Padding("0px")):
                            Text("The", styles.Description() + styles.Classname("text-xs"))
                            Text("download size", styles.Description() + styles.Classname("text-xs"))
                            Text("for this data is", styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['packed_size'] / 1024 / 1024:.1f} MB", styles.Classname("text-xs"))
                            Text("that will unpack to a", styles.Description() + styles.Classname("text-xs"))
                            Text("total size", styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['size'] / 1024 / 1024:.1f} MB.", styles.Classname("text-xs"))
                            
                else:
                    with Container(style=styles.FlexVertical() + styles.Gap("12px") + styles.Padding("16px") + styles.Classname("border rounded-md bg-input/10")):
                        Text("No data selected", styles.Classname("font-semibold"))
                        Text("Please select the data you want to use from the dropdown above.", styles.Description() + styles.Classname("text-xs"))

    def size(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text("Window Size", styles.Title())
                Text("ETS2LA bypasses Windows to provide custom window features. Due to this you cannot resize the window normally. These are sliders to manually change the window size.", styles.Description())
                Space()
                with Button(action=self.increment_page):
                    Text("Continue")

            with Container(style=styles.FlexVertical() + styles.Width("600px")):
                SliderWithTitleDescription(
                    title="Window Width",
                    description="Adjust the width of the ETS2LA window.",
                    default=settings.Get("global", "width", 1280),
                    min=400,
                    max=1920,
                    step=10,
                    changed=self.handle_width_change
                )
                SliderWithTitleDescription(
                    title="Window Height",
                    description="Adjust the height of the ETS2LA window.",
                    default=settings.Get("global", "height", 720),
                    min=300,
                    max=1080,
                    step=10,
                    changed=self.handle_height_change
                )
                Space()
                with Alert(style=styles.FlexVertical() + styles.Padding("14px") + styles.Width("550px") + styles.Classname("default") + styles.Gap("6px")):
                    with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                        style = styles.Style()
                        style.margin_top = "4px"
                        style.width = "1.4rem"
                        style.height = "1.4rem"
                        style.color = "var(--muted-foreground)"
                        Icon("triangle", style)
                        Markdown("**Changing the window size may cause pages to display incorrectly**.\nYou can adjust the window scaling by holding Left CTRL and using the scrollwheel.", styles.Classname("text-muted-foreground"))

    last_check = 0
    def window_controls(self): 
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text("Window Controls", styles.Title())
                Text("ETS2LA provides custom window controls that might be useful to you. These can be accessed through the green button in the top right corner.", styles.Description())
                Space()
                with Button(action=self.increment_page):
                    Text("Continue")
            
            with Container(style=styles.FlexVertical() + styles.Width("600px")):
                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("border rounded-md p-4 bg-input/10 items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("info", style)
                    Markdown("**Stay on top**\n\nYou can *left click* the green button to make the ETS2LA window stay on top of other windows.")
                
                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("border rounded-md p-4 bg-input/10 items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("info", style)
                    Markdown("**Transparency**\n\nYou can *right click* the green button to make the ETS2LA window slightly transparent. The amount of transparency can be adjusted in the settings.")

            offset = styles.Style()
            offset.margin_top = "28px"
            offset.margin_right = "34px"
            with Container(style=styles.Classname("top-0 absolute right-0 text-center flex gap-2 items-center") + offset):
                Text("It's this green button!", styles.Description() + styles.Classname("text-xs text-muted-foreground"))
                icon_style = styles.Style()
                icon_style.margin_top = "2px"
                icon_style.width = "1.2rem"
                icon_style.height = "1.2rem"
                icon_style.color = "var(--muted-foreground)"
                Icon("arrow-up", icon_style)

    def complete(self):
        with Container(style=styles.FlexVertical() + styles.Width("400px")):
            Text("Onboarding Complete!", styles.Title())
            Text("You have successfully completed the onboarding process. You can now start using ETS2LA. If you need help, feel free to join our Discord server.", styles.Description() + styles.MaxWidth("520px"))
            Space()
            with Button(action=self.handle_show_sidebar):
                Text("Finish")
            
        if self.show_sidebar:
            manager_button_offset = styles.Style()
            manager_button_offset.margin_top = "220px"
            with Container(style=styles.FlexVertical() + styles.Classname("left-2 top-0 absolute items-center justify-center") + manager_button_offset):
                Text("<- Press this edge to open and close the sidebar.\n      Open the Manager to enable plugins.")

    def render(self):
        pages = {
            0: self.welcome,
            1: self.language,
            2: self.sdk_setup,
            3: self.plugins,
            4: self.map_data,
            5: self.size,
            6: self.window_controls,
            7: self.complete
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
                    with Button(action=self.decrement_page, style=styles.Classname("bg-transparent w-max p-0 h-max"), type="ghost"):
                        Text(f"0{self.page + 1} / 0{len(pages)}", styles.Classname("text-xs text-muted-foreground"))
                    pages[self.page]()
            else:
                with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                    Text("Page not found", style=styles.TextColor("red"))
                    with Button(action=self.decrement_page):
                        Text("Go back", styles.Classname("w-max"))