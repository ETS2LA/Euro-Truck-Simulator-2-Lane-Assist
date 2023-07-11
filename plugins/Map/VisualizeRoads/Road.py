from plugins.Map.VisualizeRoads.Node import Node
from plugins.Map.VisualizeRoads.RoadLook import RoadLook

class Road:
    DlcGuard = 0
    RoadLook = RoadLook()
    IsSecret = False
    Uid = 0
    Nodes = []
    BlockSize = 0
    Valid = True
    Type = 0
    X = 0
    Y = 0
    Hidden = False
    StartNode = Node()
    EndNode = Node()
    Width = 9