from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
from Plugins.TTS.utils.proximity import ProximityBeep
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *

from ETS2LA.Utils.translator import Translate
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

#status_key = ControlEvent(
#    alias="tts.status",
#    name="Speak Status",
#    description="Speak the current status, this includes speed, limit, fuel, and distance to destination.",
#    type="button",
#    default="F7",
#)

class Settings(ETS2LASettingsMenu):
    plugin_name = "TTS"
    dynamic=True
    
    def render(self):
        with Group("vertical", gap=14, padding=0):
            Title("TTS")
            Description("This plugin provides no description.")
        
        with TabView():
            with Tab("Voices"):
                selected = settings.Get("TTS", "provider", "SAPI")
                if self.plugin and self.plugin.selected_provider != None:
                    provider = self.plugin.selected_provider
                else:
                    provider = next((p for p in providers if p.name == selected), None)
                
                if self.plugin:
                    Label(provider.custom_text)
                else:
                    Label("This will show provider information once the plugin is loaded.")
                    
                Selector(
                    "Select TTS provider",
                    "provider",
                    "SAPI",
                    [provider.name for provider in providers],
                    "Select the TTS provider to use.",
                )
                
                if provider is None:
                    Label("Please select a provider to show voices.")
                    return RenderUI()
                
                voice = settings.Get("TTS", "voice", provider.voices[0].name)
                
                Selector(
                    "Select TTS voice",
                    "voice",
                    voice,
                    [voice.name for voice in provider.voices],
                    "Select the TTS voice to use.",
                )
                
                if provider.supports_speed:
                    Slider(
                        "Speed",
                        "speed",
                        1.0,
                        0.5,
                        2.0,
                        0.1,
                        "Set the target speed of the voice.",
                    )
                else:
                    Label("This provider does not support speed control.")
                    
                if provider.supports_volume:
                    Slider(
                        "Volume",
                        "volume",
                        0.5,
                        0.0,
                        1.0,
                        0.05,
                        "Set the target volume of the voice.",
                    )
                else:
                    Label("This provider does not support volume control.") 
                    
                Switch(
                    "Test Mode",
                    "test_mode",
                    False,
                    "Enable test mode to test the TTS provider without loading the game.",
                )
                
            with Tab("Settings"):
                Switch(
                    "Road Proximity Beep",
                    "road_proximity_beep",
                    False,
                    "Will provide a beep based on the angle and distance to the closest road. Angle is indicated by the frequency of the beeps, and distance is indicated by the volume. Once on a road the beeps will be disabled."
                )
        
        return RenderUI()

class Plugin(ETS2LAPlugin): 
    description = PluginDescription(
        name="TTS",
        version="1.0",
        description="Text To Speech plugin for accessibility. Some people might also like voiced announcements.",
        modules=["TruckSimAPI"],
        tags=["Base", "Accessibility"],
        listen=["*.py"]
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    #controls = [
    #    status_key
    #]

    settings_menu = Settings()
    selected_provider: TTSProvider | None = None
    selected_voice: TTSVoice | None = None
    
    map_enabled: bool = False
    acc_enabled: bool = False
    
    closest_city: str = ""
    
    speed_limit: float = 0
    
    has_notified_fuel: bool = False
    has_notified_critical_fuel: bool = False
    
    last_route_distance: float = 0
    notified_distances = [2, 5, 10, 20, 50, 100, 200, 300, 400, 500, 600, 
                          700, 800, 900, 1000, 1500, 2000, 2500, 3000]
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
                logging.warning(f"Voice {voice_name} not found in provider {self.selected_provider.name}.")
                self.selected_voice = None
        else:
            logging.warning("No provider selected. Cannot select voice.")

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
            logging.warning(f"Loading TTS provider: {provider}")
            self.select_provider(provider)
            if voice not in [v.name for v in self.selected_provider.voices]:
                voice = self.selected_provider.voices[0].name
                self.settings.voice = voice
                logging.warning(f"Voice {voice} not found, using default: {self.selected_provider.voices[0].name}")
            
        if not self.selected_voice or self.selected_voice.name != voice:
            logging.warning(f"Loading TTS voice: {voice}")
            self.select_voice(voice)
            
        if self.selected_provider:
            volume = self.settings.volume
            if not volume: volume = 0.5; self.settings.volume = 0.5
            self.selected_provider.set_volume(volume)
            
            speed = self.settings.speed
            if not speed: speed = 1.0; self.settings.speed = 1.0
            self.selected_provider.set_speed(speed)
        
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
            state = self.globals.tags.status["Map"]["Map"]
            if state != self.map_enabled:
                if state:
                    self.speak(Translate("tts.map.enabled"))
                elif self.state is not None:
                    self.speak(Translate("tts.map.disabled"))
                
                self.map_enabled = state
        except:
            self.map_enabled = False

    def acc_enabled_disabled(self):
        """
        Check if acc was enabled or disabled last frame.
        """
        try:
            state = self.globals.tags.status["AdaptiveCruiseControl"]["AdaptiveCruiseControl"]
            if state != self.acc_enabled:
                if state:
                    self.speak(Translate("tts.acc.enabled"))
                elif self.state is not None:
                    self.speak(Translate("tts.acc.disabled"))
                
                self.acc_enabled = state
        except:
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
                self.speak(Translate("tts.closest.city", [city, round(distance / 1000, 1)]))
        except:
            self.closest_city = None
            
    def speedlimit_changed(self, api):
        """
        Check if the speed limit changed last frame.
        """
        try:
            speed_limit = api["truckFloat"]["speedlimit"]
            if speed_limit != self.speed_limit:
                self.speed_limit = speed_limit
                self.speak(Translate("tts.speed.limit", [round(speed_limit)]))
        except:
            self.speed_limit = 0
            
    def fuel_check(self, api):
        try:
            fuel = round(api["truckFloat"]["fuelRange"])
            if fuel < 200 and not self.has_notified_fuel:
                self.speak(Translate("tts.fuel.low_range", [fuel]))
                self.has_notified_fuel = True
            elif fuel < 50 and not self.has_notified_critical_fuel:
                self.speak(Translate("tts.fuel.critical_range", [fuel]))
                self.has_notified_critical_fuel = True
            elif fuel >= 200:
                self.has_notified_fuel = False
                self.has_notified_critical_fuel = False
            elif fuel >= 50:
                self.has_notified_critical_fuel = False
        except:
            self.has_notified_fuel = False
            self.has_notified_critical_fuel = False

    def route_distance(self, api):
        try:
            route_distance = api["truckFloat"]["routeDistance"] / 1000 # Meters to Kilometers

            for distance in self.notified_distances:
                print(f"\rroute_distance: {route_distance}, original: {api['truckFloat']['routeDistance']}", end='')
                if route_distance <= distance and distance not in self.notified_markers:
                    if self.last_route_distance > 0 and route_distance < self.last_route_distance:
                        self.speak(Translate("tts.route.distance", [distance]))
                        self.notified_markers.add(distance)
            
            if route_distance > self.last_route_distance + 50:
                self.notified_markers.clear()
            
            self.last_route_distance = route_distance
        except:
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
                self.speak(Translate("tts.damage.engine", [wear_engine]))
                self.last_wear_engine = wear_engine
            if wear_cabin > self.last_wear_cabin:
                self.speak(Translate("tts.damage.cabin", [wear_cabin]))
                self.last_wear_cabin = wear_cabin
            if wear_chassis > self.last_wear_chassis:
                self.speak(Translate("tts.damage.chassis", [wear_chassis]))
                self.last_wear_chassis = wear_chassis
            if wear_transmission > self.last_wear_transmission:
                self.speak(Translate("tts.damage.transmission", [wear_transmission]))
                self.last_wear_transmission = wear_transmission
            if wear_wheels > self.last_wear_wheels:
                self.speak(Translate("tts.damage.wheels", [wear_wheels]))
                self.last_wear_wheels = wear_wheels
            if wear_cargo > self.last_wear_cargo:
                self.speak(Translate("tts.damage.cargo", [wear_cargo]))
                self.last_wear_cargo = wear_cargo
        except:
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

            self.speak(Translate("tts.status", [speed, speed_limit, fuel, distance]))
        except Exception as e:
            self.speak(f"Error while processing status {e}")

    def update_beeper(self, api):
        if self.prox_beep:
            distance = self.globals.tags.closest_road_distance
            angle = self.globals.tags.closest_road_angle
            if distance is None or angle is None:
                if self.beeper.running: self.beeper.stop()
                return
            
            distance = distance["Map"]
            angle = angle["Map"]
            if distance == 0:
                if self.beeper.running: self.beeper.stop()
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
            self.speak("Test mode enabled. This is a test message.")
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