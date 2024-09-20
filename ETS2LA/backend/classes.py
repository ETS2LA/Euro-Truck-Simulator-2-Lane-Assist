from typing import Literal
from types import SimpleNamespace

class Job:
    special: bool = False
    
    cargo: str = ""
    cargo_id: str = 0
    
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
        return {
            'special': self.special,
            'cargo': self.cargo,
            'cargo_id': self.cargo_id,
            'unit_mass': self.unit_mass,
            'unit_count': self.unit_count,
            'delivered_delivery_time': self.delivered_delivery_time,
            'starting_time': self.starting_time,
            'finished_time': self.finished_time,
            'delivered_cargo_damage': self.delivered_cargo_damage,
            'delivered_distance_km': self.delivered_distance_km,
            'delivered_autopark_used': self.delivered_autopark_used,
            'delivered_autoload_used': self.delivered_autoload_used,
            'income': self.income,
            'delivered_revenue': self.delivered_revenue,
            'cancelled_penalty': self.cancelled_penalty,
            'event_type': self.event_type
        }
    
    def fromAPIData(self, data):
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
        elif data["specialBool"]["jobFinished"] == True:
            self.event_type = "delivered"
        elif data["specialBool"]["jobCancelled"] == True:
            self.event_type = "cancelled"