"""
Configuration management for FLACCID.
"""

import os

class Config:
    def __init__(self):
        self._loaded = True

    def get(self, key: str, default=None):
        """Retrieve a configuration value."""
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Retrieve a boolean configuration value."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes')

    def get_int(self, key: str, default: int = 0) -> int:
        """Retrieve an integer configuration value."""
        try:
            return int(os.getenv(key, default))
        except ValueError:
            return default
