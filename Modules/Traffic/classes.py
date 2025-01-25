import math

class Position():
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def is_zero(self):
        return self.x == 0 and self.y == 0 and self.z == 0
        
    def __str__(self):
        return f"Position({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
class Quaternion():
    w: float
    x: float
    y: float
    z: float
    
    def __init__(self, w: float, x: float, y: float, z: float):
        self.w = w
        self.x = y
        self.y = x
        self.z = z
        
    def euler(self): # Convert to pitch, yaw, roll
        """
        var yaw = atan2(2.0*(q.y*q.z + q.w*q.x), q.w*q.w - q.x*q.x - q.y*q.y + q.z*q.z);
        var pitch = asin(-2.0*(q.x*q.z - q.w*q.y));
        var roll = atan2(2.0*(q.x*q.y + q.w*q.z), q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z);
        """
        yaw = math.atan2(2.0*(self.y*self.z + self.w*self.x), self.w*self.w - self.x*self.x - self.y*self.y + self.z*self.z)
        pitch = math.asin(-2.0*(self.x*self.z - self.w*self.y))
        roll = math.atan2(2.0*(self.x*self.y + self.w*self.z), self.w*self.w + self.x*self.x - self.y*self.y - self.z*self.z)
        
        yaw = math.degrees(yaw)
        pitch = math.degrees(pitch)
        roll = math.degrees(roll)
        
        return pitch, yaw, roll 
        
    def is_zero(self):
        return self.w == 0 and self.x == 0 and self.y == 0 and self.z == 0
        
    def __str__(self):
        x, y, z = self.euler()
        return f"Quaternion({self.w:.2f}, {self.x:.2f}, {self.y:.2f}, {self.z:.2f}) -> (pitch {x:.2f}, yaw {y:.2f}, roll {z:.2f})"
    
    def __dict__(self):
        euler = self.euler()
        return {
            "w": self.w,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pitch": euler[0],
            "yaw": euler[1],
            "roll": euler[2]
        }

class Size:
    width: float
    height: float
    length: float
    
    def __init__(self, width: float, height: float, length: float):
        self.width = width
        self.height = height
        self.length = length
        
    def __str__(self):
        return f"Size({self.width:.2f}, {self.height:.2f}, {self.length:.2f})"

class Trailer:
    position: Position
    rotation: Quaternion
    size: Size
    
    def __init__(self, position: Position, rotation: Quaternion, size: Size):
        self.position = position
        self.rotation = rotation
        self.size = size
        
    def is_zero(self):
        return self.position.is_zero() and self.rotation.is_zero()
        
    def __str__(self):
        return f"Trailer({self.position}, {self.rotation}, {self.size})"
    
    def __dict__(self):
        return {
            "position": self.position.__dict__,
            "rotation": self.rotation.__dict__(),
            "size": self.size.__dict__
        }

class Vehicle:
    position: Position
    rotation: Quaternion
    size: Size
    speed: float
    acceleration: float
    trailer_count: int
    id: int
    trailers: list[Trailer]
    
    def __init__(self, position: Position, rotation: Quaternion, size: Size, speed: float, acceleration: float, trailer_count: int, id: int, trailers: list[Trailer]):
        self.position = position
        self.rotation = rotation
        self.size = size
        self.speed = speed
        self.acceleration = acceleration
        self.trailer_count = trailer_count
        self.id = id
        self.trailers = trailers
        
    def is_zero(self):
        return self.position.is_zero() and self.rotation.is_zero()
        
    def __str__(self):
        return f"Vehicle({self.position}, {self.rotation}, {self.size}, {self.speed:.2f}, {self.acceleration:.2f}, {self.trailer_count}, {self.trailers})"

    def __dict__(self):
        return {
            "position": self.position.__dict__,
            "rotation": self.rotation.__dict__(),
            "size": self.size.__dict__,
            "speed": self.speed,
            "acceleration": self.acceleration,
            "trailer_count": self.trailer_count,
            "id": self.id,
            "trailers": [trailer.__dict__() for trailer in self.trailers]
        }