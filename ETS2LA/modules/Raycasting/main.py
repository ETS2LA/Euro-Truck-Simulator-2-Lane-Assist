import numpy
import math
import mouse
import screeninfo
from ETS2LA.plugins.runner import PluginRunner

FOV = 80 # Vertical fov in degrees
CAMERA_HEIGHT = 1.5 # Height of the camera in meters
WHEEL_OFFSET = 0.5 # Wheel size to offset the camera in meters

runner:PluginRunner = None

def Initialize():
    global API
    API = runner.modules.TruckSimAPI

def GetScreenPointAngle(x, y, headRotation):
    # Get the screen size
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width
    screen_height = screen.height
    # Get the percentage of the screen the mouse is at
    x_percentage = x / screen_width
    y_percentage = y / screen_height
    # Check if the mouse is at the top or bottom of the screen
    if y_percentage < 0.5:
        # Calculate the angle
        verticalAngle = - (0.5 - y_percentage) * FOV
    else:
        # Calculate the angle
        verticalAngle = (y_percentage - 0.5) * FOV
        
    # Calculate the horizontal fov
    vFOVrad = FOV * math.pi / 180
    hFOVrad = 2 * math.atan(math.tan(vFOVrad / 2) * (screen_width / screen_height))
    hFOVdeg = hFOVrad * 180 / math.pi
    # print(hFOVdeg)
    # Calculate the horizontal angle
    horizontalAngle = (x_percentage - 0.5) * hFOVdeg
    
    # Add the head rotation to the angles to get the final angles
    horizontalAngle -= headRotation[0]
    verticalAngle -= headRotation[1]

    # TODO: WTF does this magic number mean
    return (horizontalAngle * 1 , verticalAngle)
    

def GetCollisionPointWithGround(horizontalAngle, verticalAngle):
    try:
        # Calculate the horizontal distance to the point
        horizontal_distance = CAMERA_HEIGHT / math.tan(math.radians(verticalAngle))
        # Calculate the x and z coordinates of the point
        x = horizontal_distance * math.sin(math.radians(-horizontalAngle))
        z = horizontal_distance * math.cos(math.radians(horizontalAngle))
        y = 0
    except:
        x = 0
        y = 0
        z = 0
    return (x, y, z)

def RotateAroundCenter(point, center, angle):
    """Rotate a point around a center point.

    Args:
        point (tuple): Point to rotate.
        center (tuple): Center point.
        angle (float): Angle in radians.

    Returns:
        tuple: Rotated point.
    """
    pointX = point[0] - center[0]
    pointY = point[1] - center[1]
    newx = pointX * math.cos(angle) - pointY * math.sin(angle)
    newy = pointX * math.sin(angle) + pointY * math.cos(angle)
    return (newx + center[0], newy + center[1])

def GetValuesFromAPI():
    global CAMERA_HEIGHT
    
    data = {}
    data["api"] = API.run()
    try:
        truck_x = data["api"]["truckPlacement"]["coordinateX"]
        truck_y = data["api"]["truckPlacement"]["coordinateY"]
        truck_z = data["api"]["truckPlacement"]["coordinateZ"]
        truck_rotation_x = data["api"]["truckPlacement"]["rotationX"]
        truck_rotation_y = data["api"]["truckPlacement"]["rotationY"]
        truck_rotation_z = data["api"]["truckPlacement"]["rotationZ"]

        cabin_offset_x = data["api"]["headPlacement"]["cabinOffsetX"] + data["api"]["configVector"]["cabinPositionX"]
        cabin_offset_y = data["api"]["headPlacement"]["cabinOffsetY"] + data["api"]["configVector"]["cabinPositionY"]
        cabin_offset_z = data["api"]["headPlacement"]["cabinOffsetZ"] + data["api"]["configVector"]["cabinPositionZ"]
        cabin_offset_rotation_x = data["api"]["headPlacement"]["cabinOffsetrotationX"]
        cabin_offset_rotation_y = data["api"]["headPlacement"]["cabinOffsetrotationY"]
        cabin_offset_rotation_z = data["api"]["headPlacement"]["cabinOffsetrotationZ"]

        head_offset_x = data["api"]["headPlacement"]["headOffsetX"] + data["api"]["configVector"]["headPositionX"] + cabin_offset_x
        head_offset_y = data["api"]["headPlacement"]["headOffsetY"] + data["api"]["configVector"]["headPositionY"] + cabin_offset_y
        head_offset_z = data["api"]["headPlacement"]["headOffsetZ"] + data["api"]["configVector"]["headPositionZ"] + cabin_offset_z
        head_offset_rotation_x = data["api"]["headPlacement"]["headOffsetrotationX"]
        head_offset_rotation_y = data["api"]["headPlacement"]["headOffsetrotationY"]
        head_offset_rotation_z = data["api"]["headPlacement"]["headOffsetrotationZ"]
        
        truck_rotation_degrees_x = truck_rotation_x * 360
        if truck_rotation_degrees_x < 0:
            truck_rotation_degrees_x = 360 + truck_rotation_degrees_x
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)
        
        truck_rotation_degrees_y = truck_rotation_y * 360
        if truck_rotation_degrees_y < 0:
            truck_rotation_degrees_y = 360 + truck_rotation_degrees_y
        truck_rotation_radians_y = -math.radians(truck_rotation_degrees_y)
        
        truck_rotation_degrees_z = truck_rotation_z * 360
        if truck_rotation_degrees_z < 0:
            truck_rotation_degrees_z = 360 + truck_rotation_degrees_z
        truck_rotation_radians_z = -math.radians(truck_rotation_degrees_z)

        head_rotation_degrees_x = (truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360
        while head_rotation_degrees_x > 360:
            head_rotation_degrees_x = head_rotation_degrees_x - 360

        head_rotation_degrees_y = (truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360

        head_rotation_degrees_z = (truck_rotation_z + cabin_offset_rotation_z + head_offset_rotation_z) * 360

        point_x = head_offset_x
        point_y = head_offset_y
        point_z = head_offset_z
        head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
        head_y = point_y * math.cos(math.radians(head_rotation_degrees_y)) - point_z * math.sin(math.radians(head_rotation_degrees_y)) + truck_y
        head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z

    except:

        truck_x = 0
        truck_y = 0
        truck_z = 0
        truck_rotation_x = 0
        truck_rotation_y = 0
        truck_rotation_z = 0

        cabin_offset_x = 0
        cabin_offset_y = 0
        cabin_offset_z = 0
        cabin_offset_rotation_x = 0
        cabin_offset_rotation_y = 0
        cabin_offset_rotation_z = 0

        head_offset_x = 0
        head_offset_y = 0
        head_offset_z = 0
        head_offset_rotation_x = 0
        head_offset_rotation_y = 0
        head_offset_rotation_z = 0

        truck_rotation_degrees_x = 0
        truck_rotation_radians_x = 0

        head_rotation_degrees_x = 0
        head_rotation_degrees_y = 0
        head_rotation_degrees_z = 0

        head_x = 0
        head_y = 0
        head_z = 0

    CAMERA_HEIGHT = head_y - truck_y + WHEEL_OFFSET
    # Remove the truck rotation from the head rotation (normalize truck rotation as the plane rotation)
    head_rotation_x = head_rotation_degrees_x - truck_rotation_degrees_x
    head_rotation_y = head_rotation_degrees_y - truck_rotation_degrees_y
    head_rotation_z = head_rotation_degrees_z - truck_rotation_degrees_z
    # Remove the truck position from the head position (normalize truck position as the plane position)
    head_x = head_x - truck_x
    head_y = head_y - truck_y
    head_z = head_z - truck_z
    # Return the values
    return (head_x, head_y, head_z), (head_rotation_x, head_rotation_y, head_rotation_z), (truck_x, truck_y, truck_z), (truck_rotation_radians_x, truck_rotation_radians_y, truck_rotation_radians_z)

def run(x=None, y=None):
    # Get values from the API
    headPos, headRotation, truckPos, truckRotation = GetValuesFromAPI()
    # Get the mouse position
    if x == None and y == None:
        x, y = mouse.get_position()
    # Calculate the angle of the ray
    horizontal, vertical = GetScreenPointAngle(x, y, headRotation)
    # Get the position of the collision point 
    point = GetCollisionPointWithGround(horizontal, vertical)
    # Distance to the point
    distance = math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)
    # Add the truck position back to the point
    point = (point[0] + truckPos[0], point[1] + truckPos[1], point[2] + truckPos[2])
    # Rotate the point around the truck to match the truck rotation
    new_x, new_z = RotateAroundCenter((point[0], point[2]), (truckPos[0], truckPos[2]), truckRotation[0] + math.pi)
    # Return the values
    return (new_x, point[1], new_z), distance