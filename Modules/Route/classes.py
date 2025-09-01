class RouteItem:
    uid: int
    distance: float
    time: float

    def __init__(self, uid: int, distance: float, time: float):
        self.uid = uid
        self.distance = distance
        self.time = time

    def __str__(self):
        return f"RouteItem({self.uid}, {self.distance / 1000:.1f} km, {self.time / 60:.1f} min)"
