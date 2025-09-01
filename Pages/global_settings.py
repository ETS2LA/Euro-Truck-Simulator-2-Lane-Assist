from ETS2LA.Utils import settings as utils_settings
from ETS2LA import variables
from ETS2LA.UI import (
    ETS2LAPage,
    styles,
    Container,
    Text,
    Tabs,
    Tab,
    SliderWithTitleDescription,
    ComboboxWithTitleDescription,
    ComboboxSearch,
    CheckboxWithTitleDescription,
    Separator,
    Button,
    Icon,
    Alert,
    AdSense,
    Side,
    InputWithTitleDescription,
    InputType,
    Space,
    TitleAndDescription,
    Link,
)

import ETS2LA.Handlers.sounds as sounds
from ETS2LA.Utils.translator import languages, parse_language, correct_naming
from ETS2LA.Utils.translator import _
from langcodes import Language
import webbrowser

import screeninfo

ad_preferences = {
    _("None"): 0,
    _("Minimal (recommended)"): 1,
    _("Medium"): 2,
    _("Full"): 3,
}


class Page(ETS2LAPage):
    url = "/settings/global"
    monitors = screeninfo.get_monitors()
    initial_high_priority = False
    refresh_rate = 2

    def __init__(self):
        super().__init__()
        self.initial_high_priority = utils_settings.Get(
            "global", "high_priority", default=True
        )

    def handle_width_change(self, width: int):
        utils_settings.Set("global", "width", width)

    def handle_height_change(self, height: int):
        utils_settings.Set("global", "height", height)

    def handle_alpha_change(self, alpha: float):
        utils_settings.Set("global", "transparency_alpha", alpha)

    def change_language(self, language: str):
        utils_settings.Set("global", "language", language)

    def change_soundpack(self, soundpack: str):
        utils_settings.Set("global", "soundpack", soundpack)

    def change_volume(self, volume: int):
        utils_settings.Set("global", "volume", volume)

    def change_startup_sound(self, *args):
        if args:
            startup_sound = args[0]
        else:
            startup_sound = not utils_settings.Get(
                "global", "startup_sound", default=True
            )

        utils_settings.Set("global", "startup_sound", startup_sound)

    def change_monitor(self, monitor: str):
        if not monitor:
            return

        monitor_index = int(monitor.split(" ")[1])
        utils_settings.Set("global", "monitor", monitor_index)

    def change_port(self, port: int):
        if not port:
            return

        utils_settings.Set("global", "frontend_port", port)

    def handle_frameless_change(self, *args):
        if args:
            frameless = args[0]
        else:
            frameless = not utils_settings.Get("global", "frameless", default=False)

        utils_settings.Set("global", "frameless", frameless)

    def handle_crash_report_change(self, *args):
        if args:
            crash_report = args[0]
        else:
            crash_report = not utils_settings.Get(
                "global", "send_crash_reports", default=True
            )

        utils_settings.Set("global", "send_crash_reports", crash_report)

    def handle_fancy_traceback_change(self, *args):
        if args:
            fancy_traceback = args[0]
        else:
            fancy_traceback = not utils_settings.Get(
                "global", "use_fancy_traceback", default=True
            )

        utils_settings.Set("global", "use_fancy_traceback", fancy_traceback)

    def handle_debug_mode_change(self, *args):
        if args:
            debug_mode = args[0]
        else:
            debug_mode = not utils_settings.Get("global", "debug_mode", default=True)

        utils_settings.Set("global", "debug_mode", debug_mode)

    def handle_frontend_mirror_change(self, mirror: str):
        utils_settings.Set("global", "frontend_mirror", mirror)

    def handle_window_timeout_change(self, window_timeout: int):
        utils_settings.Set("global", "window_timeout", window_timeout)

    def handle_fireworks_change(self, *args):
        if args:
            fireworks = args[0]
        else:
            fireworks = not utils_settings.Get("global", "fireworks", default=True)

        utils_settings.Set("global", "fireworks", fireworks)

    def handle_snow_change(self, *args):
        if args:
            snow = args[0]
        else:
            snow = not utils_settings.Get("global", "snow", default=True)

        utils_settings.Set("global", "snow", snow)

    def handle_acceleration_fallback_change(self, *args):
        if args:
            acceleration_fallback = args[0]
        else:
            acceleration_fallback = not utils_settings.Get(
                "global", "acceleration_fallback", default=True
            )

        utils_settings.Set("global", "acceleration_fallback", acceleration_fallback)

    def handle_high_priority_change(self, *args):
        if args:
            high_priority = args[0]
        else:
            high_priority = not utils_settings.Get(
                "global", "high_priority", default=True
            )

        utils_settings.Set("global", "high_priority", high_priority)

    def handle_slow_loading_change(self, *args):
        if args:
            slow_loading = args[0]
        else:
            slow_loading = not utils_settings.Get(
                "global", "slow_loading", default=False
            )

        utils_settings.Set("global", "slow_loading", slow_loading)

    def match_value_to_preference_name(self, value: int) -> str:
        for name, val in ad_preferences.items():
            if val == value:
                return name
        return _("Minimal (recommended)")

    def handle_ad_preference(self, *args):
        if args:
            ad_preference = args[0]
        else:
            ad_preference = utils_settings.Get("global", "ad_preference", default=1)
            utils_settings.Set("global", "ad_preference", ad_preference)
            return

        utils_settings.Set(
            "global", "ad_preference", ad_preferences.get(ad_preference, 1)
        )

    def open_kofi(self):
        webbrowser.open("https://ko-fi.com/tumppi066")

    def render(self):
        TitleAndDescription(
            _("Global Settings"),
            _(
                "Here you can find settings that affect the entire application. Things such as the window size and language."
            ),
        )

        ads = utils_settings.Get("global", "ad_preference", default=1)  # type: ignore

        with Tabs():
            with Tab(_("User Interface"), styles.FlexVertical() + styles.Gap("24px")):
                if ads >= 2:
                    with Container(
                        style=styles.FlexHorizontal()
                        + styles.Classname("justify-center")
                    ):
                        AdSense(
                            client="ca-pub-6002744323117854",
                            slot="3283698879",
                            style=styles.Style(
                                display="inline-block", width="700px", height="90px"
                            ),
                        )

                with Container(
                    styles.FlexHorizontal()
                    + styles.Gap("24px")
                    + styles.Classname("justify-between")
                ):
                    SliderWithTitleDescription(
                        title=_("Window Width"),
                        description=_(
                            "Change the width of the window. Please note that ETS2LA is not tested on non-standard resolutions, so use at your own risk!"
                        ),
                        min=500,
                        max=2560,
                        step=10,
                        default=utils_settings.Get("global", "width", default=720),  # type: ignore
                        suffix="px",
                        changed=self.handle_width_change,
                    )

                    SliderWithTitleDescription(
                        title=_("Window Height"),
                        description=_(
                            "Change the height of the window. Please note that ETS2LA is not tested on non-standard resolutions, so use at your own risk!"
                        ),
                        min=250,
                        max=1440,
                        step=10,
                        default=utils_settings.Get("global", "height", default=720),  # type: ignore
                        suffix="px",
                        changed=self.handle_height_change,
                    )

                SliderWithTitleDescription(
                    title=_("Transparency mode Alpha"),
                    description=_(
                        "Change the transparency of the window when entering transparency mode. This can be done by right-clicking the green button in the top right corner."
                    ),
                    min=0.4,
                    max=1,
                    step=0.05,
                    default=utils_settings.Get(
                        "global", "transparency_alpha", default=0.8
                    ),  # type: ignore
                    suffix="",
                    changed=self.handle_alpha_change,
                )

                current = utils_settings.Get("global", "language", default="English")
                if not current:
                    current = "English"

                current = Language.find(correct_naming(current))
                ComboboxWithTitleDescription(
                    title=_("Language"),
                    description=_("Select the language for the application."),
                    default=current.display_name().capitalize(),
                    options=[
                        language.display_name().capitalize() for language in languages
                    ],
                    changed=self.change_language,
                    side=Side.TOP,
                    search=ComboboxSearch(
                        _("Search Languages..."), _("Help us translate on discord!")
                    ),
                )

                if current != "English":
                    with Alert(style=styles.Padding("14px")):
                        with Container(
                            styles.FlexHorizontal()
                            + styles.Gap("12px")
                            + styles.Classname("items-start")
                        ):
                            style = styles.Style()
                            style.margin_top = "2px"
                            style.width = "1rem"
                            style.height = "1rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            with Container(styles.FlexVertical() + styles.Gap("4px")):
                                Text(
                                    _(
                                        "This translation is {percentage:.2f}% complete."
                                    ).format(percentage=_.get_percentage()),
                                    styles.Classname("text-muted-foreground"),
                                )
                                with Container(
                                    styles.FlexHorizontal() + styles.Gap("8px")
                                ):
                                    Link(
                                        _("List Contributors"),
                                        f"https://weblate.ets2la.com/user/?q=translates:{parse_language(current)}%20contributes:ets2la/backend",
                                        styles.Classname(
                                            "text-sm text-muted-foreground hover:underline"
                                        ),
                                    )
                                    Text("-")
                                    Link(
                                        _("Help Translate"),
                                        f"https://weblate.ets2la.com/projects/ets2la/backend/{parse_language(current)}",
                                        styles.Classname(
                                            "text-sm text-muted-foreground hover:underline"
                                        ),
                                    )

            with Tab(
                _("Audio"), container_style=styles.FlexVertical() + styles.Gap("24px")
            ):
                with Container(
                    styles.FlexHorizontal()
                    + styles.Gap("24px")
                    + styles.Classname("justify-between")
                ):
                    ComboboxWithTitleDescription(
                        title=_("Soundpack"),
                        description=_(
                            "Select the soundpack to use, these can be added to app/ETS2LA/Assets/Sounds."
                        ),
                        default=sounds.SELECTED_SOUNDPACK,
                        options=sounds.SOUNDPACKS,
                        changed=self.change_soundpack,
                    )

                    SliderWithTitleDescription(
                        title=_("Volume"),
                        description=_(
                            "Adjust the volume. This will affect all sounds played by ETS2LA."
                        ),
                        min=0,
                        max=100,
                        step=5,
                        default=int(sounds.VOLUME * 100),
                        suffix="%",
                        changed=self.change_volume,
                    )

                state = utils_settings.Get("global", "startup_sound", default=True)
                CheckboxWithTitleDescription(
                    title=_("Startup Sound"),
                    description=_(
                        "Toggle the startup sound on or off. This plays every time the ETS2LA window is opened."
                    ),
                    default=state,  # type: ignore
                    changed=self.change_startup_sound,
                )

            with Tab(
                _("Variables"),
                container_style=styles.FlexVertical() + styles.Gap("24px"),
            ):
                Text("Ad Preferences", styles.Classname("text-lg font-semibold"))
                default = self.match_value_to_preference_name(
                    utils_settings.Get("global", "ad_preference", default=1)  # type: ignore
                )
                ComboboxWithTitleDescription(
                    options=[
                        _("None"),
                        _("Minimal (recommended)"),
                        _("Medium"),
                        _("Full"),
                    ],
                    default=default,  # type: ignore
                    changed=self.handle_ad_preference,
                    title="How many ads do you want to see?",
                    description="This will control how many ads you see in ETS2LA. Minimal is recommended to support development without affecting usage.",
                )

                if ads == 0:
                    with Button(
                        style=styles.FlexHorizontal()
                        + styles.Gap("12px")
                        + styles.Classname("items-center bg-kofi hover:bg-kofi-active!")
                        + styles.Height("70px"),
                        action=self.open_kofi,
                    ):
                        style = styles.Style()
                        style.margin_top = "2px"
                        style.width = "1.5rem"
                        style.height = "1.5rem"
                        style.color = ""
                        Icon("heart", style)
                        Text(
                            _("Support ETS2LA Development on Ko-Fi"),
                            styles.Classname("font-semibold"),
                        )

                else:
                    with Alert(style=styles.Padding("14px")):
                        with Container(
                            styles.FlexHorizontal()
                            + styles.Gap("12px")
                            + styles.Classname("items-start")
                        ):
                            style = styles.Style()
                            style.margin_top = "2px"
                            style.width = "1.5rem"
                            style.height = "1.5rem"
                            style.color = "var(--muted-foreground)"
                            Icon("info", style)
                            with Container(styles.FlexVertical() + styles.Gap("4px")):
                                if ads == 1:
                                    Text(
                                        _(
                                            "You will see exactly one ad in the about page. There will be no other ads. This option is recommended to support further development of ETS2LA."
                                        ),
                                        styles.Classname("text-muted-foreground"),
                                    )
                                elif ads == 2:
                                    Text(
                                        _(
                                            "You will see non intrusive ads in non essential pages. Visualization pages will be ad free. This option is recommended if you want to support development further."
                                        ),
                                        styles.Classname("text-muted-foreground"),
                                    )
                                elif ads == 3:
                                    Text(
                                        _(
                                            "You will see as many ads as I thought would not completely destroy the usage. Visualization pages are still ad free when enabled."
                                        ),
                                        styles.Classname("text-muted-foreground"),
                                    )

                if ads >= 2:
                    with Container(
                        style=styles.FlexHorizontal()
                        + styles.Classname("justify-center")
                    ):
                        AdSense(
                            client="ca-pub-6002744323117854",
                            slot="3283698879",
                            style=styles.Style(
                                display="inline-block", width="700px", height="90px"
                            ),
                        )

                Text("Backend Settings", styles.Classname("text-lg font-semibold"))
                CheckboxWithTitleDescription(
                    title=_("Fallback to old acceleration method"),
                    description=_(
                        "If you are experiencing issues with the truck not accelerating / braking properly, then you can enable this option to use another method. Please keep in mind that if the new one has gotten stuck, you might need to restart the game after toggling this."
                    ),
                    default=utils_settings.Get(
                        "global", "acceleration_fallback", default=True
                    ),  # type: ignore
                    changed=self.handle_acceleration_fallback_change,
                )

                high_priority = utils_settings.Get(
                    "global", "high_priority", default=True
                )  # type: ignore
                CheckboxWithTitleDescription(
                    title=_("High Priority"),
                    description=_(
                        "Run ETS2LA in high priority mode. This will tell your OS to give more CPU time to ETS2LA, which can improve performance at the cost of other applications."
                    ),
                    default=high_priority,  # type: ignore
                    changed=self.handle_high_priority_change,
                )

                if high_priority != self.initial_high_priority:
                    with Alert(style=styles.Padding("14px")):
                        with Container(
                            styles.FlexHorizontal()
                            + styles.Gap("12px")
                            + styles.Classname("items-start")
                        ):
                            style = styles.Style()
                            style.margin_top = "2px"
                            style.width = "1rem"
                            style.height = "1rem"
                            style.color = "var(--muted-foreground)"
                            Icon("warning", style)
                            Text(
                                _(
                                    "You need to restart ETS2LA to apply the priority change!"
                                ),
                                styles.Classname("text-muted-foreground"),
                            )

                CheckboxWithTitleDescription(
                    title=_("Slow Loading"),
                    description=_(
                        "If your PC has troubles loading all plugins in parallel, you can enable this option to load them one by one. Please note that enabling this option will mean you have to wait a while for the plugins to become available."
                    ),
                    default=utils_settings.Get("global", "slow_loading", default=False),  # type: ignore
                    changed=self.handle_slow_loading_change,
                )

            with Tab(_("Miscellaneous"), styles.FlexVertical() + styles.Gap("24px")):
                if variables.LOCAL_MODE:
                    port = utils_settings.Get("global", "frontend_port", default=3005)  # type: ignore
                    InputWithTitleDescription(
                        title=_("Frontend Port"),
                        description=_(
                            "Change the port used by the frontend. This is only used in local mode."
                        ),
                        default=port,
                        type=InputType.NUMBER,
                        changed=self.change_port,
                    )

                CheckboxWithTitleDescription(
                    title=_("Frameless Window"),
                    description=_(
                        "Disable this option if you have any issues moving the window around."
                    ),
                    default=utils_settings.Get("global", "frameless", default=False),  # type: ignore
                    changed=self.handle_frameless_change,
                )
                CheckboxWithTitleDescription(
                    title=_("Send Crash Reports"),
                    description=_(
                        "Automatically send crash reports to help improve the application."
                    ),
                    default=utils_settings.Get(
                        "global", "send_crash_reports", default=True
                    ),  # type: ignore
                    changed=self.handle_crash_report_change,
                )
                CheckboxWithTitleDescription(
                    title=_("Use Fancy Traceback"),
                    description=_(
                        "Enable this option to use a fancy traceback for errors."
                    ),
                    default=utils_settings.Get(
                        "global", "use_fancy_traceback", default=True
                    ),  # type: ignore
                    changed=self.handle_fancy_traceback_change,
                )

                CheckboxWithTitleDescription(
                    title=_("Debug Mode"),
                    description=_(
                        "Enable this option to use the edge debugger for the frontend."
                    ),
                    default=utils_settings.Get("global", "debug_mode", default=False),  # type: ignore
                    changed=self.handle_debug_mode_change,
                )

                ComboboxWithTitleDescription(
                    title=_("Default UI Mirror"),
                    description=_(
                        "The default ETS2LA UI mirror to use. Auto will choose the best available mirror."
                    ),
                    options=["Auto", *variables.FRONTEND_MIRRORS],
                    default=utils_settings.Get(
                        "global", "frontend_mirror", default="Auto"
                    ),  # type: ignore
                    changed=self.handle_frontend_mirror_change,
                )

                SliderWithTitleDescription(
                    title=_("ETS2LA Window Timeout"),
                    description=_(
                        "The amount of time ETS2LA waits for the window to show up."
                    ),
                    default=utils_settings.Get("global", "window_timeout", default=10),  # type: ignore
                    min=1,
                    max=30,
                    step=1,
                    changed=self.handle_window_timeout_change,
                )

                Separator()
                with Container(
                    styles.FlexHorizontal()
                    + styles.Gap("24px")
                    + styles.Classname("justify-between")
                ):
                    CheckboxWithTitleDescription(
                        title=_("Fireworks"),
                        description=_(
                            "Enable this option to use fireworks effects during the new year's."
                        ),
                        default=utils_settings.Get("global", "fireworks", default=True),  # type: ignore
                        changed=self.handle_fireworks_change,
                    )

                    CheckboxWithTitleDescription(
                        title=_("Snow"),
                        description=_(
                            "Enable this option to use snow effects during the winter season."
                        ),
                        default=utils_settings.Get("global", "snow", default=True),  # type: ignore
                        changed=self.handle_snow_change,
                    )

                Space(styles.Height("24px"))
