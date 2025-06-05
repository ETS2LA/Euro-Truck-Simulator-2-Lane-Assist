import logging
import json, time
from Plugins.Map.utils import offset_handler
from Plugins.Map import data
from Plugins.Map.utils import internal_map as im

def update_road_data():
    """
    Update road data by clearing existing road data and marking for update.
    
    Returns:
        bool: True if successful, False otherwise
    """
    data.map.clear_road_data()
    im.road_image = None
    data.data_needs_update = True
    return True

def execute_offset_update():
    """
    Execute offset configuration update.
    
    Returns:
        bool: True if update was successful, False if no update was needed or error occurred
    """
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
    """
    Generate rules configuration based on current settings.
    
    Returns:
        bool: True if rules were generated successfully, False otherwise
    """
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
    """
    Clear all lane offset configurations.
    
    Returns:
        bool: True if offsets were cleared, False if no offsets existed or error occurred
    """
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
    """
    Clear all rules configurations.
    
    Returns:
        bool: True if rules were cleared, False if no rules existed or error occurred
    """
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
    """
    Trigger a data update by resetting the downloaded data flag.
    
    Args:
        plugin_instance: The plugin instance to update settings for
    """
    plugin_instance.settings.downloaded_data = ""
    
def use_auto_offset():
    """
    Toggle the use of auto offset.

    Args:
        plugin_instance: The plugin instance to update settings for
    """
    try:
        data.plugin.state.text = "Updating per_name data..."
        logging.warning("Updating per_name data...")
        clear_lane_offsets()
        execute_offset_update()
        clear_rules()
        update_road_data()
        data.plugin.state.text = "Per_name data updated, generating rules..."
        logging.warning("Per_name data updated, generating rules...")
        time.sleep(1)  # Wait for the data to be updated
        #generate_rules() # NOT FUNCTIONING PROPERLY, DISABLED FOR NOW
        update_road_data()
        data.plugin.state.text = "Per_name data updated, rules generated. You can now use the Map plugin."
        logging.warning("Per_name data updated, rules generated. You can now use the Map plugin.")
        return True
    except Exception as e:
        logging.error(f"Error updating per_name data: {e}", exc_info=True)
        data.plugin.state.text = "Error updating per_name data, please check the logs."
        logging.error("Error updating per_name data, please check the logs.")
        return False