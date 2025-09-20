from ETS2LA.Events import Event
import random


class Position:
    x: float
    y: float
    z: float

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def randomize(self, range_min: float = -100.0, range_max: float = 100.0):
        self.x = random.uniform(range_min, range_max)
        self.y = random.uniform(range_min, range_max)
        self.z = random.uniform(range_min, range_max)


class MyEvent(Event):
    alias = "my_event"
    current_time: float
    data: list
