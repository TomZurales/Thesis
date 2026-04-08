"""
Configuration manager for the 2D testbed application.
Demonstrates how the refactored modular structure enables easy extension.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages application configuration with file persistence.
    Shows how the modular structure makes it easy to add new features.
    """
    
    def __init__(self, config_file: str = "testbed_config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "camera": {
                "start_radius": 200,
                "start_angle": 0,
                "move_speed": 2,
                "rotation_speed": 1
            },
            "display": {
                "window_width": 800,
                "window_height": 600,
                "fps": 60,
                "show_instructions_default": True
            },
            "colors": {
                "background": [255, 255, 255],  # White
                "foreground": [0, 0, 0],        # Black  
                "camera": [255, 0, 0],          # Red
                "obstacle": [0, 0, 0]           # Black
            },
            "input": {
                "enable_mouse_wheel_zoom": False,
                "mouse_sensitivity": 1.0,
                "keyboard_repeat_delay": 100
            }
        }
    
    def load_config(self) -> bool:
        """
        Load configuration from file if it exists.
        
        Returns:
            True if config was loaded successfully, False if using defaults
        """
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
                # Merge with defaults to handle new config options
                self._merge_config(self.config, saved_config)
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def _merge_config(self, default: Dict[str, Any], saved: Dict[str, Any]):
        """Recursively merge saved config with defaults."""
        for key, value in saved.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section name
            key: Key within the section
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section name
            key: Key within the section
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Get all camera configuration values."""
        return self.config.get("camera", {})
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get all display configuration values."""
        return self.config.get("display", {})
    
    def get_color_config(self) -> Dict[str, Any]:
        """Get all color configuration values."""
        return self.config.get("colors", {})
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self._load_default_config()


# Global instance for easy access (singleton pattern)
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        Global ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance