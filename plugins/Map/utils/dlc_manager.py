import os
import json
import logging
from typing import Dict, List

from .dlc_guard import DLC_MAPPING
from .default_settings import load_settings, get_settings_path, DEFAULT_SETTINGS

logger = logging.getLogger('Map')

class DLCManager:
    """Manages DLC settings for Euro Truck Simulator 2 Lane Assistant."""

    def __init__(self):
        self.settings_path = get_settings_path()
        self._ensure_settings_exist()

    def _ensure_settings_exist(self):
        """Create default settings if they don't exist."""
        if not os.path.exists(self.settings_path):
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            logging.info("Created default settings file with base game enabled")

    def get_available_dlcs(self) -> Dict[str, bool]:
        """Get a dictionary of all available DLCs and their enabled status."""
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                return settings.get('dlc_options', {})
        except Exception as e:
            logging.error(f"Error reading DLC settings: {e}")
            return {name: False for name in DLC_MAPPING.values() if name != 'base'}

    def enable_dlc(self, dlc_name: str) -> bool:
        """Enable a specific DLC."""
        try:
            if dlc_name == 'base':
                return True  # Base game is always enabled

            settings = load_settings()

            # Find DLC ID from name
            dlc_id = None
            for id_, name in DLC_MAPPING.items():
                if name == dlc_name:
                    dlc_id = id_
                    break

            if dlc_id is None:
                logging.error(f"Unknown DLC: {dlc_name}")
                return False

            # Update enabled_dlcs list
            if isinstance(dlc_id, (int, str)):
                dlc_id = str(dlc_id)  # Ensure string format for consistency
                if dlc_id not in settings['enabled_dlcs']:
                    settings['enabled_dlcs'].append(dlc_id)

            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)

            logging.info(f"Enabled DLC: {dlc_name}")
            return True

        except Exception as e:
            logging.error(f"Error enabling DLC {dlc_name}: {e}")
            return False

    def disable_dlc(self, dlc_name: str) -> bool:
        """Disable a specific DLC."""
        try:
            if dlc_name == 'base':
                logging.warning("Cannot disable base game")
                return False

            settings = load_settings()

            # Find DLC ID from name
            dlc_id = None
            for id_, name in DLC_MAPPING.items():
                if name == dlc_name:
                    dlc_id = id_
                    break

            if dlc_id is None:
                logging.error(f"Unknown DLC: {dlc_name}")
                return False

            # Update enabled_dlcs list
            if isinstance(dlc_id, (int, str)):
                dlc_id = str(dlc_id)  # Ensure string format for consistency
                if dlc_id in settings['enabled_dlcs']:
                    settings['enabled_dlcs'].remove(dlc_id)

            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)

            logging.info(f"Disabled DLC: {dlc_name}")
            return True

        except Exception as e:
            logging.error(f"Error disabling DLC {dlc_name}: {e}")
            return False

    def get_enabled_dlcs(self) -> List[str]:
        """Get a list of enabled DLC names."""
        try:
            settings = load_settings()
            enabled_dlcs = ['base']  # Base game is always enabled
            for dlc_id in settings.get('enabled_dlcs', []):
                dlc_name = DLC_MAPPING.get(str(dlc_id))
                if dlc_name and dlc_name != 'base':
                    enabled_dlcs.append(dlc_name)
            return enabled_dlcs
        except Exception as e:
            logging.error(f"Error getting enabled DLCs: {e}")
            return ['base']
