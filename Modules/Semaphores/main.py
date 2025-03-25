from Modules.Semaphores.classes import Gate, TrafficLight, Position, Quaternion
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
            size = 1040
            self.buf = mmap.mmap(0, size, r"Local\ETS2LASemaphore")
            time.sleep(0.1)
    
    def get_route_information(self):
        if self.buf is None:
            return None
        
        try:
            semaphore_format = "fffffffffifii"
            total_format = "=" + semaphore_format * 20
            data = struct.unpack(total_format, self.buf[:1040])
            
            semaphores = []
            for i in range(0,20):
                if data[9] == 1:
                    semaphore = TrafficLight(
                        Position(data[0], data[1], data[2]),
                        data[3],
                        data[4],
                        Quaternion(data[5], data[6], data[7], data[8]),
                        data[10],
                        data[11],
                        data[12]
                    )
                else:
                    semaphore = Gate(
                        Position(data[0], data[1], data[2]),
                        data[3],
                        data[4],
                        Quaternion(data[5], data[6], data[7], data[8]),
                        data[10],
                        data[11],
                        data[12]
                    )
                    
                semaphores.append(semaphore)
                data = data[13:]
            
            return semaphores
        except:
            logging.exception("Failed to read route information")
            return None
    
    def run(self):
        return self.get_route_information()