import logging
import json
from Plugins.Map.utils import offset_handler
from Plugins.Map import data
from Plugins.Map.utils import internal_map as im

def update_road_data():
    """更新道路数据"""
    data.map.clear_road_data()
    im.road_image = None
    data.data_needs_update = True
    return True

def execute_offset_update():
    """执行偏移配置更新"""
    try:
        if offset_handler.update_offset_config():
            logging.info("The offset configuration has been updated, and the data is being reloaded...")
            return True
        else:
            logging.info("No need to update the offset configuration.")
            return False
    except Exception as e:
        logging.error(f"Failed to update the offset configuration: {str(e)}")
        return False

def generate_rules():
    """生成规则配置"""
    try:
        with open(offset_handler.CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        if offset_handler.generate_rules(config):
            logging.info("The rules configuration has been generated, and the data is being reloaded...")
            return True
        else:
            logging.info("No need to generate the rules configuration.")
            return False
    except Exception as e:
        logging.error(f"Failed to generate the rules configuration: {str(e)}")
        return False

def clear_lane_offsets():
    """清除车道偏移"""
    try:
        if offset_handler.clear_lane_offsets(clear=""):
            logging.info("The lane offset has been cleared.")
            return True
        else:
            logging.info("No lane offset to clear.")
            return False
    except Exception as e:
        logging.error(f"Failed to clear the lane offset: {str(e)}")
        return False

def clear_rules():
    """清除规则配置"""
    try:
        if offset_handler.clear_lane_offsets(clear="rules"):
            logging.info("The rules configuration has been cleared.")
            return True
        else:
            logging.info("No rules configuration to clear.")
            return False
    except Exception as e:
        logging.error(f"Failed to clear the rules configuration: {str(e)}")
        return False

def trigger_data_update(plugin_instance):
    """触发数据更新"""
    plugin_instance.settings.downloaded_data = ""