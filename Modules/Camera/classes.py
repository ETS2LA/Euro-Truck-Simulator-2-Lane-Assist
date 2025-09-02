import math


class Position:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"Position({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z


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
        """Var yaw = atan2(2.0*(q.y*q.z + q.w*q.x), q.w*q.w - q.x*q.x - q.y*q.y + q.z*q.z);
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

    def __str__(self):
        x, y, z = self.euler()
        return f"Quaternion({self.w:.2f}, {self.x:.2f}, {self.y:.2f}, {self.z:.2f}) -> (pitch {x:.2f}, yaw {y:.2f}, roll {z:.2f})"

    def __eq__(self, other):
        return (
            self.w == other.w
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
        )


class Camera:
    fov: float
    position: Position
    cx: float
    cz: float
    rotation: Quaternion

    def __init__(
        self, fov: float, position: Position, cx: float, cz: float, rotation: Quaternion
    ):
        self.fov = fov
        self.position = position
        self.cx = cx
        self.cz = cz
        self.rotation = rotation

    def __str__(self):
        return f"Camera({self.fov:.2f}, {self.position}, {self.cx}, {self.cz}, {self.rotation})"

    def __eq__(self, other):
        return (
            self.fov == other.fov
            and self.position == other.position
            and self.cx == other.cx
            and self.cz == other.cz
            and self.rotation == other.rotation
        )
