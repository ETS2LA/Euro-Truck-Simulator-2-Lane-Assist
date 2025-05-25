from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
import sounddevice as sd
import os

# Manually defining only the best voices.
voices = [
    TTSVoice(name="Heart - American English", id="af_heart"),
    TTSVoice(name="Bella - American English", id="af_bella"),
    TTSVoice(name="Nicole - American English (ASMR)", id="af_nicole"),
    TTSVoice(name="Michael - American English", id="am_michael"),
    TTSVoice(name="Puck - American English", id="am_puck"),
    TTSVoice(name="Emma - British English", id="bf_emma"),
    TTSVoice(name="Dora - Spanish", id="ef_dora"),
    TTSVoice(name="Alex - Spanish", id="em_alex"),
    TTSVoice(name="Siwis - French", id="ff_siwis"),
    TTSVoice(name="Sara - Italian", id="if_sara"),
    TTSVoice(name="Nicola - Italian", id="im_nicola"),
    TTSVoice(name="Dora - Brazilian Portuguese", id="pf_dora"),
    TTSVoice(name="Alex - Brazilian Portuguese", id="pm_alex"),
]

class Provider(TTSProvider):
    name = "Kokoro"
    voices = voices
    languages = None

    custom_text = "Kokoro is an open source TTS engine that uses a small scale neural network to generate believable speech."
    
    speed = 1.0
    volume = 0.5
    
    def initialize(self, plugin):
        global KPipeline
        plugin.state.text = "Loading Kokoro..."
        try:
            from kokoro import KPipeline
        except ImportError:
            plugin.state.text = "Installing Kokoro..."
            print("Installing docopt-ng")
            os.system("pip install docopt-ng")
            print("Installing kokoro")
            os.system("pip install kokoro")
            plugin.state.text = "Loading Kokoro..."
            from kokoro import KPipeline # If you get an error here then restart ETS2LA. Most likely already installed and your computer doesn't support hotplugging modules.
            
        plugin.state.reset()
        
    def select_voice(self, voice):
        super().select_voice(voice)
        
        pipeline = None
        if "American" in voice.name:
            pipeline = KPipeline(lang_code='a')
        elif "British" in voice.name:
            pipeline = KPipeline(lang_code='b')
        elif "Spanish" in voice.name:
            pipeline = KPipeline(lang_code='e')
        elif "French" in voice.name:
            pipeline = KPipeline(lang_code='f')
        elif "Italian" in voice.name:
            pipeline = KPipeline(lang_code='i')
        elif "Brazilian" in voice.name:
            pipeline = KPipeline(lang_code='p')
        else:
            pipeline = KPipeline(lang_code='a')
            
        self.pipeline = pipeline
        self.voice = voice.id
        
    def set_speed(self, speed):
        self.speed = speed
        
    def set_volume(self, volume):
        self.volume = volume
        
    def speak(self, text: str):
        """
        Speak the given text.
        :param text: The text to speak.
        """
        generator = self.pipeline(text, voice=self.voice)
        for i, (gs, ps, audio) in enumerate(generator):
            #samples /= np.iinfo(np.int16).max # normalize -1 - 1
            audio *= self.volume
            sd.play(audio, samplerate=24000 * self.speed)
            sd.wait()