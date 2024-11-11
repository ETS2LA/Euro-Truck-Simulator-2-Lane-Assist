import plugins.Map.classes as c

class NavigationLane():
    length: float = 0
    start: c.Position = None
    end: c.Position = None
    item: c.Item = None
    lane: c.Lane | c.PrefabNavRoute = None