import ETS2LA.variables as variables
import logging
import math
import sys


sys.path.append(f"{variables.PATH}ETS2LA/Assets/CppUtils/ets2la_AR")
ets2la_AR_imported = False
try:
    import ets2la_AR
    ets2la_AR_imported = True
except:
    # print(f"WARNING: Could not import ets2la_AR from the CppUtils! Doing calculations in Python instead.")
    ...

def ConvertCoordinateToScreen(coordinate, self):
    if type(coordinate) != Coordinate:
        return None

    if ets2la_AR_imported:
        screen_x, screen_y, distance = ets2la_AR.game_to_screen_coordinate(
            coordinate.x,
            coordinate.y,
            coordinate.z,
            self.HeadX,
            self.HeadY,
            self.HeadZ,
            self.InsideHeadX,
            self.InsideHeadY,
            self.InsideHeadZ,
            self.HeadRotationDegreesY,
            self.HeadRotationDegreesX,
            self.HeadRotationDegreesZ,
            self.CabinOffsetRotationDegreesY,
            self.CabinOffsetRotationDegreesX,
            self.CabinOffsetRotationDegreesZ,
            self.FOV,
            self.WindowPosition[0],
            self.WindowPosition[1],
            self.WindowPosition[2],
            self.WindowPosition[3],
            coordinate.relative,
            coordinate.rotation_relative
        )

        if screen_x is None: # cant return single None in c++
            return None

        return screen_x, screen_y, distance

    else:

        X = coordinate.x
        Y = coordinate.y
        Z = coordinate.z

        HeadYaw = self.HeadRotationDegreesX
        HeadPitch = self.HeadRotationDegreesY
        HeadRoll = self.HeadRotationDegreesZ

        if coordinate.relative:
            # If the head and inside positions match, then the relative X is the same as the absolute X
            # we want to add the position so that it works even when the head is not the same as inside head
            RelativeX = X
            RelativeY = Y
            RelativeZ = Z

            if abs(self.HeadX - self.InsideHeadX) > 1 or abs(self.HeadY - self.InsideHeadY) > 1 or abs(self.HeadZ - self.InsideHeadZ) > 1:
                return None # TODO: Implement relative coordinates for other cameras

            if coordinate.rotation_relative:
                # Rotate the points around the head (0, 0, 0)
                CosPitch = math.cos(math.radians(self.CabinOffsetRotationDegreesY))
                SinPitch = math.sin(math.radians(self.CabinOffsetRotationDegreesY))
                NewY = RelativeY * CosPitch - RelativeZ * SinPitch
                NewZ = RelativeZ * CosPitch + RelativeY * SinPitch

                CosYaw = math.cos(math.radians(self.CabinOffsetRotationDegreesX))
                SinYaw = math.sin(math.radians(self.CabinOffsetRotationDegreesX))
                NewX = RelativeX * CosYaw + NewZ * SinYaw
                NewZ = NewZ * CosYaw - RelativeX * SinYaw

                CosRoll = math.cos(math.radians(0))#-CabinOffsetRotationDegreesZ))
                SinRoll = math.sin(math.radians(0))#-CabinOffsetRotationDegreesZ))
                FinalX = NewX * CosRoll - NewY * SinRoll
                FinalY = NewY * CosRoll + NewX * SinRoll

                RelativeX = FinalX
                RelativeY = FinalY
                RelativeZ = NewZ
        else:
            RelativeX = X - self.HeadX
            RelativeY = Y - self.HeadY
            RelativeZ = Z - self.HeadZ

        CosYaw = math.cos(math.radians(-HeadYaw))
        SinYaw = math.sin(math.radians(-HeadYaw))
        NewX = RelativeX * CosYaw + RelativeZ * SinYaw
        NewZ = RelativeZ * CosYaw - RelativeX * SinYaw

        CosPitch = math.cos(math.radians(-HeadPitch))
        SinPitch = math.sin(math.radians(-HeadPitch))
        NewY = RelativeY * CosPitch - NewZ * SinPitch
        FinalZ = NewZ * CosPitch + RelativeY * SinPitch

        CosRoll = math.cos(math.radians(-HeadRoll))
        SinRoll = math.sin(math.radians(-HeadRoll))
        FinalX = NewX * CosRoll - NewY * SinRoll
        FinalY = NewY * CosRoll + NewX * SinRoll

        if FinalZ >= 0:
            return None

        FovRad = math.radians(self.FOV)

        WindowDistance = ((self.WindowPosition[3] - self.WindowPosition[1]) * (4 / 3) / 2) / math.tan(FovRad / 2)

        ScreenX = (FinalX / FinalZ) * WindowDistance + (self.WindowPosition[2] - self.WindowPosition[0]) / 2
        ScreenY = (FinalY / FinalZ) * WindowDistance + (self.WindowPosition[3] - self.WindowPosition[1]) / 2

        ScreenX = (self.WindowPosition[2] - self.WindowPosition[0]) - ScreenX

        Distance = math.sqrt((RelativeX ** 2) + (RelativeY ** 2) + (RelativeZ ** 2))

        return ScreenX, ScreenY, Distance


class Point:
    """Representation of a 2D point.

    :param float x: The x-coordinate of the point.
    :param float y: The y-coordinate of the point.
    :param Coordinate anchor: The anchor coordinate of the point. The point will be an offset to the 3D coordinate.
    
    Usage:
    >>> point = Point(1, 2)
    >>> point = Point(*list)
    >>> point = Point(1, 2, anchor=Coordinate(3, 4, 5))
    """
    x: float
    y: float
    anchor = None
    
    def __init__(self, x: float, y: float, anchor = None):
        self.x = x
        self.y = y
        self.anchor = anchor
        
    def tuple(self):
        return (self.x, self.y)

    def screen(self, plugin):
        if type(self.anchor) == Coordinate:
            anchor = self.anchor.screen(plugin)
            if anchor is None:
                return None
            
            point = anchor[:2]
            return point[0] + self.x, point[1] + self.y
            
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
    relative: bool = False
    """Tells AR to render the point relative to the current head position."""
    rotation_relative: bool = False
    """Tells AR to rotate the object relative to the head. This way X is right left, Y is up down and Z is forward backward."""
    
    def __init__(self, x: float, y: float, z: float, relative: bool = False, rotation_relative: bool = False):
        self.x = x
        self.y = y
        self.z = z
        self.relative = relative
        self.rotation_relative = rotation_relative
        
    def tuple(self):
        return (self.x, self.y, self.z)
    
    def screen(self, plugin):
        return ConvertCoordinateToScreen(self, plugin)
    
    def get_distance_to(self, x, y, z):
        return ((self.x - x) ** 2 + (self.y - y) ** 2 + (self.z - z) ** 2) ** 0.5
    
    def json(self): 
        return {"x": self.x, "y": self.y, "z": self.z}
    
    def __str__(self):
        return f"Coordinate({self.x}, {self.y}, {self.z})"
    
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other):
        return Coordinate(self.x * other, self.y * other, self.z * other)
    
    def __truediv__(self, other):
        return Coordinate(self.x / other, self.y / other, self.z / other)
    

class Fade:
    """A fade effect applied to a renderable 3D object. 2D objects are not affected.

    :param float prox_fade_end: The distance at which the proximity fade ends (opacity is 0).
    :param float prox_fade_start: The distance at which the proximity fade starts (opacity starts to decrease).
    :param float dist_fade_start: The distance at which the distance fade starts (opacity starts to decrease).
    :param float dist_fade_end: The distance at which the distance fade ends (opacity is 0).
    """
    prox_fade_end: float = 10
    prox_fade_start: float = 30
    dist_fade_start: float = 150
    dist_fade_end: float = 170
    
    def __init__(self,
                 prox_fade_end: float = 10,
                 prox_fade_start: float = 30,
                 dist_fade_start: float = 150,
                 dist_fade_end: float = 170):
            self.prox_fade_end = prox_fade_end
            self.prox_fade_start = prox_fade_start
            self.dist_fade_start = dist_fade_start
            self.dist_fade_end = dist_fade_end
            
    def json(self):
        return {
            "prox_fade_end": self.prox_fade_end,
            "prox_fade_start": self.prox_fade_start,
            "dist_fade_start": self.dist_fade_start,
            "dist_fade_end": self.dist_fade_end
        }
        
    def tuple(self):
        return (self.prox_fade_end, self.prox_fade_start, self.dist_fade_start, self.dist_fade_end)

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
    am: float
    
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.am = 1.0

    def tuple(self):
        return (self.r, self.g, self.b, self.a * self.am)
    
    def json(self):
        return {"r": self.r, "g": self.g, "b": self.b, "a": self.a}


class Rectangle:
    """A 2D rectangle. Can also be rendered from 3D coordinates.

    :param Point | Coordinate start: The start point of the rectangle.
    :param Point | Coordinate end: The end point of the rectangle.
    :param Color color: The color of the rectangle.
    :param Color fill: The fill color of the rectangle.
    :param int thickness: The thickness of the rectangle.
    :param Fade fade: The fade effect applied to the rectangle. (Only affects 3D objects)
    :param float custom_distance: A custom distance to be used for fade calculations
    
    Usage:
    >>> rect = Rectangle(Point(1, 2), Point(3, 4))
    >>> rect = Rectangle(Coordinate(1, 2, 3), Coordinate(4, 5, 6))
    """
    start: Point | Coordinate
    end: Point | Coordinate
    rounding: float = 0.0
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    fade: Fade = Fade()
    custom_distance: float | None = None
    
    def __init__(self, 
                 start: Point | Coordinate, 
                 end: Point | Coordinate, 
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1,
                 fade: Fade = Fade(),
                 custom_distance: float = None,
                 rounding: float = 0.0):
        self.start = start
        self.end = end
        self.rounding = rounding
        self.color = color
        self.fill = fill
        self.thickness = thickness
        self.fade = fade
        self.custom_distance = custom_distance
        
    def is_3D(self):
        return isinstance(self.start, Coordinate)
    
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        if self.is_3D():
            start_distance = self.start.get_distance_to(x, y, z) if not self.start.relative else self.start.get_distance_to(0, 0, 0)
            end_distance = self.end.get_distance_to(x, y, z) if not self.end.relative else self.end.get_distance_to(0, 0, 0)
            return (start_distance + end_distance) / 2
        return 0
        
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
    :param Fade fade: The fade effect applied to the line. (Only affects 3D objects)
    :param float custom_distance: A custom distance to be used for fade calculations
    
    Usage:
    >>> line = Line(Point(1, 2), Point(3, 4))
    """
    start: Point | Coordinate
    end: Point | Coordinate
    color: Color = Color(255, 255, 255, 255)
    thickness: int = 1
    fade: Fade = Fade()
    custom_distance: float | None = None
    
    def __init__(self, 
                 start: Point | Coordinate, 
                 end: Point | Coordinate, 
                 color: Color = Color(255, 255, 255, 255), 
                 thickness: int = 1,
                 fade: Fade = Fade(),
                 custom_distance: float = None):
        self.start = start
        self.end = end
        self.color = color
        self.thickness = thickness
        self.fade = fade
        self.custom_distance = custom_distance
        
    def is_3D(self):
        return isinstance(self.start, Coordinate)
    
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        if self.is_3D():
            start_distance = self.start.get_distance_to(x, y, z) if not self.start.relative else self.start.get_distance_to(0, 0, 0)
            end_distance = self.end.get_distance_to(x, y, z) if not self.end.relative else self.end.get_distance_to(0, 0, 0)
            return (start_distance + end_distance) / 2
        return 0
        
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
    :param Fade fade: The fade effect applied to the polygon. (Only affects 3D objects)
    :param float custom_distance: A custom distance to be used for fade calculations
    
    Usage:
    >>> polygon = Polygon([Point(1, 2), Point(3, 4), Point(5, 6)])
    """
    points: list[Point | Coordinate]
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    closed: bool = True
    fade: Fade = Fade()
    custom_distance: float | None = None
    
    def __init__(self, 
                 points: list[Point | Coordinate], 
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1, 
                 closed: bool = True,
                 fade: Fade = Fade(),
                 custom_distance: float = None):
        self.points = points
        self.color = color
        self.fill = fill
        self.thickness = thickness
        self.closed = closed
        self.fade = fade
        self.custom_distance = custom_distance
        
    def is_3D(self):
        return isinstance(self.points[0], Coordinate)
    
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        if self.is_3D():
            distances = [
                point.get_distance_to(x, y, z) if not point.relative else point.get_distance_to(0, 0, 0)
                for point in self.points
            ]
            return sum(distances) / len(distances)
        return 0
        
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
    :param Fade fade: The fade effect applied to the circle. (Only affects 3D objects)
    :param float custom_distance: A custom distance to be used for fade calculations
    
    Usage:
    >>> circle = Circle(Point(1, 2), radius=150)
    """
    center: Point | Coordinate
    radius: float = 100
    color: Color = Color(255, 255, 255, 255)
    fill: Color = Color(0, 0, 0, 0)
    thickness: int = 1
    fade: Fade = Fade()
    custom_distance: float | None = None
    
    def __init__(self, 
                 center: Point | Coordinate, 
                 radius: float = 100,
                 color: Color = Color(255, 255, 255, 255), 
                 fill: Color = Color(0, 0, 0, 0), 
                 thickness: int = 1,
                 fade: Fade = Fade(),
                 custom_distance: float = None):
        self.center = center
        self.radius = radius
        self.color = color
        self.fill = fill
        self.thickness = thickness
        self.fade = fade
        self.custom_distance = custom_distance
        
    def is_3D(self):
        return isinstance(self.center, Coordinate)
    
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        if self.is_3D():
            return self.center.get_distance_to(x, y, z) if not self.center.relative else self.center.get_distance_to(0, 0, 0)
        return 0
        
    def json(self):
        return {
            "center": self.center.json(),
            "radius": self.radius,
            "color": self.color.json(),
            "fill": self.fill.json(),
            "thickness": self.thickness
        }
        

class Text:
    """A 2D text rendered at a point. Can also be rendered from 3D coordinates.

    :param Point | Coordinate point: The point where the text is rendered.
    :param str text: The text to render.
    :param Color color: The color of the text.
    :param int size: The size of the text.
    :param Fade fade: The fade effect applied to the text. (Only affects 3D objects)
    :param float custom_distance: A custom distance to be used for fade calculations
    
    Usage:
    >>> text = Text(Point(1, 2), "Hello World!")
    """
    point: Point | Coordinate
    text: str
    color: Color = Color(255, 255, 255, 255)
    size: int = 12
    fade: Fade = Fade()
    custom_distance: float | None = None
    
    def __init__(self, 
                 point: Point | Coordinate, 
                 text: str,
                 color: Color = Color(255, 255, 255, 255), 
                 size: int = 12,
                 fade: Fade = Fade(),
                 custom_distance: float = None):
        self.point = point
        self.text = text
        self.color = color
        self.size = size
        self.fade = fade
        self.custom_distance = custom_distance
        
    def is_3D(self):
        return isinstance(self.point, Coordinate)
    
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        if self.is_3D():
            return self.point.get_distance_to(x, y, z) if not self.point.relative else self.point.get_distance_to(0, 0, 0)
        return 0
        
    def json(self):
        return {
            "point": self.point.json(),
            "text": self.text,
            "color": self.color.json(),
            "size": self.size
        }
        
class Bezier:
    """A 2D Bezier curve rendered from four points, can only be rendered in 2D.
    
    :param Point p1: The first control point of the Bezier curve.
    :param Point p2: The second control point of the Bezier curve.
    :param Point p3: The third control point of the Bezier curve.
    :param Point p4: The fourth control point of the Bezier curve.
    :param Color color: The color of the Bezier curve.
    :param float thickness: The thickness of the Bezier curve.
    :param int segments: The number of segments to use for the Bezier curve. More segments means smoother curve but more performance cost.
    :param float custom_distance: A custom distance to be used for fade calculations
    :param Fade fade: The fade effect applied to the Bezier curve. (Only works with custom_distance)
    
    """
    
    p1: Point
    p2: Point
    p3: Point
    p4: Point
    color: Color = Color(255, 255, 255, 255)
    thickness: float = 1.0
    segments: int = 10
    custom_distance: float | None = None
    fade: Fade = Fade()
    
    def __init__(self, 
                 p1: Point, 
                 p2: Point, 
                 p3: Point, 
                 p4: Point, 
                 color: Color = Color(255, 255, 255, 255), 
                 thickness: float = 1.0,
                 segments: int = 100,
                 custom_distance: float | None = None,
                 fade: Fade = Fade()):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.color = color
        self.thickness = thickness
        self.segments = segments
        self.custom_distance = custom_distance
        self.fade = fade
        
    def get_distance(self, x: float, y: float, z: float):
        if self.custom_distance is not None:
            return self.custom_distance
        return 0
        
    def is_3D(self):
        return False  # Bezier curves are always rendered in 2D
        
    def json(self):
        return {
            "p1": self.p1.json(),
            "p2": self.p2.json(),
            "p3": self.p3.json(),
            "p4": self.p4.json(),
            "color": self.color.json(),
            "thickness": self.thickness,
            "segments": self.segments
        }