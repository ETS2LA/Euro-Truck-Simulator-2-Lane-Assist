import math
import time

tmp_speed_update_frequency = 0.5  # seconds

# TODO: Switch __dict__ to __iter__ and dict() for typing support.
# TODO: f = Class() -> dict(f) instead of f.__dict__()


def rotate_around_point(point, center, pitch, yaw, roll):
    """
    Rotate a point around a center point by the given pitch, yaw, and roll angles (in degrees).

    Parameters:
    - point: [x, y, z] coordinates of the point to rotate
    - center: [x, y, z] coordinates of the center of rotation
    - pitch: rotation around X-axis (in degrees)
    - yaw: rotation around Y-axis (in degrees)
    - roll: rotation around Z-axis (in degrees)

    Returns:
    - Rotated point [x, y, z]
    """
    # Convert angles from degrees to radians
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)
    roll_rad = math.radians(roll)

    # Translate point to origin (relative to center)
    x = point[0] - center[0]
    y = point[1] - center[1]
    z = point[2] - center[2]

    # Pitch rotation (around X-axis)
    rotated_y = y * math.cos(pitch_rad) - z * math.sin(pitch_rad)
    rotated_z = y * math.sin(pitch_rad) + z * math.cos(pitch_rad)
    y, z = rotated_y, rotated_z

    # Roll rotation (around Z-axis)
    rotated_x = x * math.cos(roll_rad) - y * math.sin(roll_rad)
    rotated_y = x * math.sin(roll_rad) + y * math.cos(roll_rad)
    x, y = rotated_x, rotated_y

    # Yaw rotation (around Y-axis)
    rotated_x = x * math.cos(yaw_rad) - z * math.sin(yaw_rad)
    rotated_z = x * math.sin(yaw_rad) + z * math.cos(yaw_rad)
    x, z = rotated_x, rotated_z

    # Translate back
    return [x + center[0], y + center[1], z + center[2]]


class Position:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def is_zero(self):
        return self.x == 0 and self.y == 0 and self.z == 0

    def __str__(self):
        return f"Position({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


class Quaternion:
    w: float
    x: float
    y: float
    z: float

    def __init__(self, w: float, x: float, y: float, z: float):
        self.w = w
        self.x = y
        self.y = x
        self.z = z

    def euler(self):  # Convert to pitch, yaw, roll
        """
        var yaw = atan2(2.0*(q.y*q.z + q.w*q.x), q.w*q.w - q.x*q.x - q.y*q.y + q.z*q.z);
        var pitch = asin(-2.0*(q.x*q.z - q.w*q.y));
        var roll = atan2(2.0*(q.x*q.y + q.w*q.z), q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z);
        """
        yaw = math.atan2(
            2.0 * (self.y * self.z + self.w * self.x),
            self.w * self.w - self.x * self.x - self.y * self.y + self.z * self.z,
        )
        pitch = math.asin(-2.0 * (self.x * self.z - self.w * self.y))
        roll = math.atan2(
            2.0 * (self.x * self.y + self.w * self.z),
            self.w * self.w + self.x * self.x - self.y * self.y - self.z * self.z,
        )

        yaw = math.degrees(yaw)
        pitch = math.degrees(pitch)
        roll = math.degrees(roll)

        return pitch, yaw, roll

    def is_zero(self):
        return self.w == 0 and self.x == 0 and self.y == 0 and self.z == 0

    def __str__(self):
        x, y, z = self.euler()
        return f"Quaternion({self.w:.2f}, {self.x:.2f}, {self.y:.2f}, {self.z:.2f}) -> (pitch {x:.2f}, yaw {y:.2f}, roll {z:.2f})"

    def __dict__(self):  # type: ignore
        euler = self.euler()
        return {
            "w": self.w,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pitch": euler[0],
            "yaw": euler[1],
            "roll": euler[2],
        }


class Size:
    width: float
    height: float
    length: float

    def __init__(self, width: float, height: float, length: float):
        self.width = width
        self.height = height
        self.length = length

    def __str__(self):
        return f"Size({self.width:.2f}, {self.height:.2f}, {self.length:.2f})"


class Trailer:
    position: Position
    rotation: Quaternion
    size: Size

    def __init__(self, position: Position, rotation: Quaternion, size: Size):
        self.position = position
        self.rotation = rotation
        self.size = size

    def is_zero(self):
        return self.position.is_zero() and self.rotation.is_zero()

    def __str__(self):
        return f"Trailer({self.position}, {self.rotation}, {self.size})"

    def __dict__(self):  # type: ignore
        return {
            "position": self.position.__dict__,
            "rotation": self.rotation.__dict__(),
            "size": self.size.__dict__,
        }


class Vehicle:
    position: Position
    rotation: Quaternion
    size: Size
    speed: float
    acceleration: float
    trailer_count: int
    id: int
    trailers: list[Trailer]

    is_tmp: bool
    is_trailer: bool
    time: float = 0.0
    speed_position: Position = Position(0, 0, 0)

    def __init__(
        self,
        position: Position,
        rotation: Quaternion,
        size: Size,
        speed: float,
        acceleration: float,
        trailer_count: int,
        trailers: list[Trailer],
        id: int,
        is_tmp: bool,
        is_trailer: bool,
    ):
        self.position = position
        self.rotation = rotation
        self.size = size
        self.speed = speed
        self.acceleration = acceleration
        self.trailer_count = trailer_count
        self.trailers = trailers
        self.id = id
        self.is_tmp = is_tmp
        self.is_trailer = is_trailer

        self.time = time.time()

    def update_from_last(self, vehicle):
        if not self.is_tmp:
            return

        time_diff = time.time() - vehicle.time
        if time_diff < tmp_speed_update_frequency:
            self.time = vehicle.time
            self.speed = vehicle.speed
            self.speed_position = vehicle.speed_position
            return

        last_position = vehicle.speed_position
        distance = math.sqrt(
            (self.position.x - last_position.x) ** 2
            + (self.position.y - last_position.y) ** 2
            + (self.position.z - last_position.z) ** 2
        )

        if distance > 0.1:
            self.speed = distance / time_diff
        else:
            self.speed = 0

        self.speed_position = Position(
            self.position.x, self.position.y, self.position.z
        )

    def is_zero(self):
        return self.position.is_zero() and self.rotation.is_zero()

    def __str__(self):
        return f"Vehicle({self.position}, {self.rotation}, {self.size}, {self.speed:.2f}, {self.acceleration:.2f}, {self.trailer_count}, {self.trailers})"

    def get_corners(self):
        """
        This function will output the corners of the vehicle in the following order:
        1. Front left
        2. Front right
        3. Back right
        4. Back left
        """
        ground_middle = [self.position.x, self.position.y, self.position.z]

        # Back left
        back_left = [
            ground_middle[0] - self.size.width / 2,
            ground_middle[1],
            ground_middle[2] + self.size.length / 2,
        ]

        # Back right
        back_right = [
            ground_middle[0] + self.size.width / 2,
            ground_middle[1],
            ground_middle[2] + self.size.length / 2,
        ]

        # Front right
        front_right = [
            ground_middle[0] + self.size.width / 2,
            ground_middle[1],
            ground_middle[2] - self.size.length / 2,
        ]

        # Front left
        front_left = [
            ground_middle[0] - self.size.width / 2,
            ground_middle[1],
            ground_middle[2] - self.size.length / 2,
        ]

        # Rotate the corners
        pitch, yaw, roll = self.rotation.euler()
        front_left = rotate_around_point(front_left, ground_middle, pitch, -yaw, 0)
        front_right = rotate_around_point(front_right, ground_middle, pitch, -yaw, 0)
        back_right = rotate_around_point(back_right, ground_middle, pitch, -yaw, 0)
        back_left = rotate_around_point(back_left, ground_middle, pitch, -yaw, 0)

        return front_left, front_right, back_right, back_left

    def __dict__(self):  # type: ignore
        return {
            "position": self.position.__dict__,
            "rotation": self.rotation.__dict__(),
            "size": self.size.__dict__,
            "speed": self.speed,
            "acceleration": self.acceleration,
            "trailer_count": self.trailer_count,
            "trailers": [trailer.__dict__() for trailer in self.trailers],
            "id": self.id,
            "is_tmp": self.is_tmp,
            "is_trailer": self.is_trailer,
        }
