class Point:
    """Representation of a 2D point.

    :param float x: The x-coordinate of the point.
    :param float y: The y-coordinate of the point.
    
    Usage:
    >>> point = Point(1, 2)
    >>> point = Point(*list)
    """
    x: float
    y: float
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
    def tuple(self):
        return (self.x, self.y)
    
    def json(self):
        return {"x": self.x, "y": self.y}
    
        
class Coordinate:
    """Representation of a 3D coordinate.
    
    :param float x: The x-coordinate of the point.
    :param float y: The y-coordinate of the point.
    :param float z: The z-coordinate of the point.
    
    Usage:
    >>> Coordinate = Coordinate(1, 2, 3)
    >>> Coordinate = Coordinate(*list)
    """
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def tuple(self):
        return (self.x, self.y, self.z)
    
    def json(self): 
        return {"x": self.x, "y": self.y, "z": self.z}
    

class Color:
    """A color with r,g,b and a values.

    :param int r: The red value of the color.
    :param int g: The green value of the color. 
    :param int b: The blue value of the color.
    :param int a: The alpha value of the color.
    
    Usage:
    >>> color = Color(255, 255, 255) # a = 255
    >>> color = Color(255, 255, 255, 150)
    >>> color = Color(*list)
    """
    r: int
    g: int
    b: int
    a: int
    
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
    def tuple(self):
        return (self.r, self.g, self.b, self.a)
    
    def json(self):
        return {"r": self.r, "g": self.g, "b": self.b, "a": self.a}


class Rectangle:
    """A 2D rectangle. Can also be rendered from 3D coordinates.

    :param Point | Coordinate start: The start point of the rectangle.
    :param Point | Coordinate end: The end point of the rectangle.
    :param Color color: The color of the rectangle.
    :param Color fill: The fill color of the rectangle.
    :param int thickness: The thickness of the rectangle.
    
    Usage:
    >>> rect = Rectangle(Point(1, 2), Point(3, 4))
    >>> rect = Rectangle(Coordinate(1, 2, 3), Coordinate(4, 5, 6))
    """
    start: Point | Coordinate
    end: Point | Coordinate
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    
    def __init__(self, 
                 start: Point | Coordinate, 
                 end: Point | Coordinate, 
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1):
        self.start = start
        self.end = end
        self.color = color
        self.fill = fill
        self.thickness = thickness
        
    def json(self):
        return {
            "start": self.start.json(),
            "end": self.end.json(),
            "color": self.color.json(),
            "fill": self.fill.json(),
            "thickness": self.thickness
        }
        
        
class Line:
    """A 2D line. Can also be rendered between 3D coordinates.

    :param Point | Coordinate start: The start point of the line.
    :param Point | Coordinate end: The end point of the line.
    :param Color color: The color of the line.
    :param int thickness: The thickness of the line.
    
    Usage:
    >>> line = Line(Point(1, 2), Point(3, 4))
    """
    start: Point | Coordinate
    end: Point | Coordinate
    color: Color = Color(255, 255, 255, 255)
    thickness: int = 1
    
    def __init__(self, 
                 start: Point | Coordinate, 
                 end: Point | Coordinate, 
                 color: Color = Color(255, 255, 255, 255), 
                 thickness: int = 1):
        self.start = start
        self.end = end
        self.color = color
        self.thickness = thickness
        
    def json(self):
        return {
            "start": self.start.json(),
            "end": self.end.json(),
            "color": self.color.json(),
            "thickness": self.thickness
        }
        

class Polygon:
    """A 2D polygon rendered over a list of points. Can also be rendered from 3D coordinates.

    :param list[Point | Coordinate] points: The points of the polygon.
    :param Color color: The color of the polygon.
    :param Color fill: The fill color of the polygon.
    :param int thickness: The thickness of the polygon.
    :param bool closed: Whether the polygon is closed or not. (ie. the last point is connected to the first point)
    
    Usage:
    >>> polygon = Polygon([Point(1, 2), Point(3, 4), Point(5, 6)])
    """
    points: list[Point | Coordinate]
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    closed: bool = True
    
    def __init__(self, 
                 points: list[Point | Coordinate], 
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1, 
                 closed: bool = True):
        self.points = points
        self.color = color
        self.fill = fill
        self.thickness = thickness
        self.closed = closed
        
    def json(self):
        return {
            "points": [point.json() for point in self.points],
            "color": self.color.json(),
            "fill": self.fill.json(),
            "thickness": self.thickness,
            "closed": self.closed
        }
        

class Circle:
    """A 2D circle rendered from a center point and a radius. Can also be rendered from 3D coordinates.

    :param Point | Coordinate center: The center point of the circle.
    :param float radius: The radius of the circle.
    :param Color color: The color of the circle.
    :param Color fill: The fill color of the circle.
    :param int thickness: The thickness of the circle.
    
    Usage:
    >>> circle = Circle(Point(1, 2), radius=150)
    """
    center: Point | Coordinate
    radius: float = 100
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    
    def __init__(self, 
                 center: Point | Coordinate, 
                 radius: float = 100,
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1):
        self.center = center
        self.radius = radius
        self.color = color
        self.fill = fill
        self.thickness = thickness
        
    def json(self):
        return {
            "center": self.center.json(),
            "radius": self.radius,
            "color": self.color.json(),
            "fill": self.fill.json(),
            "thickness": self.thickness
        }