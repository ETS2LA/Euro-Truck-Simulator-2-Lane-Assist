from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *

import importlib
import time
import os

providers = []
files = os.listdir("Plugins/TTS/providers")
files.remove("provider.py")

for file in files:
    if file.endswith(".py"):
        module_name = file[:-3]
        module = importlib.import_module(f"Plugins.TTS.providers.{module_name}")
        provider_class = getattr(module, "Provider", None)
        if provider_class:
            providers.append(provider_class())

class Settings(ETS2LASettingsMenu):
    plugin_name = "TTS"
    dynamic=True
    
    def render(self):
        if not self.plugin:
            Label("Please enable the plugin before viewing this page.")
            return RenderUI()
        
        
        
        return RenderUI()

class Plugin(ETS2LAPlugin):
    fps_cap = 2
    
    description = PluginDescription(
        name="TTS",
        version="1.0",
        description="Text To Speech plugin for accessibility. Some people might also like voiced announcements.",
        modules=[],
        listen=["*.py"],
        hidden=True
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    settings_menu = Settings()
    selected_provider: TTSProvider | None = None
    
    def select_provider(self, provider_name: str):
        """
        Select a provider.
        :param provider_name: The name of the provider to select.
        """
        for provider in providers:
            if provider.name == provider_name:
                provider.initialize()
                self.selected_provider = provider
                break
        else:
            raise ValueError(f"Provider {provider_name} not found.")

    def init(self):
        self.select_provider("SAPI")
        # Select first voice by default
        self.selected_provider.select_voice(self.selected_provider.voices[0])
        
    def speak(self, text: str):
        """
        Speak the given text.
        :param text: The text to speak.
        """
        if self.selected_provider:
            self.selected_provider.speak(text)
        else:
            raise ValueError("No provider selected.")

    def run(self):
        self.speak("Hello, this is a test of the TTS plugin.")
        time.sleep(5)
