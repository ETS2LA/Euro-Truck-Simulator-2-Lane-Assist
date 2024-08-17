from typing import Literal, List, Tuple

class Object:
    id: int
    objectType: str
    screenPoints: list
    
    def __init__(self, id, objectType, screenPoints):
        self.id = id
        self.objectType = objectType
        self.screenPoints = screenPoints
        
    def json(self) -> dict:
        return {
            "id": self.id,
            "objectType": self.objectType,
            "screenPoints": self.screenPoints
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id}"

class TrafficLight(Object):
    state: Literal["red", "yellow", "green"]
    
    def __init__(self, id, objectType, screenPoints, state):
        super().__init__(id, objectType, screenPoints)
        self.state = state
        
    def json(self) -> dict:
        return {
            **super().json(),
            "state": self.state
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and state {self.state}"

class Sign(Object):
    signType: Literal["stop_sign", 
                      "yield_sign", 
                      "speedlimit_sign", 
                      "info_sign", 
                      "mandatory_sign", 
                      "warning_sign", 
                      "priority_sign", 
                      "prohibitory_sign",
                      "regulatory_sign", 
                      "service_sign", 
                      "railroad_sign", 
                      "additional_sign"]
    
    def __init__(self, id, objectType, screenPoints, signType):
        super().__init__(id, objectType, screenPoints)
        self.signType = signType
        
    def json(self) -> dict:
        return {
            **super().json(),
            "signType": self.signType
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and type {self.signType}"

class Vehicle(Object):
    raycasts: list
    speed: float
    
    def __init__(self, id, objectType, screenPoints, raycasts, speed=0):
        super().__init__(id, objectType, screenPoints)
        self.raycasts = raycasts
        self.speed = speed
        
    def json(self) -> dict:
        return {
            **super().json(),
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "speed": self.speed
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and speed {self.speed}"