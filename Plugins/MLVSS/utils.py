import Modules.BetterScreenCapture.main as ScreenCapture
import variables as MLVSS_variables
import threading
import math


def convert_to_screen_coordinate(x: float, y: float, z: float):
    head_yaw = head_rotation_degrees_x
    head_pitch = head_rotation_degrees_y
    head_roll = head_rotation_degrees_z

    relative_x = x - head_x
    relative_y = y - head_y
    relative_z = z - head_z

    cos_yaw = math.cos(math.radians(-head_yaw))
    sin_yaw = math.sin(math.radians(-head_yaw))
    new_x = relative_x * cos_yaw + relative_z * sin_yaw
    NewZ = relative_z * cos_yaw - relative_x * sin_yaw

    cos_pitch = math.cos(math.radians(-head_pitch))
    sin_pitch = math.sin(math.radians(-head_pitch))
    new_y = relative_y * cos_pitch - NewZ * sin_pitch
    final_z = NewZ * cos_pitch + relative_y * sin_pitch

    cos_roll = math.cos(math.radians(-head_roll))
    sin_roll = math.sin(math.radians(-head_roll))
    final_x = new_x * cos_roll - new_y * sin_roll
    final_y = new_y * cos_roll + new_x * sin_roll

    if final_z >= 0:
        return None, None, None

    fov_rad = math.radians(MLVSS_variables.FOV)
    
    window_distance = ((ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) * (4 / 3) / 2) / math.tan(fov_rad / 2)

    screen_x = (final_x / final_z) * window_distance + (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) / 2
    screen_y = (final_y / final_z) * window_distance + (ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) / 2

    screen_x = (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) - screen_x

    distance = math.sqrt((relative_x ** 2) + (relative_y ** 2) + (relative_z ** 2))

    return screen_x, screen_y, distance


def update_telemetry():
    global truck_rotation_degrees_x
    global truck_rotation_degrees_y
    global truck_rotation_degrees_z
    global truck_rotation_radians_x
    global truck_rotation_radians_y
    global truck_rotation_radians_z
    global truck_rotation_x
    global truck_rotation_y
    global truck_rotation_z
    global truck_x
    global truck_y
    global truck_z
    global head_rotation_degrees_x
    global head_rotation_degrees_y
    global head_rotation_degrees_z
    global head_x
    global head_y
    global head_z
    global wheel_angles
    global wheel_coordinates

    APIDATA = MLVSS_variables.SCS_telemetry.update()


    truck_x = APIDATA["truckPlacement"]["coordinateX"]
    truck_y = APIDATA["truckPlacement"]["coordinateY"]
    truck_z = APIDATA["truckPlacement"]["coordinateZ"]
    truck_rotation_x = APIDATA["truckPlacement"]["rotationX"]
    truck_rotation_y = APIDATA["truckPlacement"]["rotationY"]
    truck_rotation_z = APIDATA["truckPlacement"]["rotationZ"]

    cabin_offset_x = APIDATA["headPlacement"]["cabinOffsetX"] + APIDATA["configVector"]["cabinPositionX"]
    cabin_offset_y = APIDATA["headPlacement"]["cabinOffsetY"] + APIDATA["configVector"]["cabinPositionY"]
    cabin_offset_z = APIDATA["headPlacement"]["cabinOffsetZ"] + APIDATA["configVector"]["cabinPositionZ"]
    cabin_offset_rotation_x = APIDATA["headPlacement"]["cabinOffsetrotationX"]
    cabin_offset_rotation_y = APIDATA["headPlacement"]["cabinOffsetrotationY"]
    cabin_offset_rotation_z = APIDATA["headPlacement"]["cabinOffsetrotationZ"]

    head_offset_x = APIDATA["headPlacement"]["headOffsetX"] + APIDATA["configVector"]["headPositionX"] + cabin_offset_x
    head_offset_y = APIDATA["headPlacement"]["headOffsetY"] + APIDATA["configVector"]["headPositionY"] + cabin_offset_y
    head_offset_z = APIDATA["headPlacement"]["headOffsetZ"] + APIDATA["configVector"]["headPositionZ"] + cabin_offset_z
    head_offset_rotation_x = APIDATA["headPlacement"]["headOffsetrotationX"]
    head_offset_rotation_y = APIDATA["headPlacement"]["headOffsetrotationY"]
    head_offset_rotation_z = APIDATA["headPlacement"]["headOffsetrotationZ"]

    truck_rotation_degrees_x = truck_rotation_x * 360
    truck_rotation_degrees_y = truck_rotation_y * 360
    truck_rotation_degrees_z = truck_rotation_z * 180
    truck_rotation_radians_x = -math.radians(truck_rotation_degrees_x)
    truck_rotation_radians_y = -math.radians(truck_rotation_degrees_y)
    truck_rotation_radians_z = -math.radians(truck_rotation_degrees_z)

    head_rotation_degrees_x = ((truck_rotation_x + cabin_offset_rotation_x + head_offset_rotation_x) * 360) % 360
    head_rotation_degrees_y = ((truck_rotation_y + cabin_offset_rotation_y + head_offset_rotation_y) * 360) % 360
    head_rotation_degrees_z = ((truck_rotation_z + cabin_offset_rotation_z + head_offset_rotation_z) * 180) % 180

    point_x = head_offset_x
    point_y = head_offset_y
    point_z = head_offset_z
    head_x = point_x * math.cos(truck_rotation_radians_x) - point_z * math.sin(truck_rotation_radians_x) + truck_x
    head_y = point_y + truck_y
    head_z = point_x * math.sin(truck_rotation_radians_x) + point_z * math.cos(truck_rotation_radians_x) + truck_z


    truck_wheel_points_x = [Point for Point in APIDATA["configVector"]["truckWheelPositionX"] if Point != 0]
    truck_wheel_points_y = [Point for Point in APIDATA["configVector"]["truckWheelPositionY"] if Point != 0]
    truck_wheel_points_z = [Point for Point in APIDATA["configVector"]["truckWheelPositionZ"] if Point != 0]

    wheel_angles = [Angle for Angle in APIDATA["truckFloat"]["truck_wheelSteering"] if Angle != 0]

    wheel_coordinates = []
    for i in range(len(truck_wheel_points_x)):
        point_x = truck_x + truck_wheel_points_x[i] * math.cos(truck_rotation_radians_x) - truck_wheel_points_z[i] * math.sin(truck_rotation_radians_x)
        point_y = truck_y + truck_wheel_points_y[i]
        point_z = truck_z + truck_wheel_points_z[i] * math.cos(truck_rotation_radians_x) + truck_wheel_points_x[i] * math.sin(truck_rotation_radians_x)
        wheel_coordinates.append((point_x, point_y, point_z))


def launch(plugin):
    def run_thread(plugin):
        while True:
            plugin.run()
    threading.Thread(target=run_thread, args=(plugin,), daemon=True).start()