from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
try:
    import pyttsx3
    engine = pyttsx3.init()
except Exception as e:
    raise ImportError("pyttsx3 failed to load, please make sure you have eSpeak installed on Linux or SAPI5 on Windows.") from e
    
engine_voices = engine.getProperty("voices")

voices = []
for ev in engine_voices:
    voice = TTSVoice()
    voice.name = ev.name
    voice.id = ev.id
    voice.language = ev.languages[0] if ev.languages else None
    voices.append(voice)


class Provider(TTSProvider):
    name = "SAPI"
    voices = voices
    languages = None
    custom_text = "SAPI is Microsoft's own TTS engine, you can download more voices from the internet"

    def initialize(self, plugin): ...

    def select_voice(self, voice):
        super().select_voice(voice)
        engine.setProperty("voice", voice.id)

    def set_speed(self, speed):
        engine.setProperty("rate", round(200 * speed))  # 200wpm is the default speed.

    def set_volume(self, volume):
        engine.setProperty("volume", volume)

    def speak(self, text: str):
        """Speak the given text.
        :param text: The text to speak.
        """
        engine.say(text)
        engine.runAndWait()
