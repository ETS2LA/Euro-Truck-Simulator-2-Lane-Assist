from Modules.PositionEstimation.classes import HeadTranslation, Position
import math

def GetHeadTranslation(data):
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
        truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)

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
        head_rotation_degrees_x = 0
        head_x = 0
        head_y = 0
        head_z = 0
        
    # Angle = 0 because it will be updated later
    return HeadTranslation(head_x, head_y, head_z, 0, head_rotation_degrees_x)

def GetPosition(data):
    try:
        truck_x = data["api"]["truckPlacement"]["coordinateX"]
        truck_y = data["api"]["truckPlacement"]["coordinateY"]
        truck_z = data["api"]["truckPlacement"]["coordinateZ"]
    except:
        truck_x = 0
        truck_y = 0 
        truck_z = 0 
        
    return Position(truck_x, truck_y, truck_z)