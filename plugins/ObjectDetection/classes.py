from modules.Raycasting.main import RaycastResponse as Raycast
from typing import Literal, List, Tuple

class Object:
    id: int
    objectType: str
    screenPoints: list
    position: Tuple[float, float, float]
    
    def __init__(self, id, objectType, screenPoints, position=(0, 0, 0)):
        self.id = id
        self.objectType = objectType
        self.screenPoints = screenPoints
        self.position = position
        
    def json(self) -> dict:
        return {
            "id": self.id,
            "position": self.position,
            "objectType": self.objectType,
            "screenPoints": self.screenPoints
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id}"

class TrafficLight(Object):
    state: Literal["red", "yellow", "green"]
    position: Tuple[float, float, float]
    
    def __init__(self, id, objectType, screenPoints, state, position=(0, 0, 0)):
        super().__init__(id, objectType, screenPoints)
        self.state = state
        self.position = position
        
    def json(self) -> dict:
        return {
            **super().json(),
            "state": self.state
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and state {self.state}"

class Sign(Object):
    signType: Literal["stop", 
                      "yield", 
                      "speedlimit", 
                      "info", 
                      "mandatory", 
                      "warning", 
                      "priority", 
                      "prohibitory",
                      "regulatory", 
                      "service", 
                      "railroad", 
                      "additional"]
    
    def __init__(self, id, objectType, screenPoints, signType, position):
        super().__init__(id, objectType, screenPoints, position=position)
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
    distance: float
    
    def __init__(self, id, objectType, screenPoints, raycasts, speed=0, distance=0):
        super().__init__(id, objectType, screenPoints)
        self.raycasts = raycasts
        self.speed = speed
        self.distance = distance
        
    def json(self) -> dict:
        return {
            **super().json(),
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "speed": self.speed,
            "distance": self.distance
        }
        
    def fromJson(self, json: dict):
        return Vehicle(json["id"], json["objectType"], json["screenPoints"], [Raycast.fromJson(raycast) for raycast in json["raycasts"]], json["speed"], json["distance"])
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and speed {self.speed}"
    
class RoadMarker(Object):
    markerType: Literal["solid", "broken", "dotted", "double"]
    
    def __init__(self, id, objectType, screenPoints, position, markerType = "solid"):
        super().__init__(id, objectType, screenPoints, position=position)
        self.markerType = markerType
        
    def json(self) -> dict:
        return {
            **super().json(),
            "markerType": self.markerType
        }
        
    def __str__(self) -> str:
        return f"{self.objectType} with id {self.id} and type {self.markerType}"