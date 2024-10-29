from types import SimpleNamespace
from pydantic import BaseModel
from typing import Literal
import time

class CancelledJob(BaseModel):
    timestamp: float = 0
    special: bool = False
    started_time: int = 0
    cancelled_time: int = 0
    cancelled_penalty: int = 0
    
    def json(self):
        return self.model_dump()
        
    def fromAPIData(self, data):
        self.timestamp = time.time()
        self.special = data["configBool"]["specialJob"]
        self.started_time = data["gameplayUI"]["jobStartingTime"]
        self.cancelled_time = data["gameplayUI"]["jobFinishedTime"]
        self.cancelled_penalty = data["gameplayLongLong"]["jobCancelledPenalty"]

class FinishedJob(BaseModel):
    timestamp: float = 0
    
    special: bool = False
    
    cargo: str = ""
    cargo_id: str = ""
        
    unit_mass: float = 0
    unit_count: int = 0
    
    starting_time: int = 0
    finished_time: int = 0
    delivered_delivery_time: int = 0
    
    delivered_autoload_used: bool = False
    delivered_autopark_used: bool = False
    
    delivered_cargo_damage: float = 0
    
    delivered_distance_km: float = 0
    
    delivered_revenue: int = 0
    
    def json(self):
        return self.model_dump()
        
    def fromAPIData(self, data):
        self.timestamp = time.time()
        
        self.special = data["configBool"]["specialJob"]
        
        self.cargo = data["configString"]["cargo"]
        self.cargo_id = data["configString"]["cargoId"]
        
        self.unit_mass = data["configFloat"]["unitMass"]
        self.unit_count = data["configUI"]["unitCount"]
        
        self.starting_time = data["gameplayUI"]["jobStartingTime"]
        self.finished_time = data["gameplayUI"]["jobFinishedTime"]
        self.delivered_delivery_time = data["gameplayUI"]["jobDeliveredDeliveryTime"]
        
        self.delivered_autoload_used = data["gameplayBool"]["jobDeliveredAutoloadUsed"]
        self.delivered_autopark_used = data["gameplayBool"]["jobDeliveredAutoparkUsed"]
        
        self.delivered_cargo_damage = data["gameplayFloat"]["jobDeliveredCargoDamage"]
        
        self.delivered_distance_km = data["gameplayFloat"]["jobDeliveredDistanceKm"]
        
        self.delivered_revenue = data["gameplayLongLong"]["jobDeliveredRevenue"]
    
class Job(BaseModel):
    timestamp: float = 0
    
    special: bool = False
    
    cargo: str = ""
    cargo_id: str = ""
    
    unit_mass: float = 0
    unit_count: int = 0
    
    delivered_delivery_time: int = 0
    starting_time: int = 0
    finished_time: int = 0
    
    delivered_cargo_damage: float = 0
    delivered_distance_km: float = 0
    
    delivered_autopark_used: bool = False
    delivered_autoload_used: bool = False
    
    income: int = 0
    delivered_revenue: int = 0
    cancelled_penalty: int = 0
    
    event_type: Literal["delivered", "cancelled", "loaded"] = "loaded"
    
    def json(self):
        return self.model_dump()
    
    def fromAPIData(self, data):
        self.timestamp = time.time()
        
        self.special = data["configBool"]["specialJob"]
        
        self.cargo = data["configString"]["cargo"]
        self.cargo_id = data["configString"]["cargoId"]
        
        self.unit_mass = data["configFloat"]["unitMass"]
        self.unit_count = data["configUI"]["unitCount"]
        
        self.delivered_delivery_time = data["gameplayUI"]["jobDeliveredDeliveryTime"]
        self.starting_time = data["gameplayUI"]["jobStartingTime"]
        self.finished_time = data["gameplayUI"]["jobFinishedTime"]
        
        self.delivered_cargo_damage = data["gameplayFloat"]["jobDeliveredCargoDamage"]
        self.delivered_distance_km = data["gameplayFloat"]["jobDeliveredDistanceKm"]

        self.delivered_autopark_used = data["gameplayBool"]["jobDeliveredAutoparkUsed"]
        self.delivered_autoload_used = data["gameplayBool"]["jobDeliveredAutoloadUsed"]
        
        self.income = data["configLongLong"]["jobIncome"]
        self.delivered_revenue = data["gameplayLongLong"]["jobDeliveredRevenue"]
        self.cancelled_penalty = data["gameplayLongLong"]["jobCancelledPenalty"]
        
        if data["specialBool"]["onJob"] == True:
            self.event_type = "loaded"
        elif data["specialBool"]["jobCancelled"] == True:
            self.event_type = "cancelled"
        elif data["specialBool"]["jobFinished"] == True:
            self.event_type = "delivered"
            
class Refuel(BaseModel):
    timestamp: float = 0
    refuelAmount: float = 0
    type: Literal["started", "payed"] = "started"
    
    def json(self):
        return self.model_dump()
        
    def fromAPIData(self, data):
        self.timestamp = time.time()
        if data["specialBool"]["refuelPayed"] == True:
            self.type = "payed"
        self.refuelAmount = data["gameplayFloat"]["refuelAmount"]