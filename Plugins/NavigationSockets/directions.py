THROUGH = 0

SLIGHT_LEFT = 1
LEFT = 2
SHARP_LEFT = 3
U_TURN_LEFT = 4

SLIGHT_RIGHT = 11
RIGHT = 12
SHARP_RIGHT = 13
U_TURN_RIGHT = 14

MERGE = -1


def map_angle_to_direction(angle: float) -> int:
    if angle > 0:
        if angle < 10:
            return THROUGH
        if angle < 45:
            return SLIGHT_RIGHT
        elif angle < 135:
            return RIGHT
        elif angle < 225:
            return SHARP_RIGHT
        elif angle < 315:
            return U_TURN_RIGHT
        else:
            return THROUGH
    else:
        if angle > -10:
            return THROUGH
        if angle > -45:
            return SLIGHT_LEFT
        elif angle > -135:
            return LEFT
        elif angle > -225:
            return SHARP_LEFT
        elif angle > -315:
            return U_TURN_LEFT
        else:
            return THROUGH


class ThenHint:
    direction: int

    def __init__(self, direction: int):
        self.direction = direction


class Lane:
    id: int
    branches: list[int]
    active: int

    def __init__(self, branches: list[int], active: int = None, id: int = 0):
        self.id = id
        self.branches = branches
        self.active = active

    def to_dict(self):
        data = {
            "branches": self.branches,
        }
        if self.active is not None:
            data["activeBranch"] = self.active

        return data


class LaneHint:
    lanes: list[Lane]

    def __init__(self, lanes: list[Lane]):
        self.lanes = lanes

    def to_dict(self):
        return {"lanes": [lane.to_dict() for lane in self.lanes]}


class Name:
    icon: str
    text: str

    def __init__(self, icon: str, text: str):
        self.icon = icon
        self.text = text


class RouteDirection:
    direction: int
    distanceMeters: float
    name: Name = None
    laneHint: LaneHint = None
    thenHint: ThenHint = None

    def __init__(
        self,
        direction: int,
        distanceMeters: float,
        name: Name = None,
        laneHint: LaneHint = None,
        thenHint: ThenHint = None,
    ):
        self.direction = direction
        self.distanceMeters = distanceMeters
        self.name = name
        self.laneHint = laneHint
        self.thenHint = thenHint

    def to_dict(self):
        result = {"direction": self.direction, "distanceMeters": self.distanceMeters}
        if self.name:
            result["name"] = {"icon": self.name.icon, "text": self.name.text}
        if self.laneHint:
            result["laneHint"] = self.laneHint.to_dict()
        if self.thenHint:
            result["thenHint"] = {"direction": self.thenHint.direction}

        return result
