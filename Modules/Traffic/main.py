from Modules.Traffic.classes import Position, Quaternion, Size, Trailer, Vehicle
from ETS2LA.Module import *
import logging
import struct
import mmap
import time

class Module(ETS2LAModule):
    vehicle_format = "ffffffffffffhh"
    trailer_format = "ffffffffff"
    vehicle_object_format = vehicle_format + trailer_format + trailer_format
    total_format = "=" + vehicle_object_format * 40
    
    last_vehicles: dict[int, Vehicle] = {}
    
    start_time = 0
    message_shown = False
    
    def imports(self):
        self.start_time = time.time()
        self.wait_for_buffer()
        
    def wait_for_buffer(self):
        self.buf = None
        while self.buf is None:
            try:
                size = 5280
                self.buf = mmap.mmap(0, size, r"Local\ETS2LATraffic")
            except: 
                if time.time() - self.start_time > 5 and not self.message_shown:
                    logging.warning("ETS2LATraffic buffer not found. Make sure the SDK is installed and the game is running. This plugin will wait until the buffer is available.")
                    self.message_shown = True
                    
            time.sleep(1)
            
    def create_vehicle_from_dict(self, data):
        position = Position(data["position"]["x"], data["position"]["y"], data["position"]["z"])
        rotation = Quaternion(data["rotation"]["x"], data["rotation"]["y"], data["rotation"]["z"], data["rotation"]["w"])
        size = Size(data["size"]["width"], data["size"]["height"], data["size"]["length"])
        speed = data["speed"]
        acceleration = data["acceleration"]
        trailer_count = data["trailer_count"]
        id = data["id"]
        
        trailers = []
        for trailer in data["trailers"]:
            trailer_position = Position(trailer["position"]["x"], trailer["position"]["y"], trailer["position"]["z"])
            trailer_rotation = Quaternion(trailer["rotation"]["x"], trailer["rotation"]["y"], trailer["rotation"]["z"], trailer["rotation"]["w"])
            trailer_size = Size(trailer["size"]["width"], trailer["size"]["height"], trailer["size"]["length"])
            
            trailers.append(Trailer(trailer_position, trailer_rotation, trailer_size))
        
        return Vehicle(position, rotation, size, speed, acceleration, trailer_count, id, trailers)
    
    def get_traffic(self):
        if self.buf is None:
            return None
        
        try:
            data = struct.unpack(self.total_format, self.buf[:5280])
            vehicles: list[Vehicle] = []
            for i in range(0, 40):
                position = Position(data[0], data[1], data[2])
                rotation = Quaternion(data[3], data[4], data[5], data[6])
                size = Size(data[7], data[8], data[9])
                speed = data[10]
                acceleration = data[11]
                trailer_count = data[12]
                id = data[13]
                
                trailers = []
                for j in range(0, trailer_count):
                    offset = 14 + (j * 10)
                    trailer_position = Position(data[offset], data[offset + 1], data[offset + 2])
                    trailer_rotation = Quaternion(data[offset + 3], data[offset + 4], data[offset + 5], data[offset + 6])
                    trailer_size = Size(data[offset + 7], data[offset + 8], data[offset + 9])
                    
                    trailers.append(Trailer(trailer_position, trailer_rotation, trailer_size))
                
                if not position.is_zero() and not rotation.is_zero():
                    vehicles.append(Vehicle(position, rotation, size, speed, acceleration, trailer_count, id, trailers))
                
                data = data[14 + (2 * 10):]
            
            if len(vehicles) > 0:
                if vehicles[0].is_tmp:
                    for vehicle in vehicles:
                        if vehicle.id in self.last_vehicles:
                            vehicle.update_from_last(self.last_vehicles[vehicle.id])

            self.last_vehicles = {vehicle.id: vehicle for vehicle in vehicles}
            return vehicles
        except:
            logging.exception("Failed to read camera properties")
            return None
    
    def run(self):
        return self.get_traffic()