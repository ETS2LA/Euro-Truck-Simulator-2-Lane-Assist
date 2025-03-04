from Modules.Camera.classes import Position, Quaternion, Camera
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
            size = 36
            self.buf = mmap.mmap(0, size, r"Local\ETS2LACameraProps")
            time.sleep(0.1)
    
    def get_camera_properties(self):
        if self.buf is None:
            return None
        
        try:
            format = "=ffffhhffff" # fov, x, y, z, cx, cz, qw, qx, qy, qz
            data = struct.unpack(format, self.buf[:36])
            
            camera_data = Camera(
                data[0],
                Position(data[1], data[2], data[3]),
                data[4],
                data[5],
                Quaternion(data[6], data[7], data[8], data[9])
            )
            
            return camera_data
        except:
            logging.exception("Failed to read camera properties")
            return None
    
    def run(self):
        return self.get_camera_properties()