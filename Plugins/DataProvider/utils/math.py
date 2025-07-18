from typing import Literal
from scipy.spatial.transform import Rotation as R
import numpy as np
import math

def DistanceBetweenPoints(p1: tuple[float, float] | tuple[float, float, float], p2: tuple[float, float] | tuple[float, float, float]) -> float:
    """Get the distance between two points.

    :param tuple[float, float] | tuple[float, float, float] p1: Point 1.
    :param tuple[float, float] | tuple[float, float, float] p2: Point 2.
    :return float: Distance
    """
    if len(p1) == 2:
        return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))
    else:
        return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) + math.pow(p2[2] - p1[2], 2))
    
def LerpTuple(from_tuple: tuple[float, float] | tuple[float, float, float], to_tuple: tuple[float, float] | tuple[float, float, float], s: float) -> tuple[float, float] | tuple[float, float, float]:
    """Lerp between two tuples.

    :param tuple[float, float] | tuple[float, float, float] from_tuple: Tuple to lerp from.
    :param tuple[float, float] | tuple[float, float, float] to_tuple: Tuple to lerp to.
    :param float s: The interpolation value.
    :return tuple[float, float] | tuple[float, float, float]: The lerped tuple.
    """
    if len(from_tuple) == 2:
        return ((1 - s) * from_tuple[0] + s * to_tuple[0], (1 - s) * from_tuple[1] + s * to_tuple[1])
    else:
        return ((1 - s) * from_tuple[0] + s * to_tuple[0], (1 - s) * from_tuple[1] + s * to_tuple[1], (1 - s) * from_tuple[2] + s * to_tuple[2])
    
def TupleMiddle(t1: tuple[float, float] | tuple[float, float, float], t2: tuple[float, float] | tuple[float, float, float]) -> tuple[float, float] | tuple[float, float, float]:
    """Get the middle point between two tuples.

    :param tuple[float, float] | tuple[float, float, float] t1: Tuple 1.
    :param tuple[float, float] | tuple[float, float, float] t2: Tuple 2.
    :return tuple[float, float] | tuple[float, float, float]: The middle point between the two tuples.
    """
    if len(t1) == 2:
        return ((t1[0] + t2[0]) / 2, (t1[1] + t2[1]) / 2)
    else:
        return ((t1[0] + t2[0]) / 2, (t1[1] + t2[1]) / 2, (t1[2] + t2[2]) / 2)

def IsInBoundingBox(point: tuple[float, float], min_x: float, max_x: float, min_y: float, max_y: float) -> bool:
    """Check if a point is in a bounding box.

    :param tuple[float, float] point: Point to check.
    :param float min_x: Minimum x value of the bounding box.
    :param float max_x: Maximum x value of the bounding box.
    :param float min_y: Minimum y value of the bounding box.
    :param float max_y: Maximum y value of the bounding box.
    :return bool: True if the point is in the bounding box, False otherwise.
    """
    return min_x <= point[0] <= max_x and min_y <= point[1] <= max_y

def IsInFront(point: tuple[float, float] | tuple[float, float, float], truck_rotation: float, truck_position: tuple[float, float] | tuple[float, float, float]) -> bool:
    """Will return True if a point is in front of the truck, False otherwise.

    :param tuple[float, float] | tuple[float, float, float] point: Point to check, must be either [x,z] or [x,y,z]
    :param float truck_rotation: Truck rotation, should be gotten from the data.truck_rotation variable.
    :param tuple[float, float] | tuple[float, float, float] truck_position: Must be the same format as point.
    :return bool: True if the point is in front of the truck, False otherwise.
    """
    forward_vector = [-math.sin(truck_rotation), -math.cos(truck_rotation)]
    point_forward_vector = [point[0] - truck_position[0], point[len(point)-1] - truck_position[len(truck_position)-1]]
    angle = math.acos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
    angle = math.degrees(angle)
    return -90 < angle < 90

def GetMostInDirection(points: list[tuple[float, float]] | list[tuple[float, float, float]], truck_rotation: float, truck_position: tuple[float, float] | tuple[float, float, float], direction: Literal["left", "straight", "right"] = "straight") -> int:
    """Find the index of the point that is most to the direction specified.

    :param list[tuple[float, float]] | list[tuple[float, float, float]] points: List of points to check.
    :param float truck_rotation: Truck rotation, should be gotten from the data.truck_rotation variable.
    :param tuple[float, float] | tuple[float, float, float] truck_position: Must be the same format as the points.
    :param Literal["left", "straight", "right"] direction: The direction to check for. Defaults to "straight".
    :return int: Index of the point that is most straight ahead of the truck.
    """
    forward_vector = [-math.sin(truck_rotation), -math.cos(truck_rotation)]
    target_angle = 0 if direction == "straight" else 90 if direction == "right" else -90
    forward_vector = RotateAroundPoint(forward_vector[0], forward_vector[1], math.radians(target_angle), 0, 0)
    best_index = 0
    best_angle = 180
    for i, point in enumerate(points):
        point_forward_vector = [point[0] - truck_position[0], point[len(point)-1] - truck_position[len(truck_position)-1]]
        angle = math.acos(np.dot(forward_vector, point_forward_vector) / (np.linalg.norm(forward_vector) * np.linalg.norm(point_forward_vector)))
        angle = math.degrees(angle)
        if angle < best_angle:
            best_angle = angle
            best_index = i
    
    return best_index

def InOut(s: float) -> float:
    """InOut interpolation function.

    :param float s: Interpolation value.
    :return float: InOut interpolated value.
    """
    return 3 * math.pow(s, 2) - 2 * math.pow(s, 3)

def EaseOutInverted(s: float) -> float:
    """EaseOutInverted interpolation function.

    :param float s: Interpolation value.
    :return float: EaseOutInverted interpolated value.
    """
    return 1 - s * s

def Hermite(s, x, z, tanX, tanZ):
    """Hermite interpolation function.

    :param float s: The interpolation value.
    :param float x: The x value.
    :param float z: The z value.
    :param float tanX: The tangent x value.
    :param float tanZ: The tangent z value.
    :return float: The hermite interpolated value.
    """
    h1 = 2 * math.pow(s, 3) - 3 * math.pow(s, 2) + 1
    h2 = -2 * math.pow(s, 3) + 3 * math.pow(s, 2)
    h3 = math.pow(s, 3) - 2 * math.pow(s, 2) + s
    h4 = math.pow(s, 3) - math.pow(s, 2)
    return h1 * x + h2 * z + h3 * tanX + h4 * tanZ


def RotateAroundPoint(x: float, y: float, angle: float, origin_x: float, origin_y: float) -> tuple[float, float]:
    """Rotate a point around another point.

    :param float x: X coordinate of the point to rotate.
    :param float y: Y (Z) coordinate of the point to rotate.
    :param float angle: Angle to rotate the point by in radians.
    :param float origin_x: X coordinate of the origin point.
    :param float origin_y: Y (Z) coordinate of the origin point.
    :return tuple[float, float]: The rotated point.
    """
    s = math.sin(angle)
    c = math.cos(angle)
    
    x -= origin_x
    y -= origin_y
    
    new_x = x * c - y * s
    new_y = x * s + y * c
    
    return new_x + origin_x, new_y + origin_y

def VectorBetweenPoints(p1: tuple[float, float] | tuple[float, float, float], p2: tuple[float, float] | tuple[float, float, float]) -> tuple[float, float]:
    """Get the vector between two points.

    :param tuple[float, float] | tuple[float, float, float] p1: Point 1.
    :param tuple[float, float] | tuple[float, float, float] p2: Point 2.
    :return tuple[float, float]: The vector between the two points.
    """
    if len(p1) == 2:
        return p2[0] - p1[0], p2[1] - p1[1]
    else:
        return p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    

def QuatToEuler(quat: list[float]) -> list[float]:
    """Convert quaternion to Euler angles with game-specific adjustments.
    
    :param list[float] quat: Quaternion in [w,x,y,z] format
    :return list[float]: Euler angles [pitch, yaw, roll] in radians
    """
    try:
        qw, qx, qy, qz = quat
        
        # Pitch (X rotation)
        pitch = math.atan2(-qx, qw) * 2 - math.pi / 2
        
        # Yaw (Y rotation) - from original code
        yaw = math.atan2(-qy, qw) * 2 - math.pi / 2
        
        # Roll (Z rotation)
        roll = math.atan2(-qz, qw) * 2 - math.pi / 2
        
        return [pitch, yaw, roll]
    except:
        return [0, 0, 0]


def hermite_curve(P0, P1, T0, T1, t):
    """Hermite interpolation function.

    :param (np.array) P0: The starting position (x, y, z).
    :param (np.array) P1: The ending position (x, y, z).
    :param (np.array) T0: The tangent at start position (x, y, z).
    :param (np.array) T1: The tangent at end position (x, y, z).
    :param float t: The interpolation value between 0 and 1.

    :return (np.array) P_t: The hermite interpolated position (x,y,z).
    """
    # Hermite basis functions
    P_t = (
            (2 * t ** 3 - 3 * t ** 2 + 1) * P0 +
            (t ** 3 - 2 * t ** 2 + t) * T0 +
            (-2 * t ** 3 + 3 * t ** 2) * P1 +
            (t ** 3 - t ** 2) * T1
    )
    return P_t


def quaternion_rotate(q, v):
    """Rotate vector by quaternion.

    :param (np.array) q: quaternion in (w,x,y,z) format.
    :param (np.array) v: vector (x,y,z) to be rotated.
    :return (np.array) v_rotated: rotated vector (x,y,z).
    """
    # Scipy use quaternion in (x, y, z, w) format
    qw, qx, qy, qz = q
    q = np.array([qx, qy, qz, qw])

    q_norm = q / np.linalg.norm(q)  # Normalize
    r = R.from_quat(q_norm)
    v_rotated = r.apply(v)
    return v_rotated


def Hermite3D(s, start_pos, end_pos, start_quaternion, end_quaternion, length):
    """Hermite interpolation function in 3D space.

    :param float s: The interpolation value between 0 and 1.
    :param tuple[float, float, float] start_pos: The starting position (x,y,z).
    :param tuple[float, float, float] end_pos: The ending position (x,y,z).
    :param tuple[float, float, float] start_quaternion: The starting quaternion (w,x,y,z).
    :param tuple[float, float, float] end_quaternion: The ending quaternion (w,x,y,z).
    :param float length: The length of the road.
    :return tuple[float, float, float]: The hermite interpolated position (x,y,z).
    """
    if length is None or length == 0:
        length = DistanceBetweenPoints(start_pos, end_pos)

    # Initial vector defined by [0, 0, -1] * road length
    initial_vector = np.array([0, 0, -1]) * length

    # Calculate tangent at start/end node using initial vector and quaternion
    tan_start = quaternion_rotate(start_quaternion, initial_vector)
    tan_end = quaternion_rotate(end_quaternion, initial_vector)

    return hermite_curve(np.array(start_pos), np.array(end_pos), tan_start, tan_end, s)
