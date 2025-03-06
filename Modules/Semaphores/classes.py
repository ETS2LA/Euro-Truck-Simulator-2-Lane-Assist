from typing import Literal
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
    
    def __dict__(self): # type: ignore
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

class Semaphore():
    position: Position
    cx: float
    cy: float
    quat: Quaternion
    type: Literal["gate", "traffic_light"]
    time_left: float
    state: int
    id: int
    
    def __init__(self, position: Position, cx: float, cy: float, quat: Quaternion, type: int, time_left: float, state: int, id: int):
        self.position = position
        self.cx = cx
        self.cy = cy
        self.quat = quat
        self.type = "traffic_light" if type == 1 else "gate"
        self.time_left = time_left
        self.state = state
        self.id = id
        
    def __str__(self):
        return f"Semaphore({self.position}, {self.cx:.2f}, {self.cy:.2f}, {self.quat}, {self.type}, {self.time_left:.2f}, {self.state}, {self.id})"

# Traffic light states
OFF = 0
ORANGE_TO_RED = 1
RED = 2
ORANGE_TO_GREEN = 4
GREEN = 8
SLEEP = 32

# Gate states
CLOSING = 0
CLOSED = 1
OPENING = 2
OPEN = 3
        
class TrafficLight(Semaphore):
    def __init__(self, position: Position, cx: float, cy: float, quat: Quaternion, time_left: float, state: int, id: int):
        super().__init__(position, cx, cy, quat, 1, time_left, state, id)
        
    def __str__(self):
        text = f"Traffic light {self.id} - "
        if self.state == OFF:
            text += "OFF"
        elif self.state == ORANGE_TO_RED:
            text += "ORANGE_TO_RED"
        elif self.state == RED:
            text += "RED"
        elif self.state == ORANGE_TO_GREEN:
            text += "ORANGE_TO_GREEN"
        elif self.state == GREEN:
            text += "GREEN"
        elif self.state == SLEEP:
            text += "SLEEP"
            
        text += f" ({self.time_left:.1f}s left)"
        return f"{text}"

class Gate(Semaphore):
    def __init__(self, position: Position, cx: float, cy: float, quat: Quaternion, time_left: float, state: int, id: int):
        super().__init__(position, cx, cy, quat, 2, time_left, state, id)
        
    def __str__(self):
        text = "Gate - "
        if self.state == CLOSING:
            text += "CLOSING"
        elif self.state == CLOSED:
            text += "CLOSED"
        elif self.state == OPENING:
            text += "OPENING"
        elif self.state == OPEN:
            text += "OPEN"
            
        text += f" ({self.time_left:.1f}s left)"
        return f"{text}"