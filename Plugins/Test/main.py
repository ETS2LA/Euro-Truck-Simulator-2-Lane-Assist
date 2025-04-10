# Framework
from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *
from ETS2LA.Plugin import *

from ETS2LA.Utils.Values.numbers import SmoothedValue
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
    
    steering = False
    
    def init(self):
        self.dictionary = {}
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
        
        print(f"Send: {self.sending.get():.2f} ms ({self.sending_bandwidth.get():.2f} MB/s), Receive: {self.receiving.get():.2f} ms ({self.receiving_bandwidth.get():.2f} MB/s)      ", end="\r")