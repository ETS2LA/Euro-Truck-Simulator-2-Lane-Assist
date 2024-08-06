class Vehicle:
    raycasts: list
    screenPoints: list
    vehicleType: str
    speed: float
    id: int
    
    def __init__(self, raycasts, screenPoints, vehicleType, id, speed=0):
        self.raycasts = raycasts
        self.screenPoints = screenPoints
        self.vehicleType = vehicleType
        self.id = id
        self.speed = speed
    
    def json(self):
        return {
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "screenPoints": self.screenPoints,
            "vehicleType": self.vehicleType,
            "speed": self.speed,
            "id": self.id
        }