import math

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