import numpy as np

# Function to calculate the perpendicular vector
def perpendicular_vector(v):
    return np.array([-v[1], v[0]])

# Function to normalize a vector
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

# Function to calculate lane boundaries
def calculate_lanes(points, lane_width, num_left_lanes, num_right_lanes, custom_offset=999):
    lanes = {'left': [[] for _ in range(num_left_lanes)], 
             'right': [[] for _ in range(num_right_lanes)]}
    
    for i in range(len(points) - 1):
        point1 = np.array(points[i])
        point2 = np.array(points[i + 1])
        
        # Calculate the direction vector
        direction_vector = point2 - point1
        
        # Normalize the direction vector
        direction_vector = normalize(direction_vector)
        
        # Calculate the perpendicular vector
        perp_vector = perpendicular_vector(direction_vector)
        
        # Adjust the middle point if there are no lanes on one side
        if num_left_lanes == 0:
            # Middle point is the edge of the right lanes
            middle_offset = -perp_vector * lane_width * num_right_lanes / 2
            if num_right_lanes % 2 == 0:
                middle_offset -= perp_vector * lane_width / 2
            point1 -= middle_offset
            point2 -= middle_offset
        elif num_right_lanes == 0:
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

    return lanes