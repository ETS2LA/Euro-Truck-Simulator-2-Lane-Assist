import json
import math
import os
import logging
from Plugins.Map.utils import prefab_helpers, road_helpers
from Plugins.Map import data

# 使用规范化路径处理
CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), 
    '../data/config.json'
))
logging.warning("偏移配置路径: %s", CONFIG_PATH)
def update_offset_config_add():
    logging.warning("更新偏移配置")
    # 在路径计算前添加文件存在检查
    if not os.path.exists(CONFIG_PATH):
        open(CONFIG_PATH, 'w').write(json.dumps({"offsets": {"per_name": {}}}))
    logging.warning("配置文件路径: %s", CONFIG_PATH)
    # 读取现有配置
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    logging.warning("配置内容: %s", config)
    updated = False
    distance_threshold = 0.25  # 距离阈值
    per_name = config['offsets']['per_name']
    updated_list = []
    sorted_distances = []
    # 遍历当前路段所有道路
    for road in data.current_sector_roads:
        start_node = road.start_node
        end_node = road.end_node
        if road.road_look.name in updated_list:
            logging.warning(f"已处理过的道路: {road.road_look.name}")
            continue
        # 新增道路对象有效性检查
        if not (hasattr(road, 'road_look') 
                and hasattr(road.road_look, 'name') 
                and road.road_look.name 
                and isinstance(road.road_look.name, str)):
            logging.warning(f"跳过无效道路对象: {road}")
            continue
        start_node = road.start_node
        end_node = road.end_node
        if start_node and end_node:
            items = [
                start_node.forward_item_uid, start_node.backward_item_uid,
                end_node.forward_item_uid, end_node.backward_item_uid
            ]
            items = [
                item for item in items if item != road.uid
            ]
            items = [
                data.map.get_item_by_uid(item) for item in items
            ]
        
        # 计算最小距离
        min_distance = math.inf
        for item in items:
            try:
                if item and hasattr(item, "nav_routes"):
                    item_distances = []  # 存储当前item所有有效距离
                    # 检查起点和终点到prefab的距离
                    for lane in road.lanes:
                        start_point = lane.points[0]
                        end_point = lane.points[-1]
                        
                        # 改进后的距离计算
                        try:
                            _, start_dist = prefab_helpers.get_closest_lane(item, start_point.x, start_point.z, return_distance=True)
                            _, end_dist = prefab_helpers.get_closest_lane(item, end_point.x, end_point.z, return_distance=True)
                            start_dist = round(start_dist, 2)
                            end_dist = round(end_dist, 2)
                            logging.warning(f"当前道路：{road.road_look.name}, 起点距离: {start_dist}, 终点距离: {end_dist}")
                            # 记录所有有效起点距离
                            item_distances.extend([start_dist, end_dist])
                        except Exception as e:
                            logging.error(f"距离计算错误: {str(e)}")
                            continue
                        # 取当前item所有距离中的最小值
                        if item_distances:
                            # 取当前item所有距离中最小的两个值之和
                            sorted_distances = sorted(item_distances)
                            current_min_sum = sum(sorted_distances[:2])  # 取最小的两个距离之和
                            
                            if current_min_sum < min_distance:
                                min_distance = current_min_sum
                                logging.warning(f"当前prefab {item.uid} 最小距离和: {min_distance} (含{len(item_distances)}个测量点)")

                        # 最终有效性检查
                        if math.isnan(min_distance) or math.isinf(min_distance):
                            logging.warning(f"异常距离值: {min_distance}")
                            continue
            except Exception as e:
                logging.error(f"Error processing item {item.uid if item else 'unknown'}: {str(e)}")
                continue
        
        # 修改距离检查逻辑
        # 修改距离检查逻辑，增加有效范围判断
        if (min_distance != math.inf and 0.5 < min_distance < 50) and all(0.5 < md < 50 for md in sorted_distances[:2]):  # 调整有效距离范围
            logging.warning(f"{road.road_look.name} sorted_distances: {sorted_distances}")
            current_name = road.road_look.name.strip()
            if current_name in updated_list:
                continue
            
            current_offset = road_helpers.GetOffset(road)
            try:
                # 修改基准偏移计算方式
                base_offset = min_distance  # 使用前两个最小距离的平均值 
                required_offset = current_offset + base_offset  # 保持加法但使用新基准
                logging.warning(f"计算偏移: {road.road_look.name} (current_offset:{current_offset} base_offset:{base_offset} required_offset:{required_offset})")
                new_offset = round(required_offset, 2)  # 直接使用计算出的偏移量
                logging.warning(f"新偏移: {new_offset}")
            except (TypeError, ValueError) as e:
                logging.error(f"偏移量计算错误: {current_name} - {str(e)}")
                continue
            if road.road_look.name not in per_name:
                per_name[road.road_look.name] = new_offset
                logging.warning(f"添加偏移: {road.road_look.name} ({required_offset})")
                updated = True
                updated_list.append(road.road_look.name)
            elif road.road_look.name in per_name:
                per_name[road.road_look.name] = new_offset
                logging.warning(f"已存在相同偏移: {road.road_look.name} ({required_offset} vs {per_name[road.road_look.name]})")
                updated = True
                updated_list.append(road.road_look.name)
            elif min_distance <= distance_threshold:
                # 处理小于阈值的情况
                logging.warning(f"距离未达阈值: {road.road_look.name} ({min_distance})")
        else:
            logging.warning(f"无效距离被过滤: {road.road_look.name} ({min_distance})")
            
    # 添加配置验证逻辑
    if updated:
        if not isinstance(config.get('offsets', {}).get('per_name'), dict):
            logging.warning("Invalid config structure, resetting offsets")
            config['offsets']['per_name'] = {}
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        logging.warning("配置已更新")
        return True
    return False

def update_offset_config_sub():
    logging.warning("sub更新偏移配置")
    # 在路径计算前添加文件存在检查
    if not os.path.exists(CONFIG_PATH):
        open(CONFIG_PATH, 'w').write(json.dumps({"offsets": {"per_name": {}}}))
    logging.warning("sub配置文件路径: %s", CONFIG_PATH)
    # 读取现有配置
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    logging.warning("sub配置内容: %s", config)
    updated = False
    distance_threshold = 0.25  # 距离阈值
    per_name = config['offsets']['per_name']
    updated_list = []
    sorted_distances = []
    # 遍历当前路段所有道路
    for road in data.current_sector_roads:
        start_node = road.start_node
        end_node = road.end_node
        if road.road_look.name in updated_list:
            logging.warning(f"sub已处理过的道路: {road.road_look.name}")
            continue
        # 新增道路对象有效性检查
        if not (hasattr(road, 'road_look') 
                and hasattr(road.road_look, 'name') 
                and road.road_look.name 
                and isinstance(road.road_look.name, str)):
            logging.warning(f"sub跳过无效道路对象: {road}")
            continue
        start_node = road.start_node
        end_node = road.end_node
        if start_node and end_node:
            items = [
                start_node.forward_item_uid, start_node.backward_item_uid,
                end_node.forward_item_uid, end_node.backward_item_uid
            ]
            items = [
                item for item in items if item != road.uid
            ]
            items = [
                data.map.get_item_by_uid(item) for item in items
            ]
        
        # 计算最小距离
        min_distance = math.inf
        for item in items:
            try:
                if item and hasattr(item, "nav_routes"):
                    item_distances = []  # 存储当前item所有有效距离
                    # 检查起点和终点到prefab的距离
                    for lane in road.lanes:
                        start_point = lane.points[0]
                        end_point = lane.points[-1]
                        
                        # 改进后的距离计算
                        try:
                            _, start_dist = prefab_helpers.get_closest_lane(item, start_point.x, start_point.z, return_distance=True)
                            _, end_dist = prefab_helpers.get_closest_lane(item, end_point.x, end_point.z, return_distance=True)
                            start_dist = round(start_dist, 2)
                            end_dist = round(end_dist, 2)
                            logging.warning(f"sub当前道路：{road.road_look.name}, 起点距离: {start_dist}, 终点距离: {end_dist}")
                            # 记录所有有效起点距离
                            item_distances.extend([start_dist, end_dist])
                        except Exception as e:
                            logging.error(f"sub距离计算错误: {str(e)}")
                            continue
                        # 取当前item所有距离中的最小值
                        if item_distances:
                            # 取当前item所有距离中最小的两个值之和
                            sorted_distances = sorted(item_distances)
                            current_min_sum = sum(sorted_distances[:2])  # 取最小的两个距离之和
                            
                            if current_min_sum < min_distance:
                                min_distance = current_min_sum
                                logging.warning(f"sub当前prefab {item.uid} 最小距离和: {min_distance} (含{len(item_distances)}个测量点)")

                        # 最终有效性检查
                        if math.isnan(min_distance) or math.isinf(min_distance):
                            logging.warning(f"sub异常距离值: {min_distance}")
                            continue
            except Exception as e:
                logging.error(f"subError processing item {item.uid if item else 'unknown'}: {str(e)}")
                continue
        
        # 修改距离检查逻辑
        if (min_distance != math.inf and distance_threshold < min_distance < 1000) or not (distance_threshold < md < 1000 for md in sorted_distances):  # 添加合理范围限制
            logging.warning(f"{road.road_look.name} sorted_distances: {sorted_distances} {(distance_threshold < md < 1000 for md in sorted_distances)}")
            current_name = road.road_look.name.strip()
            if current_name in updated_list:
                continue
            
            current_offset = road_helpers.GetOffset(road)
            try:
                # 修改base_offset计算方式：使用更精确的基准偏移计算
                base_offset = min_distance  # 使用前两个最小距离的平均值
                required_offset = current_offset - base_offset
                logging.warning(f"sub计算偏移: {road.road_look.name} (current_offset:{current_offset} base_offset:{base_offset} required_offset:{required_offset})")
                new_offset = round(required_offset, 2)  # 直接使用计算出的偏移量
                logging.warning(f"sub新偏移: {new_offset}")
            except (TypeError, ValueError) as e:
                logging.error(f"sub偏移量计算错误: {current_name} - {str(e)}")
                continue
            if road.road_look.name not in per_name:
                per_name[road.road_look.name] = new_offset
                logging.warning(f"sub添加偏移: {road.road_look.name} ({required_offset})")
                updated = True
                updated_list.append(road.road_look.name)
            elif road.road_look.name in per_name:
                per_name[road.road_look.name] = new_offset
                logging.warning(f"sub已存在相同偏移: {road.road_look.name} ({required_offset} vs {per_name[road.road_look.name]})")
                updated = True
                updated_list.append(road.road_look.name)
            elif min_distance <= distance_threshold:
                # 处理小于阈值的情况
                logging.warning(f"sub距离未达阈值: {road.road_look.name} ({min_distance})")
        else:
            logging.warning(f"sub无效距离被过滤: {road.road_look.name} ({min_distance})")
            
    # 添加配置验证逻辑
    if updated:
        if not isinstance(config.get('offsets', {}).get('per_name'), dict):
            logging.warning("Invalid config structure, resetting offsets")
            config['offsets']['per_name'] = {}
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        logging.warning("sub配置已更新")
        return True
    return False


def update_offset_config():
    update_offset_config_sub()
    update_offset_config_add()
    
if __name__ == "__main__":
    try:
        if update_offset_config():
            print("配置已更新")
        else:
            print("无需更新配置")
    except Exception as e:
        print(f"发生错误: {e}")
