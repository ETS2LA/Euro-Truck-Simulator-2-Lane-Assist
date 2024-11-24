import os
import json
import logging

logger = logging.getLogger('Map')

# DLC mapping for better error messages and validation
DLC_MAPPING = {
    -1: 'base',
    0: 'base',
    1: 'scandinavia',
    2: 'italia',
    3: 'baltic',
    4: 'black_sea',
    5: 'iberia'
}

def check_dlc_access(dlc_guard):
    """
    Check if the DLC is accessible based on the dlc_guard value.
    Base game (dlc_guard <= 0) is always accessible.
    Other DLCs require explicit enabling in settings.
    """
    try:
        # Convert dlc_guard to int if it's a string
        if isinstance(dlc_guard, str):
            dlc_guard = int(dlc_guard)
        elif dlc_guard is None or dlc_guard <= 0:
            return True  # Base game is always accessible

        # Get DLC name for better logging
        dlc_name = DLC_MAPPING.get(dlc_guard, f"unknown_{dlc_guard}")

        # Load user settings
        settings_path = os.path.expanduser('~/Documents/ETS2LA/global_settings.json')
        if not os.path.exists(settings_path):
            # Create default settings if file doesn't exist
            default_settings = {
                'enabled_dlcs': [],  # Empty list means only base game
                'dlc_options': {name: False for name in DLC_MAPPING.values() if name != 'base'}
            }
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, 'w') as f:
                json.dump(default_settings, f, indent=4)
            logging.info("Created default settings file with base game enabled")
            return False  # Only base game accessible

        with open(settings_path, 'r') as f:
            settings = json.load(f)
            enabled_dlcs = settings.get('enabled_dlcs', [])

            # Update settings format if needed
            if 'dlc_options' not in settings:
                settings['dlc_options'] = {
                    name: (dlc_id in enabled_dlcs)
                    for dlc_id, name in DLC_MAPPING.items()
                    if name != 'base'
                }
                with open(settings_path, 'w') as f:
                    json.dump(settings, f, indent=4)

            is_accessible = dlc_guard in enabled_dlcs
            if not is_accessible:
                logging.debug(f"DLC {dlc_name} (guard: {dlc_guard}) not enabled in settings")
            return is_accessible

    except (ValueError, TypeError, json.JSONDecodeError) as e:
        logging.warning(f"Error checking DLC access for {dlc_guard}: {e}, defaulting to base game only")
        return dlc_guard <= 0
    except Exception as e:
        logging.error(f"Unexpected error checking DLC access for {dlc_guard}: {e}")
        return dlc_guard <= 0
