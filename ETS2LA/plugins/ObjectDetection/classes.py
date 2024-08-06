class Vehicle:
    raycasts: list
    screenPoints: list
    vehicleType: str
    def __init__(self, raycasts, screenPoints, vehicleType):
        self.raycasts = raycasts
        self.screenPoints = screenPoints
        self.vehicleType = vehicleType
    
    def json(self):
        return {
            "raycasts": [raycast.json() for raycast in self.raycasts],
            "screenPoints": self.screenPoints,
            "vehicleType": self.vehicleType
        }