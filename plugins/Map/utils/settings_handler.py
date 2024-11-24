"""Settings handler for robust error handling of missing or invalid settings."""
import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

from .default_settings import DEFAULT_SETTINGS, load_settings

logger = logging.getLogger('Map')

class SettingsError(Exception):
    """Base exception for settings-related errors."""
    pass

class SettingsHandler:
    """Handles settings access with proper error handling."""

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        """
        Safely get a setting value with fallback to default.

        Args:
            key: The setting key to retrieve
            default: Default value if setting is not found

        Returns:
            The setting value or default
        """
        try:
            settings = load_settings()
            return settings.get(key, default)
        except Exception as e:
            logging.warning(f"Failed to get setting {key}, using default. Error: {e}")
            return default

    @staticmethod
    def set_setting(key: str, value: Any) -> bool:
        """
        Safely set a setting value.

        Args:
            key: The setting key to set
            value: The value to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings = load_settings()
            settings[key] = value

            settings_path = Path(os.path.expanduser("~/Documents/ETS2LA/global_settings.json"))
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Failed to set setting {key}. Error: {e}")
            return False

    @staticmethod
    def get_dlc_setting(dlc_id: str) -> bool:
        """
        Get DLC enabled status with proper error handling.

        Args:
            dlc_id: The DLC ID to check

        Returns:
            bool: True if DLC is enabled, False otherwise
        """
        try:
            settings = load_settings()
            enabled_dlcs = settings.get('enabled_dlcs', [])
            return str(dlc_id) in [str(x) for x in enabled_dlcs]
        except Exception as e:
            logging.error(f"Failed to check DLC {dlc_id} status. Error: {e}")
            return False  # Default to disabled on error

    @staticmethod
    def validate_settings() -> Dict[str, bool]:
        """
        Validate all settings and return status report.

        Returns:
            Dict with validation results for each setting type
        """
        results = {
            'settings_file_exists': False,
            'valid_json': False,
            'required_fields_present': False
        }

        try:
            settings_path = Path(os.path.expanduser("~/Documents/ETS2LA/global_settings.json"))
            results['settings_file_exists'] = settings_path.exists()

            if results['settings_file_exists']:
                with open(settings_path) as f:
                    settings = json.load(f)
                results['valid_json'] = True

                required_fields = ['enabled_dlcs']
                results['required_fields_present'] = all(
                    field in settings for field in required_fields
                )

        except json.JSONDecodeError:
            logging.error("Settings file contains invalid JSON")
        except Exception as e:
            logging.error(f"Error validating settings: {e}")

        return results
