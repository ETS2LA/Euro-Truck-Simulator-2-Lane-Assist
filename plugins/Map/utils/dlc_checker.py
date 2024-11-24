"""DLC access checker with proper type handling."""
import logging
from typing import Union, Optional

from .settings_handler import SettingsHandler
from .dlc_guard import DLC_MAPPING

logger = logging.getLogger('Map')

class DLCChecker:
    """Handles DLC access checking with proper type conversion."""

    @staticmethod
    def has_access(dlc_id: Union[int, str]) -> bool:
        """
        Check if user has access to a DLC.

        Args:
            dlc_id: DLC identifier (can be int or str)

        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            # Convert to string for consistent comparison
            str_id = str(dlc_id).lower()

            # Base game is always accessible
            if str_id == '0' or str_id == 'base':
                return True

            # Check if DLC is enabled in settings
            return SettingsHandler.get_dlc_setting(str_id)

        except Exception as e:
            logging.error(f"Error checking DLC access for ID {dlc_id}: {e}")
            return False

    @staticmethod
    def get_dlc_name(dlc_id: Union[int, str]) -> Optional[str]:
        """
        Get DLC name from ID with proper type handling.

        Args:
            dlc_id: DLC identifier (can be int or str)

        Returns:
            Optional[str]: DLC name if found, None otherwise
        """
        try:
            str_id = str(dlc_id)
            return DLC_MAPPING.get(str_id)
        except Exception as e:
            logging.error(f"Error getting DLC name for ID {dlc_id}: {e}")
            return None

    @staticmethod
    def validate_dlc_id(dlc_id: Union[int, str]) -> bool:
        """
        Validate if a DLC ID is valid.

        Args:
            dlc_id: DLC identifier to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            str_id = str(dlc_id)
            return str_id in DLC_MAPPING or str_id.lower() == 'base' or str_id == '0'
        except Exception as e:
            logging.error(f"Error validating DLC ID {dlc_id}: {e}")
            return False
