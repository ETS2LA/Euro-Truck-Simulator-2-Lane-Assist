import sounddevice as sd
import numpy as np
import threading
import time


# Used by the main file to play beeps based on the angle
# and the distance to the closest road. Useful for
# accessibility for blind users.
class ProximityBeep:
    def __init__(self):
        self.running = False
        self.thread = None
        self.current_angle = 0
        self.current_distance = 0
        self.sample_rate = 44100
        self.beep_thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

    def set_angle(self, angle, target_angle=0):
        diff = ((angle - target_angle + 180) % 360) - 180
        self.current_angle = abs(diff)

    def set_distance(self, distance):
        """Set the distance to the closest road"""
        self.current_distance = max(0, min(distance, 100))

    def loop(self):
        while self.running:
            self.generate()

            if self.current_angle < 5:
                time.sleep(0.25)  # min 4 per second to avoid clipping
            else:
                delay = 0.25 + (self.current_angle / 180.0) * 0.75
                time.sleep(delay)

    def generate(self):
        """Generate a short beep with fixed pitch"""
        duration = 0.05  # 50ms
        frequency = 800  # Hz

        distance = min(self.current_distance, 100)
        volume = 0.3 + (distance / 100) * 0.7

        # Sine wave beep
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        beep = np.sin(2 * np.pi * frequency * t) * volume

        # Fade in and out to try and avoid clipping
        fade = int(self.sample_rate * 0.005)
        beep[:fade] = beep[:fade] * np.linspace(0, 1, fade)
        beep[-fade:] = beep[-fade:] * np.linspace(1, 0, fade)

        sd.play(beep, self.sample_rate, blocking=False)
