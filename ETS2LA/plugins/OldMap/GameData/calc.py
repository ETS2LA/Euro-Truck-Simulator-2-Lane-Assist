import numpy as np
import math

# MARK: Vector
# Function to calculate the perpendicular vector
def perpendicular_vector(v):
    return np.array([-v[1], v[0]])

# Function to normalize a vector
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def lerp(a, b, t):
    return a + t * (b - a)

def distance_between(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

# Function to calculate lane boundaries
# MARK: Lanes
def calculate_lanes(points, lane_width, num_left_lanes, num_right_lanes, road, custom_offset=999, next_offset=999, side=0):
    lanes = {'left': [[] for _ in range(num_left_lanes)], 
             'right': [[] for _ in range(num_right_lanes)]}
    
    #print(custom_offset)
    base_custom_offset = custom_offset
    # points = points[::-1] # This will fix some roads being the other way around (mainly 2 left 1 right with a wide gap)
    pointCount = len(points)
    for i in range(pointCount - 1):
        point1 = np.array(points[i])
        point2 = np.array(points[i + 1])
        if next_offset != base_custom_offset and next_offset != 999 and base_custom_offset != 999:
            if side == 0:
                custom_offset = lerp(base_custom_offset, next_offset, i / (pointCount - 1))
            elif side == 1:
                custom_offset = lerp(base_custom_offset, next_offset, 1 - i / (pointCount - 1))
        
        # Calculate the direction vector
        direction_vector = point2 - point1
        
        # Normalize the direction vector
        direction_vector = normalize(direction_vector)
        
        # Calculate the perpendicular vector
        perp_vector = perpendicular_vector(direction_vector)
        
        # Adjust the middle point if there are no lanes on one side
        if num_left_lanes == 0:
            custom_offset = 999
            # Middle point is the edge of the right lanes
            middle_offset = -perp_vector * lane_width * num_right_lanes / 2
            if num_right_lanes % 2 == 0:
                middle_offset -= perp_vector * lane_width / 2
            point1 -= middle_offset
            point2 -= middle_offset
        elif num_right_lanes == 0:
            custom_offset = 999
            # Middle point is the edge of the left lanes
            middle_offset = perp_vector * lane_width * num_left_lanes / 2
            if num_right_lanes % 2 == 0:
                middle_offset += perp_vector * lane_width / 2
            point1 += middle_offset
            point2 += middle_offset
        
        # Offset to keep the lanes centered
        elif num_left_lanes > num_right_lanes:
            middle_offset = perp_vector * lane_width * (num_left_lanes + 1 - num_right_lanes) / 2
            point1 -= middle_offset
            point2 -= middle_offset
        elif num_right_lanes > num_left_lanes:
            middle_offset = -perp_vector * lane_width * (num_right_lanes + 1 - num_left_lanes) / 2
            point1 -= middle_offset
            point2 -= middle_offset
            
        
        # Calculate the lane points for each lane on the left side
        for lane in range(num_left_lanes):
            if custom_offset == 999 or (num_left_lanes == 1 and num_right_lanes == 0):
                offset = perp_vector * (lane_width * (lane + 1))
            else:
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)
            
            left_point1 = point1 + offset
            left_point2 = point2 + offset
            lanes['left'][lane].append(left_point1.tolist())
            if i == len(points) - 2:
                lanes['left'][lane].append(left_point2.tolist())
        
        # Calculate the lane points for each lane on the right side
        for lane in range(num_right_lanes):
            if custom_offset == 999 or (num_left_lanes == 0 and num_right_lanes == 1):
                offset = perp_vector * (lane_width * (lane + 1))
            else:
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)
            right_point1 = point1 - offset
            right_point2 = point2 - offset
            lanes['right'][lane].append(right_point1.tolist())
            if i == len(points) - 2:
                lanes['right'][lane].append(right_point2.tolist())

    # Add the Y values from the road. This will help with visualizing the lanes later on
    for lane in range(num_left_lanes):
        for i in range(len(lanes['left'][lane])):
            lanes['left'][lane][i].append(road.YValues[i])
    for lane in range(num_right_lanes):
        for i in range(len(lanes['right'][lane])):
            lanes['right'][lane][i].append(road.YValues[i])

    return lanes

# MARK: Points
def RotatePoint(x, z, angle, rotX, rotZ):
    s = math.sin(angle)
    c = math.cos(angle)
    newX = x - rotX
    newZ = z - rotZ
    return (((newX * c) - (newZ * s) + rotX), ((newX * s) + (newZ * c) + rotZ))

def RotatePoint3D(x, y, z, angleX, angleY, angleZ, rotX, rotY, rotZ):
    # Rotation around X-axis
    cosX = math.cos(angleX)
    sinX = math.sin(angleX)
    y_rotated_x = y * cosX - z * sinX
    z_rotated_x = y * sinX + z * cosX

    # Rotation around Y-axis
    cosY = math.cos(angleY)
    sinY = math.sin(angleY)
    x_rotated_y = x * cosY + z_rotated_x * sinY
    z_rotated_y = -x * sinY + z_rotated_x * cosY

    # Rotation around Z-axis
    cosZ = math.cos(angleZ)
    sinZ = math.sin(angleZ)
    x_rotated_z = x_rotated_y * cosZ - y_rotated_x * sinZ
    y_rotated_z = x_rotated_y * sinZ + y_rotated_x * cosZ

    # Translate back
    newX = x_rotated_z + rotX
    newY = y_rotated_z + rotY
    newZ = z_rotated_y + rotZ

    return newX, newY, newZ

def Hermite(s, x, z, tanX, tanZ):
    h1 = 2 * math.pow(s, 3) - 3 * math.pow(s, 2) + 1
    h2 = -2 * math.pow(s, 3) + 3 * math.pow(s, 2)
    h3 = math.pow(s, 3) - 2 * math.pow(s, 2) + s
    h4 = math.pow(s, 3) - math.pow(s, 2)
    return h1 * x + h2 * z + h3 * tanX + h4 * tanZ