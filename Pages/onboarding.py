from ETS2LA.UI import *
from ETS2LA.Utils.translator import languages, parse_language
from ETS2LA.Utils.translator import _
from langcodes import Language
from ETS2LA.Utils import settings
from ETS2LA.Window.utils import get_transparency, get_on_top 
import time

from Pages.sdk_installation import Page as SDKInstallPage
from Pages.sdk_installation import games, game_versions, files_for_version, CheckIfInstalled

sdk_page = SDKInstallPage()
sdk_page.onboarding_mode = True

class Page(ETS2LAPage):
    url = "/onboarding"
    refresh_rate = 2
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
        SendPopup(_("If you've done the onboarding before, you know how to exit. ETS2LA will not work without doing the onboarding once."))

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

    def handle_high_priority_change(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("global", "high_priority", True)
            
        settings.Set("global", "high_priority", value)

    def loading(self):
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100vh")):
            Text(_("Loading..."), styles.Title())
            Text(_("We are doing something that is taking a while. Just sit tight and relax!"), styles.Description())

    def welcome(self):
        with Container(style=styles.FlexVertical() + styles.Width("400px")):
            Text(_("Welcome to ETS2LA!"), styles.Title())
            Text(_("Let's get you setup with the basics right off the bat! Press the button below to continue."), styles.Description())
        
        with Button(action=self.increment_page):
            Text(_("Continue"))
        
        with Container(style=styles.Classname("bottom-2 absolute left-0 right-0 text-center")):
            with Button(action=self.handle_skip_onboarding, type="link"):
                Text(_("Skip Onboarding"), styles.Description() + styles.Classname("text-xs"))

        offset = styles.Style()
        offset.margin_bottom = "55px"
        offset.margin_right = "16px"
        with Container(style=styles.Classname("bottom-0 absolute right-0 text-center flex gap-2 items-center") + offset):
            # TRANSLATORS: Try to keep the length of this text the same, it affects the location of the arrow icon pointing to the theme selector.
            Text(_("You can change the theme here!"), styles.Description() + styles.Classname("text-xs text-muted-foreground"))
            icon_style = styles.Style()
            icon_style.margin_top = "2px"
            icon_style.width = "1.2rem"
            icon_style.height = "1.2rem"
            icon_style.color = "var(--muted-foreground)"
            Icon("arrow-down", icon_style)
                
    def language(self):
        with Container(style=styles.FlexHorizontal() + styles.Classname("items-center") + styles.Width("800px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("400px")):
                Text(_("Language Selection"), styles.Title())
                Text(_("Please select your preferred language for ETS2LA. This option can be changed later in the options. All our translations are community made!"), styles.Description())
                Space()
                with Button(action=self.increment_page, style=styles.Classname("default w-full")):
                    Text(_("Continue"))
            
            current = settings.Get("global", "language", default="English")
            current = Language.find(current)
            
            with Container(style=styles.FlexVertical()):
                ComboboxWithTitleDescription(
                    title=_("Language"),
                    description=_("Select your preferred language for ETS2LA."),
                    default=current.display_name().capitalize(),
                    options=[language.display_name().capitalize() for language in languages],
                    changed=self.change_language,
                    search=ComboboxSearch(_("Search Languages..."), _("Help us translate on discord!")),
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
                        with Container(styles.FlexVertical() + styles.Gap("4px")):
                            Text(f"This translation is {_.get_percentage():.2f}% complete.", styles.Classname("text-muted-foreground"))
                            with Container(styles.FlexHorizontal() + styles.Gap("8px")):
                                Link(_("List Contributors"), f"https://weblate.ets2la.com/user/?q=translates:{parse_language(current)}%20contributes:ets2la/backend", styles.Classname("text-sm text-muted-foreground hover:underline"))
                                Text("-")
                                Link(_("Help Translate"), f"https://weblate.ets2la.com/projects/ets2la/backend/{parse_language(current)}", styles.Classname("text-sm text-muted-foreground hover:underline"))
                        
    def sdk_setup(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("470px")):
                Text(_("SDK Setup"), styles.Title())
                Text(_("To get started, we need to set up the SDK. This will allow ETS2LA to interact with your game. To the right you will find a list of games, click install on one of them and then continue."), styles.Description())
                Space()
                if not sdk_page.CanContinue():
                    Text(_("Waiting for SDK installation..."), styles.Description() + styles.Classname("text-xs"))
                else:
                    with Button(action=self.increment_page):
                        Text(_("Continue"))

            sdk_page.render()

    def plugins(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text(_("Plugins"), styles.Title())
                Text(_("ETS2LA uses plugins to provide most of it's functionality. You can select between a simple mode, and an advanced mode. This can be changed later on in the settings."), styles.Description() + styles.MaxWidth("520px"))
                Space()
                with Button(action=self.increment_page, style=styles.Classname("default w-full")):
                    Text(_("Continue"))

            with Container(style=styles.Classname("text-start") + styles.Width("550px") + styles.FlexVertical() + styles.Gap("12px")):
                CheckboxWithTitleDescription(
                    title=_("Advanced Plugin Mode"),
                    description=_("Enables advanced plugin management features. Can be changed at any time in the plugin manager."),
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
                            Markdown(_("Keeping **Advanced Plugin Mode** disabled is recommended, however advanced users who want to select plugins themselves might want it enabled."), styles.Classname("text-muted-foreground"))
                        else:
                            style = styles.Style()
                            style.margin_top = "-12px"
                            style.width = "3rem"
                            style.height = "3rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            Markdown(_("**Advanced Plugin Mode** unlocks manual control of enabled plugins. It also lets you download more plugins from other repositories. Keep in mind that these 3rd party plugins are not *officially* supported by ETS2LA."), styles.Classname("text-muted-foreground"))

    def priority(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text(_("High Priority Mode"), styles.Title())
                Text(_("ETS2LA can automatically tell your operating system that it should run in a high priority mode. This is recommended especially on lower end devices."), styles.Description() + styles.MaxWidth("520px"))
                Space()
                with Button(action=self.loading_increment, style=styles.Classname("default w-full")):
                    Text(_("Continue"))
                    
            with Container(style=styles.Classname("text-start") + styles.Width("550px") + styles.FlexVertical() + styles.Gap("12px")):
                state = settings.Get("global", "high_priority", True)
                CheckboxWithTitleDescription(
                    title=_("High Priority"),
                    description=_("Run ETS2LA in high priority mode. This will tell your OS to give more CPU time to ETS2LA, which can improve performance at the cost of other applications."),
                    default=state, # type: ignore
                    changed=self.handle_high_priority_change
                )
                if not state:
                    with Alert(style=styles.FlexVertical() + styles.Padding("14px") + styles.Classname("default") + styles.Gap("6px")):
                        with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                            style = styles.Style()
                            style.margin_top = "2px"
                            style.width = "1rem"
                            style.height = "1rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            Markdown(_("You'll need to restart ETS2LA after doing the onboarding to apply this change."), styles.Classname("text-muted-foreground"))

    def map_data(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text(_("Map Data"), styles.Title())
                Text(_("ETS2LA uses pre-extracted map data from the game. We handle the data beforehand and you can then just download it as necessary. Please select the data you need for your current game version below."), styles.Description())
                Space()
                data = settings.Get("Map", "selected_data")
                if data:
                    with Button(action=self.increment_page):
                        Text(_("Continue"))
                else:
                    Text(_("Waiting for data selection..."), styles.Description() + styles.Classname("text-xs"))

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
                    title=_("Selected Data"),
                    description=_("Select the data that matches your game and mods."),
                    default=current,
                    options=[config["name"] for config in configs.values()],
                    search=ComboboxSearch(
                        placeholder=_("Search data"),
                        empty=_("No matching data found")
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
                            Text(_("The"), styles.Description() + styles.Classname("text-xs"))
                            Text(_("download size"), styles.Description() + styles.Classname("text-xs"))
                            Text(_("for this data is"), styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['packed_size'] / 1024 / 1024:.1f} MB", styles.Classname("text-xs"))
                            Text(_("that will unpack to a"), styles.Description() + styles.Classname("text-xs"))
                            Text(_("total size"), styles.Description() + styles.Classname("text-xs"))
                            Text(f"{config['size'] / 1024 / 1024:.1f} MB.", styles.Classname("text-xs"))
                            
                else:
                    with Container(style=styles.FlexVertical() + styles.Gap("12px") + styles.Padding("16px") + styles.Classname("border rounded-md bg-input/10")):
                        Text(_("No data selected"), styles.Classname("font-semibold"))
                        Text(_("Please select the data you want to use from the dropdown above."), styles.Description() + styles.Classname("text-xs"))

    def size(self):
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text(_("Window Size"), styles.Title())
                Text(_("ETS2LA bypasses Windows to provide custom window features. Due to this you cannot resize the window normally. These are sliders to manually change the window size."), styles.Description())
                Space()
                with Button(action=self.increment_page):
                    Text(_("Continue"))

            with Container(style=styles.FlexVertical() + styles.Width("600px")):
                SliderWithTitleDescription(
                    title=_("Window Width"),
                    description=_("Adjust the width of the ETS2LA window."),
                    default=settings.Get("global", "width", 1280),
                    min=400,
                    max=1920,
                    step=10,
                    changed=self.handle_width_change
                )
                SliderWithTitleDescription(
                    title=_("Window Height"),
                    description=_("Adjust the height of the ETS2LA window."),
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
                        # TRANSLATORS: The newline in this text is fairly important for the layout, you should try to keep it if possible.
                        Markdown(_("**Changing the window size may cause pages to display incorrectly**.\nYou can adjust the window scaling by holding Left CTRL and using the scrollwheel."), styles.Classname("text-muted-foreground"))

    last_check = 0
    def window_controls(self): 
        with Container(style=styles.FlexHorizontal() + styles.Width("1000px") + styles.Gap("48px")):
            with Container(style=styles.FlexVertical() + styles.Width("450px")):
                Text(_("Window Controls"), styles.Title())
                Text(_("ETS2LA provides custom window controls that might be useful to you. These can be accessed through the green button in the top right corner."), styles.Description())
                Space()
                with Button(action=self.increment_page):
                    Text(_("Continue"))

            with Container(style=styles.FlexVertical() + styles.Width("600px")):
                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("border rounded-md p-4 bg-input/10 items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("info", style)
                    # TRANSLATORS: Please keep the newlines in the text, they are important for the layout.
                    Markdown(_("**Stay on top**\n\nYou can *left click* the green button to make the ETS2LA window stay on top of other windows."))

                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("border rounded-md p-4 bg-input/10 items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("info", style)
                    # TRANSLATORS: Please keep the newlines in the text, they are important for the layout.
                    Markdown(_("**Transparency**\n\nYou can *right click* the green button to make the ETS2LA window slightly transparent. The amount of transparency can be adjusted in the settings."))

                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("border rounded-md p-4 bg-input/10 items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("info", style)
                    # TRANSLATORS: Please keep the newlines in the text, they are important for the layout.
                    Markdown(_("**Fullscreen**\n\nYou can *middle click* the green button to make the ETS2LA window fullscreen."))


            offset = styles.Style()
            offset.margin_top = "28px"
            offset.margin_right = "34px"
            with Container(style=styles.Classname("top-0 absolute right-0 text-center flex gap-2 items-center") + offset):
                Text(_("It's this green button!"), styles.Description() + styles.Classname("text-xs text-muted-foreground"))
                icon_style = styles.Style()
                icon_style.margin_top = "2px"
                icon_style.width = "1.2rem"
                icon_style.height = "1.2rem"
                icon_style.color = "var(--muted-foreground)"
                Icon("arrow-up", icon_style)

    def complete(self):
        with Container(style=styles.FlexVertical() + styles.Width("400px")):
            Text(_("Onboarding Complete!"), styles.Title())
            Text(_("You have successfully completed the onboarding process. You can now start using ETS2LA. If you need help, feel free to join our Discord server."), styles.Description() + styles.MaxWidth("520px"))
            Space()
            with Button(action=self.handle_show_sidebar):
                Text(_("Finish"))
            
        if self.show_sidebar:
            manager_button_offset = styles.Style()
            manager_button_offset.margin_top = "220px"
            with Container(style=styles.FlexVertical() + styles.Classname("left-2 top-0 absolute items-center justify-center") + manager_button_offset):
                # TRANSLATORS: Please keep the newlines and the spaces in this text, they are important for the layout.
                Text(_("<- Press this edge to open and close the sidebar.\n      Open the Manager to enable plugins."))

    def render(self):
        pages = {
            0: self.welcome,
            1: self.language,
            2: self.sdk_setup,
            3: self.plugins,
            4: self.priority,
            5: self.map_data,
            6: self.size,
            7: self.window_controls,
            8: self.complete
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
        
        with Container(style=styles.FlexVertical() + styles.Classname("items-center relative justify-center gap-4 text-center") + styles.Height("100%")):
            if self.page in pages:
                with Container(style=styles.FlexVertical() + styles.Classname("justify-center gap-4 text-left") + styles.Height("100vh")):
                    with Button(action=self.decrement_page, style=styles.Classname("bg-transparent w-max p-0 h-max"), type="ghost"):
                        Text(f"0{self.page + 1} / 0{len(pages)}", styles.Classname("text-xs text-muted-foreground"))
                    pages[self.page]()
            else:
                with Container(style=styles.FlexVertical() + styles.Width("520px") + styles.Classname("items-center")):
                    Text(_("Page not found"), style=styles.TextColor("red"))
                    with Button(action=self.decrement_page):
                        Text(_("Go back"), styles.Classname("w-max"))