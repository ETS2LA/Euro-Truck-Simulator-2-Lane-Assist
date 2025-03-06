from Modules.Route.classes import RouteItem
from ETS2LA.Module import *
import logging
import struct
import mmap
import time

class Module(ETS2LAModule):
    def imports(self):
        self.wait_for_buffer()
        
    def wait_for_buffer(self):
        self.buf = None
        while self.buf is None:
            size = 80_000
            self.buf = mmap.mmap(0, size, r"Local\ETS2LARoute")
            time.sleep(0.1)
    
    def get_route_information(self):
        if self.buf is None:
            return None
        
        try:
            format = "qff"
            total_format = "=" + format * 5000
            data = struct.unpack(total_format, self.buf[:80_000])
            
            items = []
            for i in range(0,5000):
                if data[0] == 0:
                    break
                
                item = RouteItem(data[0], data[1], data[2])
                items.append(item)
                data = data[3:]
            
            return items
        except:
            logging.exception("Failed to read route information")
            return None
    
    def run(self):
        return self.get_route_information()