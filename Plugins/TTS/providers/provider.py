class TTSVoice:
    name: str
    """
    The name of this voice.
    """
    language: str | None
    """
    The language of this voice.
    If None assume all.
    """
    id: str | None
    """
    The id of this voice, if the engine
    needs it.
    """

    def __init__(
        self, name: str = "", language: str | None = None, id: str | None = None
    ):
        self.name = name
        self.language = language
        self.id = id


class TTSProvider:
    name: str
    """
    The name of the TTSProvider.
    """
    voices: list[TTSVoice]
    """
    A list of voices to show on the UI.
    """
    languages: list[str] | None
    """
    The languages this TTSProvider can use.
    If None, assume all languages.
    """
    supports_speed: bool = True
    """
    Whether this TTSProvider supports speed.
    """
    supports_volume: bool = True
    """
    Whether this TTSProvider supports volume.
    """
    custom_text: str = ""
    """
    Custom text to show in the UI after the speed slider.
    """

    _selected_voice: TTSVoice | None
    _selected_language: str | None

    def initialize(self, plugin):
        """Initialize the TTSProvider.
        This is called when the provider is selected.
        """
        pass

    def select_voice(self, voice: TTSVoice):
        """Select a voice.
        :param voice: The voice to select.
        """
        self._selected_voice = voice

    def select_language(self, language: str):
        """Select a language.
        :param language: The language to select.
        """
        self._selected_language = language

    def get_voices(self) -> list[TTSVoice]:
        """Get the list of voices.
        :return: The list of voices.
        """
        if self._selected_language:
            return [
                voice
                for voice in self.voices
                if not voice.language or voice.language == self._selected_language
            ]

    def speak(self, text: str):
        """Speak the given text.
        :param text: The text to speak.
        """
        pass

    def set_volume(self, volume: float):
        """Set the volume.
        :param volume: The volume to set.
        """
        pass

    def set_speed(self, speed: float):
        """Set the speed.
        :param speed: The speed to set.
        """
        pass
