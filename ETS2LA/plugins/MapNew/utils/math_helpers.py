import math

def DistanceBetweenPoints(p1: tuple[float, float] | tuple[float, float, float], p2: tuple[float, float] | tuple[float, float, float]) -> float:
    if len(p1) == 2:
        return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))
    else:
        return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) + math.pow(p2[2] - p1[2], 2))
    
def LerpTuple(from_tuple: tuple[float, float] | tuple[float, float, float], to_tuple: tuple[float, float] | tuple[float, float, float], s: float) -> tuple[float, float] | tuple[float, float, float]:
    if len(from_tuple) == 2:
        return ((1 - s) * from_tuple[0] + s * to_tuple[0], (1 - s) * from_tuple[1] + s * to_tuple[1])
    else:
        return ((1 - s) * from_tuple[0] + s * to_tuple[0], (1 - s) * from_tuple[1] + s * to_tuple[1], (1 - s) * from_tuple[2] + s * to_tuple[2])
    
def TupleMiddle(t1: tuple[float, float] | tuple[float, float, float], t2: tuple[float, float] | tuple[float, float, float]) -> tuple[float, float] | tuple[float, float, float]:
    if len(t1) == 2:
        return ((t1[0] + t2[0]) / 2, (t1[1] + t2[1]) / 2)
    else:
        return ((t1[0] + t2[0]) / 2, (t1[1] + t2[1]) / 2, (t1[2] + t2[2]) / 2)

def IsInBoundingBox(point: tuple[float, float], min_x: float, max_x: float, min_y: float, max_y: float) -> bool:
    return min_x <= point[0] <= max_x and min_y <= point[1] <= max_y

def Hermite(s, x, z, tanX, tanZ):
    h1 = 2 * math.pow(s, 3) - 3 * math.pow(s, 2) + 1
    h2 = -2 * math.pow(s, 3) + 3 * math.pow(s, 2)
    h3 = math.pow(s, 3) - 2 * math.pow(s, 2) + s
    h4 = math.pow(s, 3) - math.pow(s, 2)
    return h1 * x + h2 * z + h3 * tanX + h4 * tanZ

def RotateAroundPoint(x: float, y: float, angle: float, origin_x: float, origin_y: float) -> tuple[float, float]:
    s = math.sin(angle)
    c = math.cos(angle)
    
    x -= origin_x
    y -= origin_y
    
    new_x = x * c - y * s
    new_y = x * s + y * c
    
    return (new_x + origin_x, new_y + origin_y)