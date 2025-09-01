from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
from Plugins.TTS.utils.proximity import ProximityBeep
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from ETS2LA.UI import (
    ETS2LAPage,
    ETS2LAPageLocation,
    styles,
    TitleAndDescription,
    Tabs,
    Tab,
    Alert,
    Text,
    ComboboxWithTitleDescription,
    ComboboxSearch,
    SliderWithTitleDescription,
    CheckboxWithTitleDescription,
    Container,
)

from ETS2LA.Utils.translator import _, ngettext
from ETS2LA.Utils import settings
import importlib
import logging
import time
import os

providers: list[TTSProvider] = []
files = os.listdir("Plugins/TTS/providers")
files.remove("provider.py")

for file in files:
    if file.endswith(".py"):
        module_name = file[:-3]
        module = importlib.import_module(f"Plugins.TTS.providers.{module_name}")
        provider_class = getattr(module, "Provider", None)
        if provider_class:
            providers.append(provider_class())

# status_key = ControlEvent(
#    alias="tts.status",
#    name="Speak Status",
#    description="Speak the current status, this includes speed, limit, fuel, and distance to destination.",
#    type="button",
#    default="F7",
# )


class Settings(ETS2LAPage):
    url = "/settings/TTS"
    location = ETS2LAPageLocation.SETTINGS
    title = "TTS"
    refresh_rate = 10

    def handle_provider_change(self, value: str):
        settings.Set("TTS", "provider", value)

    def handle_voice_change(self, value: str):
        settings.Set("TTS", "voice", value)

    def handle_speed_change(self, value: float):
        settings.Set("TTS", "speed", value)

    def handle_volume_change(self, value: float):
        settings.Set("TTS", "volume", value)

    def handle_test_mode_change(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("TTS", "test_mode", False)

        settings.Set("TTS", "test_mode", value)

    def handle_prox_beep_change(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("TTS", "road_proximity_beep", False)

        settings.Set("TTS", "road_proximity_beep", value)

    def render(self):
        TitleAndDescription(
            title=_("TTS"),
            description=_(
                "The TTS plugin provides text-to-speech functionality for accessibility and voiced announcements."
            ),
        )

        with Tabs():
            with Tab(
                _("Voices"), container_style=styles.Gap("20px") + styles.FlexVertical()
            ):
                selected = settings.Get("TTS", "provider", "SAPI")
                if self.plugin and self.plugin.selected_provider is not None:
                    provider = self.plugin.selected_provider
                else:
                    provider = next((p for p in providers if p.name == selected), None)

                with Alert(style=styles.Padding("14px")):
                    if self.plugin:
                        Text(provider.custom_text)
                    elif not provider:
                        Text(
                            _("Please select a provider!"),
                            style=styles.TextColor("red"),
                        )
                    else:
                        Text(
                            _(
                                "This will show provider information once the plugin is loaded."
                            )
                        )

                ComboboxWithTitleDescription(
                    title=_("Select TTS provider"),
                    description=_("Select the TTS provider to use."),
                    options=[provider.name for provider in providers],
                    default=provider.name if provider else "SAPI",
                    changed=self.handle_provider_change,
                )

                if provider is None:
                    Text(
                        _("Please select a provider to show voices."),
                        style=styles.TextColor("red"),
                    )
                    return

                voice = settings.Get("TTS", "voice", provider.voices[0].name)
                if voice not in [v.name for v in provider.voices]:
                    voice = provider.voices[0].name
                    settings.Set("TTS", "voice", voice)
                    logging.warning(
                        _("Voice {0} not found, using default: {1}").format(
                            voice, provider.voices[0].name
                        )
                    )

                ComboboxWithTitleDescription(
                    title=_("Select TTS voice"),
                    description=_("Select the TTS voice to use."),
                    options=[voice.name for voice in provider.voices],
                    default=voice,
                    changed=self.handle_voice_change,
                    search=ComboboxSearch(
                        placeholder=_("Search for a voice..."),
                        empty=_("No voices found."),
                    ),
                )

                with Container(style=styles.Gap("20px") + styles.FlexHorizontal()):
                    SliderWithTitleDescription(
                        title=_("Speed"),
                        description=_("Set the target speed of the voice."),
                        default=settings.Get("TTS", "speed", 1.0),
                        min=0.5,
                        max=2.0,
                        step=0.1,
                        changed=self.handle_speed_change,
                    )

                    SliderWithTitleDescription(
                        title=_("Volume"),
                        description=_("Set the target volume of the voice."),
                        default=settings.Get("TTS", "volume", 0.5),
                        min=0.0,
                        max=1.0,
                        step=0.05,
                        changed=self.handle_volume_change,
                    )
                CheckboxWithTitleDescription(
                    title=_("Test Mode"),
                    description=_(
                        "Enable test mode to test the TTS provider without loading the game."
                    ),
                    default=settings.Get("TTS", "test_mode", False),
                    changed=self.handle_test_mode_change,
                )

            with Tab(_("Settings")):
                CheckboxWithTitleDescription(
                    title=_("Enable Road Proximity Beep"),
                    description=_(
                        "Enable a proximity beep that indicates the distance and angle to the closest road."
                    ),
                    default=settings.Get("TTS", "road_proximity_beep", False),
                    changed=self.handle_prox_beep_change,
                )


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("TTS"),
        version="1.0",
        description=_(
            "Text To Speech plugin for accessibility. Some people might also like voiced announcements."
        ),
        modules=["TruckSimAPI"],
        tags=["Base", "Accessibility"],
        listen=["*.py"],
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    # controls = [
    #    status_key
    # ]

    pages = [Settings]
    selected_provider: TTSProvider | None = None
    selected_voice: TTSVoice | None = None

    map_enabled: bool = False
    acc_enabled: bool = False

    closest_city: str = ""

    speed_limit: float = 0

    has_notified_fuel: bool = False
    has_notified_critical_fuel: bool = False

    last_route_distance: float = 0
    notified_distances = [
        2,
        5,
        10,
        20,
        50,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1500,
        2000,
        2500,
        3000,
    ]
    notified_markers = set()

    last_wear_engine: float = 0
    last_wear_cabin: float = 0
    last_wear_chassis: float = 0
    last_wear_transmission: float = 0
    last_wear_wheels: float = 0
    last_wear_cargo: float = 0

    first = True
    last_update = 0

    test_mode = False
    prox_beep = False
    beeper = ProximityBeep()

    def select_provider(self, provider_name: str):
        """
        Select a provider.
        :param provider_name: The name of the provider to select.
        """
        for provider in providers:
            if provider.name == provider_name:
                provider.initialize(self)
                self.selected_provider = provider
                break
        else:
            raise ValueError(f"Provider {provider_name} not found.")

        self.pages[0].reset_timer(
            self.pages[0]
        )  # Reset the settings page to update the provider selection

    def select_voice(self, voice_name: str):
        """
        Select a voice.
        :param voice_name: The name of the voice to select.
        """
        if self.selected_provider:
            for voice in self.selected_provider.voices:
                if voice.name == voice_name:
                    self.selected_voice = voice
                    self.selected_provider.select_voice(voice)
                    break
            else:
                logging.warning(
                    _("Voice {0} not found in provider {1}.").format(
                        voice_name, self.selected_provider.name
                    )
                )
                self.selected_voice = None
        else:
            logging.warning(_("No provider selected. Cannot select voice."))

        self.pages[0].reset_timer(
            self.pages[0]
        )  # Reset the settings page to update the provider selection

    def init(self):
        self.load_settings()

    def load_settings(self):
        self.test_mode = self.settings.test_mode
        if self.test_mode is None:
            self.settings.test_mode = False

        self.prox_beep = self.settings.road_proximity_beep
        if self.prox_beep is None:
            self.settings.road_proximity_beep = False

        provider = self.settings.provider
        voice = self.settings.voice

        if not provider:
            provider = "SAPI"

        if not voice:
            voice = "Microsoft Zira Desktop - English (United States)"

        if not self.selected_provider or self.selected_provider.name != provider:
            logging.warning(_("Loading TTS provider: {0}").format(provider))
            self.select_provider(provider)
            if voice not in [v.name for v in self.selected_provider.voices]:
                voice = self.selected_provider.voices[0].name
                self.settings.voice = voice
                logging.warning(
                    _("Voice {0} not found, using default: {1}").format(
                        voice, self.selected_provider.voices[0].name
                    )
                )

        if not self.selected_voice or self.selected_voice.name != voice:
            logging.warning(_("Loading TTS voice: {0}").format(voice))
            self.select_voice(voice)

        if self.selected_provider:
            volume = self.settings.volume
            if not volume:
                volume = 0.5
                self.settings.volume = 0.5
            self.selected_provider.set_volume(volume)
            self.pages[0].reset_timer(
                self.pages[0]
            )  # Reset the settings page to update the volume

            speed = self.settings.speed
            if not speed:
                speed = 1.0
                self.settings.speed = 1.0
            self.selected_provider.set_speed(speed)
            self.pages[0].reset_timer(
                self.pages[0]
            )  # Reset the settings page to update the speed

    def speak(self, text: str):
        """
        Speak the given text.
        :param text: The text to speak.
        """
        if self.first:
            return

        if self.selected_provider:
            self.selected_provider.speak(text)
        else:
            raise ValueError("No provider selected.")

    def map_enabled_disabled(self):
        """
        Check if map was enabled or disabled last frame.
        """
        try:
            state = self.globals.tags.status["plugins.map"]["Map"]
            if state != self.map_enabled:
                print(f"Map state changed: {state}")
                if state:
                    self.speak(_("Map steering enabled."))
                elif self.state is not None:
                    self.speak(_("Map steering disabled."))

                self.map_enabled = state
        except Exception:
            self.map_enabled = False

    def acc_enabled_disabled(self):
        """
        Check if acc was enabled or disabled last frame.
        """
        try:
            state = self.globals.tags.status["plugins.adaptivecruisecontrol"][
                "AdaptiveCruiseControl"
            ]
            if state != self.acc_enabled:
                if state:
                    self.speak(_("Adaptive Cruise Control enabled."))
                elif self.state is not None:
                    self.speak(_("Adaptive Cruise Control disabled."))

                self.acc_enabled = state
        except Exception:
            self.acc_enabled = False

    def closest_city_changed(self):
        """
        Check if the closest city changed last frame.
        """
        try:
            city = self.globals.tags.closest_city
            distance = self.globals.tags.closest_city_distance
            if city != self.closest_city:
                self.closest_city = city
                text = ngettext(
                    "Closest city is now {city} at a distance of {distance} kilometer.",
                    "Closest city is now {city} at a distance of {distance} kilometers.",
                    round(distance),
                ).format(city=city, distance=round(distance))
                self.speak(text)
        except Exception:
            self.closest_city = None

    def speedlimit_changed(self, api):
        """
        Check if the speed limit changed last frame.
        """
        try:
            speed_limit = api["truckFloat"]["speedlimit"]
            if speed_limit != self.speed_limit:
                self.speed_limit = speed_limit
                self.speak(
                    ngettext(
                        "Speed limit changed to {0} kilometer per hour.",
                        "Speed limit changed to {0} kilometers per hour.",
                        round(speed_limit),
                    ).format(round(speed_limit))
                )
        except Exception:
            self.speed_limit = 0

    def fuel_check(self, api):
        try:
            fuel = round(api["truckFloat"]["fuelRange"])
            if fuel < 200 and not self.has_notified_fuel:
                self.speak(
                    ngettext(
                        "Fuel range is now only {0} kilometer, please refuel soon.",
                        "Fuel range is now only {0} kilometers, please refuel soon.",
                        fuel,
                    ).format(fuel)
                )
                self.has_notified_fuel = True
            elif fuel < 50 and not self.has_notified_critical_fuel:
                self.speak(
                    ngettext(
                        "Fuel range is now critical at only {0} kilometer, please refuel as soon as possible.",
                        "Fuel range is now critical at only {0} kilometers, please refuel as soon as possible.",
                        fuel,
                    ).format(fuel)
                )
                self.has_notified_critical_fuel = True
            elif fuel >= 200:
                self.has_notified_fuel = False
                self.has_notified_critical_fuel = False
            elif fuel >= 50:
                self.has_notified_critical_fuel = False
        except Exception:
            self.has_notified_fuel = False
            self.has_notified_critical_fuel = False

    def route_distance(self, api):
        try:
            route_distance = (
                api["truckFloat"]["routeDistance"] / 1000
            )  # Meters to Kilometers

            for distance in self.notified_distances:
                if route_distance <= distance and distance not in self.notified_markers:
                    if (
                        self.last_route_distance > 0
                        and route_distance < self.last_route_distance
                    ):
                        self.speak(
                            _("It's {0} kilometers to the next waypoint.").format(
                                round(distance)
                            )
                        )
                        self.notified_markers.add(distance)

            if route_distance > self.last_route_distance + 50:
                self.notified_markers.clear()

            self.last_route_distance = route_distance
        except Exception:
            self.last_route_distance = 0
            self.notified_markers.clear()

    def damage_check(self, api):
        try:
            wear_engine = round(api["truckFloat"]["wearEngine"] * 100)
            wear_cabin = round(api["truckFloat"]["wearCabin"] * 100)
            wear_chassis = round(api["truckFloat"]["wearChassis"] * 100)
            wear_transmission = round(api["truckFloat"]["wearTransmission"] * 100)
            wear_wheels = round(api["truckFloat"]["wearWheels"] * 100)
            wear_cargo = round(api["jobFloat"]["cargoDamage"] * 100)

            if wear_engine > self.last_wear_engine:
                self.speak(_("Engine damage is now at {0}%.").format(wear_engine))
                self.last_wear_engine = wear_engine
            if wear_cabin > self.last_wear_cabin:
                self.speak(_("Cabin damage is now at {0}%.").format(wear_cabin))
                self.last_wear_cabin = wear_cabin
            if wear_chassis > self.last_wear_chassis:
                self.speak(_("Chassis damage is now at {0}%.").format(wear_chassis))
                self.last_wear_chassis = wear_chassis
            if wear_transmission > self.last_wear_transmission:
                self.speak(
                    _("Transmission damage is now at {0}%.").format(wear_transmission)
                )
                self.last_wear_transmission = wear_transmission
            if wear_wheels > self.last_wear_wheels:
                self.speak(_("Wheel damage is now at {0}%.").format(wear_wheels))
                self.last_wear_wheels = wear_wheels
            if wear_cargo > self.last_wear_cargo:
                self.speak(_("Cargo damage is now at {0}%.").format(wear_cargo))
                self.last_wear_cargo = wear_cargo
        except Exception:
            self.last_wear_cargo = 0
            self.last_wear_engine = 0
            self.last_wear_chassis = 0
            self.last_wear_transmission = 0
            self.last_wear_wheels = 0
            self.last_wear_cabin = 0

    def status(self, api):
        try:
            speed = round(api["truckFloat"]["speed"])
            speed_limit = round(api["truckFloat"]["speedLimit"])
            fuel = round(api["truckFloat"]["fuel"])
            distance = round(api["truckFloat"]["routeDistance"] / 1000)

            self.speak(
                _(
                    "Speed {0} kilometers per hour, limit {1}, fuel {2}%, and it's {3} kilometers to the next waypoint."
                ).format(speed, speed_limit, fuel, distance)
            )
        except Exception as e:
            self.speak(f"Error while processing status {e}")

    def update_beeper(self, api):
        if self.prox_beep:
            distance = self.globals.tags.closest_road_distance
            angle = self.globals.tags.closest_road_angle
            if distance is None or angle is None:
                if self.beeper.running:
                    self.beeper.stop()
                return

            if "plugins.map" not in distance or "plugins.map" not in angle:
                return

            distance = distance["plugins.map"]
            angle = angle["plugins.map"]
            if distance == 0:
                if self.beeper.running:
                    self.beeper.stop()
                return

            if not self.beeper.running:
                self.beeper.start()

            self.beeper.set_angle(angle, 0)
            self.beeper.set_distance(distance)
        else:
            if self.beeper.running:
                self.beeper.stop()

    def run(self):
        api = self.modules.TruckSimAPI.run()

        self.update_beeper(api)
        if self.last_update + 1 > time.time():
            return

        self.load_settings()

        if self.test_mode:
            self.last_update = time.time()
            self.speak(_("Test mode enabled. This is a test message."))
            return

        self.map_enabled_disabled()
        self.acc_enabled_disabled()
        self.closest_city_changed()
        self.speedlimit_changed(api)
        self.fuel_check(api)
        self.route_distance(api)
        self.damage_check(api)

        self.first = False
        self.last_update = time.time()
