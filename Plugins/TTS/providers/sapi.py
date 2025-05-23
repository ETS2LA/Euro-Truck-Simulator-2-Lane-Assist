from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
import pyttsx3

engine = pyttsx3.init()
engine_voices = engine.getProperty('voices')

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
    
    def initialize(self, plugin):
        ...
        
    def select_voice(self, voice):
        super().select_voice(voice)
        engine.setProperty('voice', voice.id)
        
    def speak(self, text: str):
        """
        Speak the given text.
        :param text: The text to speak.
        """
        engine.say(text)
        engine.runAndWait()