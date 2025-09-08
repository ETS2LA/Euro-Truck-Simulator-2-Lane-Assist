# WARNING:
# This uses old code from the old Map plugin. This means that it isn't typed.
# You should not edit this code unless you know what you are doing.
import re

# TODO: Clean the code and optimize road generation

from Plugins.Map.utils import prefab_helpers
from Plugins.Map.utils import math_helpers
from Plugins.Map import classes as c
import numpy as np
import logging
import math
import cv2
import json

offsets = {}
per_name = {}
rules = {}
rules_filename = "plugins/Map/data/config.json"


def get_rules():
    global offsets, per_name, rules
    try:
        with open(rules_filename, "r") as f:
            data = json.load(f)
            offsets = data["offsets"]["base"]
            per_name = data["offsets"]["per_name"]
            rules = data["offsets"]["rules"]
            logging.info("Successfully loaded road rules from config.json")
    except Exception as e:
        logging.error(f"Error loading road rules: {e}. Using default values.")
        offsets = {}
        per_name = {}
        rules = {}


def perpendicular_vector(v):
    return np.array([-v[1], v[0]])


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def lerp(a, b, t):
    return a + t * (b - a)


def calculate_lanes(
    points,
    lane_width,
    num_left_lanes,
    num_right_lanes,
    road,
    custom_offset=999,
    prev_offset=999,
):
    try:
        # Validate input points
        if not points or len(points) < 2:
            logging.error(
                f"Road {road.uid if hasattr(road, 'uid') else 'unknown'} failed to generate points: insufficient points"
            )
            return {"left": [], "right": []}

        lanes = {
            "left": [[] for _ in range(num_left_lanes)],
            "right": [[] for _ in range(num_right_lanes)],
        }

        base_custom_offset = custom_offset

        pointCount = len(points)
        for i in range(pointCount - 1):
            point1 = points[i].list()
            point1 = np.array([point1[0], point1[2]])
            point2 = points[i + 1].list()
            point2 = np.array([point2[0], point2[2]])

            if (
                base_custom_offset != 999
                and prev_offset != 999
                and prev_offset != base_custom_offset
            ):
                custom_offset = lerp(
                    prev_offset, base_custom_offset, i / (pointCount - 2)
                )

            direction_vector = point2 - point1
            direction_vector = normalize(direction_vector)
            perp_vector = perpendicular_vector(direction_vector)

            if num_left_lanes == 0:  # lanes on only right side
                middle_offset = perp_vector * lane_width * (num_right_lanes + 1) / 2
                if num_right_lanes % 2 == 0:
                    middle_offset -= perp_vector * lane_width / 2
                point1 -= middle_offset
                point2 -= middle_offset

            elif num_right_lanes == 0:  # lanes on only left side
                middle_offset = -perp_vector * lane_width * (num_left_lanes + 1) / 2
                if num_left_lanes % 2 == 0:
                    middle_offset += perp_vector * lane_width / 2
                point1 -= middle_offset
                point2 -= middle_offset

            # elif num_left_lanes > num_right_lanes: # more lanes on left side
            #     #               sideways    * 4.5        * (2              + 1 - 1              ) / 2
            #     middle_offset = perp_vector * lane_width * (num_left_lanes + 1 - num_right_lanes) / 2
            #     point1 -= middle_offset
            #     point2 -= middle_offset
            #
            # elif num_right_lanes > num_left_lanes: # more lanes on right side
            #     middle_offset = -perp_vector * lane_width * (num_right_lanes + 1 - num_left_lanes) / 2
            #     point1 -= middle_offset
            #     point2 -= middle_offset

            for lane in range(num_left_lanes):  # left lanes
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)

                left_point1 = point1 - offset
                left_point2 = point2 - offset
                lanes["left"][lane].append(left_point1.tolist())
                if i == len(points) - 2:
                    lanes["left"][lane].append(left_point2.tolist())

            for lane in range(num_right_lanes):  # right lanes
                offset = perp_vector * (lane_width * (lane) + custom_offset / 2)

                right_point1 = point1 + offset
                right_point2 = point2 + offset
                lanes["right"][lane].append(right_point1.tolist())
                if i == len(points) - 2:
                    lanes["right"][lane].append(right_point2.tolist())

        for lane in range(num_left_lanes):
            for i in range(len(lanes["left"][lane])):
                lanes["left"][lane][i].append(road.points[i].list()[1])
        for lane in range(num_right_lanes):
            for i in range(len(lanes["right"][lane])):
                lanes["right"][lane][i].append(road.points[i].list()[1])

        return lanes
    except Exception as e:
        logging.error(
            f"Error calculating lanes for road {getattr(road, 'uid', 'unknown')}: {e}"
        )
        return {"left": [], "right": []}


def GetOffset(road):
    try:
        name = road.road_look.name
        rule_offset = 999
        for rule in rules:
            rule = rule.replace("**", "")
            if rule in name:
                rule_offset = rules["**" + rule]

        reg = re.search(r"(^|\s|_)([+-]?\d+(\.\d+)?)m(_|\s|$)", road.road_look.name)
        if name in per_name:
            custom_offset = per_name[name]
        elif rule_offset != 999:
            custom_offset = rule_offset
        elif reg:
            custom_offset = 4.5 + float(reg.group(2)) * 2
        elif str(road.road_look.offset) in offsets:
            custom_offset = offsets[str(road.road_look.offset)]
        else:
            roadOffset = road.road_look.offset

            if "narrow" in road.road_look.name:
                custom_offset = roadOffset
                if road.road_look.shoulder_space_left > 0:
                    custom_offset += road.road_look.shoulder_space_left / 2
                if road.road_look.shoulder_space_right > 0:
                    custom_offset += road.road_look.shoulder_space_right / 2
            elif "no offset" in road.road_look.name:
                custom_offset = 4.5
            elif "tmpl" in road.road_look.name:
                custom_offset = 4.5 + roadOffset * 2
            else:
                custom_offset = 4.5 + roadOffset

        return custom_offset
    except Exception as e:
        logging.error(
            f"Error getting offset for road {getattr(road, 'uid', 'unknown')}: {e}"
        )
        return 4.5


def GetRoadLanes(road, data):
    if offsets == {} and per_name == {} and rules == {}:
        get_rules()

    try:
        start_node, end_node = road.get_nodes()
        if not start_node or not end_node:
            logging.error(f"Road {road.uid} failed to initialize nodes")
            return [], c.BoundingBox(0, 0, 0, 0)

        if not hasattr(road, "road_look") or not road.road_look:
            logging.error(f"Road {road.uid} has no road_look")
            return [], c.BoundingBox(0, 0, 0, 0)

        custom_offset = GetOffset(road)

        start_node, end_node = road.get_nodes()
        if not start_node or not end_node:
            logging.error(f"Failed to get nodes for road {road.uid}")
            return [], c.BoundingBox(0, 0, 0, 0)

        prev_road = None
        if hasattr(start_node, "backward_item_uid"):
            try:
                prev_road = data.map.get_item_by_uid(start_node.backward_item_uid)
                if isinstance(prev_road, c.Road):
                    custom_offset_prev = (
                        GetOffset(prev_road) if prev_road else custom_offset
                    )
                else:
                    custom_offset_prev = custom_offset
            except Exception as e:
                logging.debug(f"Could not get previous road offset: {e}")
                custom_offset_prev = custom_offset
        else:
            custom_offset_prev = custom_offset

        try:
            lanes = calculate_lanes(
                road.points,
                4.5,
                len(road.road_look.lanes_left),
                len(road.road_look.lanes_right),
                road,
                custom_offset=custom_offset,
                prev_offset=custom_offset_prev,
            )
        except Exception as e:
            logging.error(f"Error calculating lanes for road {road.uid}: {e}")
            return [], c.BoundingBox(0, 0, 0, 0)

        lanes["left"] = lanes["left"][::-1]
        points = lanes["left"] + lanes["right"]

        bounding_box = [[999999, 999999], [-999999, -999999]]
        for lane in points:
            for point in lane:
                if point[0] < bounding_box[0][0]:
                    bounding_box[0][0] = point[0]
                if point[0] > bounding_box[1][0]:
                    bounding_box[1][0] = point[0]
                if point[1] < bounding_box[0][1]:
                    bounding_box[0][1] = point[1]
                if point[1] > bounding_box[1][1]:
                    bounding_box[1][1] = point[1]

        bounding_box[0][0] -= 5
        bounding_box[0][1] -= 5
        bounding_box[1][0] += 5
        bounding_box[1][1] += 5

        bounding_box = c.BoundingBox(
            bounding_box[0][0],
            bounding_box[0][1],
            bounding_box[1][0],
            bounding_box[1][1],
        )

        lane_objects = []

        for lane in lanes["left"]:
            lane_objects.append(
                c.Lane(
                    [c.Position(point[0], point[2], point[1]) for point in lane], "left"
                )
            )
        for lane in lanes["right"]:
            lane_objects.append(
                c.Lane(
                    [c.Position(point[0], point[2], point[1]) for point in lane],
                    "right",
                )
            )

        return lane_objects, bounding_box

    except Exception as e:
        logging.error(
            f"Error in GetRoadLanes for road {getattr(road, 'uid', 'unknown')}: {e}",
            exc_info=True,
        )
        return [], c.BoundingBox(0, 0, 0, 0)


def display_road_lanes(road) -> None:
    cv2.namedWindow("Road Lanes", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Road Lanes", 1000, 1000)
    img = np.zeros((1000, 1000, 3), np.uint8)

    scaling_factor = 2
    offset_x = 500
    offset_y = 500

    for lane in road.lanes:
        poly_points = np.array(
            [
                [
                    int(((point.x - road.x) * scaling_factor + offset_x)),
                    int(((point.z - road.y) * scaling_factor + offset_y)),
                ]
                for point in lane.points
            ],
            np.int32,
        )
        cv2.polylines(
            img, [poly_points], isClosed=False, color=(255, 255, 255), thickness=1
        )

    cv2.imshow("Road Lanes", img)
    cv2.resizeWindow("Road Lanes", 1000, 1000)
    cv2.waitKey(0)


def get_error_for_road(road, map):
    if road is None:
        return []

    offsets = []

    road.get_nodes(map=map)
    start_node = road.start_node
    end_node = road.end_node

    if start_node and end_node:
        items = [
            start_node.forward_item_uid,
            start_node.backward_item_uid,
            end_node.forward_item_uid,
            end_node.backward_item_uid,
        ]
        items = [item for item in items if item != road.uid]
        items = [map.get_item_by_uid(item) for item in items]
        for item in items:
            if item is not None:
                try:
                    if item.nav_routes:
                        for lane in road.lanes:
                            start_point = lane.points[0]
                            end_point = lane.points[-1]
                            route, distance = prefab_helpers.get_closest_lane(
                                item, start_point.x, start_point.z, return_distance=True
                            )
                            route_end, distance_end = prefab_helpers.get_closest_lane(
                                item, end_point.x, end_point.z, return_distance=True
                            )
                            if distance < distance_end:
                                offsets.append(distance)
                            else:
                                offsets.append(distance_end)
                except Exception:
                    pass

    return offsets


def get_closest_lane(item, x: float, z: float, return_distance: bool = False) -> int:
    closest_point_distance = math.inf
    closest_lane_id = -1
    for lane_id, lane in enumerate(item.lanes):
        for point in lane.points:
            point_tuple = point.tuple()
            point_tuple = (point_tuple[0], point_tuple[2])
            distance = math_helpers.DistanceBetweenPoints((x, z), point_tuple)
            if distance < closest_point_distance:
                closest_point_distance = distance
                closest_lane_id = lane_id

    if return_distance:
        return closest_lane_id, closest_point_distance

    return closest_lane_id
