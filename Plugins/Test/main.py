# Framework
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *

from ETS2LA.Utils.Values.numbers import SmoothedValue
import matplotlib
import logging
import random
import time
import sys

class Plugin(ETS2LAPlugin):
    fps_cap = 999
    
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Camera"],
        listen=["*.py"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    sending = SmoothedValue("time", 10)
    receiving = SmoothedValue("time", 10)
    
    sending_bandwidth = SmoothedValue("time", 10)
    receiving_bandwidth = SmoothedValue("time", 10)
    
    sending_jitter = 0
    receiving_jitter = 0
    
    last_jitter_update = time.time()
    
    steering = False
    
    def init(self):
        self.dictionary = {}
        print("Please allow up to 10s for values to stabilize")
        print("Initializing dictionary...")
        count = 200000
        for i in range(count):
            self.dictionary[i] = i
            if i % count/100 == 0:
                print(f"{i} / {count} ({(i/count)*100:.2f}%)", end="\r")
        self.payload_size = sys.getsizeof(self.dictionary)
        print("Dictionary size: ", f"{self.payload_size/1000/1000:.2f}", "MB")
    
    def imports(self):
        ...

    def run(self):
        start_time = time.time()
        self.globals.tags.test = self.dictionary
        sending_ms = (time.time() - start_time) * 1000
        
        start_time = time.time()
        test = self.globals.tags.test
        receiving_ms = (time.time() - start_time) * 1000
        
        self.sending.smooth(sending_ms)
        self.receiving.smooth(receiving_ms)
        
        receive_bandwidth = self.payload_size / (receiving_ms / 1000) / 1000 / 1000
        send_bandwidth = self.payload_size / (sending_ms / 1000) / 1000 / 1000
        
        self.sending_bandwidth.smooth(send_bandwidth)
        self.receiving_bandwidth.smooth(receive_bandwidth)

        if time.time() - self.last_jitter_update > 1:
            self.last_jitter_update = time.time()
            sending_lower = self.sending.zero_percent_jitter("lower")
            sending_upper = self.sending.zero_percent_jitter("upper")
            self.sending_jitter = sending_upper - sending_lower
            
            receiving_lower = self.receiving.zero_percent_jitter("lower")
            receiving_upper = self.receiving.zero_percent_jitter("upper")
            self.receiving_jitter = receiving_upper - receiving_lower
        
        print(f"Send: {self.sending.get():.2f} ms @ {self.sending_bandwidth.get():.2f} MB/s (jitter ±{self.sending_jitter:.2f} ms), Receive: {self.receiving.get():.2f} ms @ {self.receiving_bandwidth.get():.2f} MB/s (jitter ±{self.receiving_jitter:.2f} ms)      ", end="\r")