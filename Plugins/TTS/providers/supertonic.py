from Plugins.TTS.providers.provider import TTSProvider, TTSVoice
from ETS2LA.Plugin import ETS2LAPlugin
from ETS2LA.variables import PATH
import sounddevice as sd
import os

# Manually defining only the best voices.
voices = [
    TTSVoice(name="F1 - English", id="F1"),
    TTSVoice(name="F2 - English", id="F2"),
    TTSVoice(name="M1 - English", id="M1"),
    TTSVoice(name="M2 - English", id="M2"),
]


class Provider(TTSProvider):
    name = "Supertonic"
    voices = voices
    languages = None

    custom_text = "Supertonic is a very fast and open source TTS engine that uses a small scale neural network to generate believable speech."

    speed = 1.0
    volume = 0.5
    denoise_steps = 10 # basically the quality setting, more is better but slower
    pipeline = None

    def initialize(self, plugin: ETS2LAPlugin):
        global load_text_to_speech, load_voice_style
        plugin.state.text = "Loading Supertonic..."

        # set hf home to an app folder not the %USERPROFILE%/.cache/huggingface which is used by default
        os.environ["HF_HOME"] = os.path.join(PATH, "cache")

        try:
            from Plugins.TTS.providers.supertonic_helper import load_text_to_speech, load_voice_style
        except ImportError:
            plugin.state.text = "Installing Supertonic..."
            print("Installing onnxruntime")
            os.system("pip install onnxruntime")
            print("Installing huggingface_hub")
            os.system("pip install huggingface_hub")
            plugin.state.text = "Loading Supertonic..."
            from Plugins.TTS.providers.supertonic_helper import load_text_to_speech, load_voice_style

        plugin.state.reset()

    def select_voice(self, voice):
        super().select_voice(voice)
        try:
            self.voice = load_voice_style([os.path.join(PATH, "cache", "supertonic", "voice_styles", voice.id + ".json")], verbose=False)
        except FileNotFoundError:
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id="Supertone/supertonic",
                local_dir=os.path.join(PATH, "cache", "supertonic")
            )
            self.voice = load_voice_style([os.path.join(PATH, "cache", "supertonic", "voice_styles", voice.id + ".json")], verbose=False)

        if self.pipeline is None:
            try:
                self.pipeline = load_text_to_speech(
                    onnx_dir=os.path.join(PATH, "cache", "supertonic", "onnx"),
                    use_gpu=False, # not supported as of commit 8d42b55
                )
            except FileNotFoundError:
                from huggingface_hub import snapshot_download
                snapshot_download(
                    repo_id="Supertone/supertonic",
                    local_dir=os.path.join(PATH, "cache", "supertonic")
                )
                self.pipeline = load_text_to_speech(
                    onnx_dir=os.path.join(PATH, "cache", "supertonic", "onnx"),
                    use_gpu=False, # not supported as of commit 8d42b55
                )

    def set_speed(self, speed):
        self.speed = speed

    def set_volume(self, volume):
        self.volume = volume

    def speak(self, text: str):
        """Speak the given text.
        :param text: The text to speak.
        """
        wav, duration = self.pipeline(
            text,
            self.voice,
            self.denoise_steps,
            float(self.speed)
        )
        w = wav[0, : int(self.pipeline.sample_rate * duration[0].item())]
        w *= self.volume
        sd.play(w, samplerate=self.pipeline.sample_rate)
        sd.wait()