"""
Configuration management for FLACCID.
"""

import os


class yesConfig:
    def __init__(self):
        self._loaded = True

    def get(self, key: str, default=None):
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = os.getenv(key)
        if value is None:
            return default
        value = value.lower()
        if value in ("true", "1", "yes"):  # Accept common true values
            return True
        if value in ("false", "0", "no"):  # Accept common false values
            return False
        return default

    def get_int(self, key: str, default: int = 0) -> int:
        try:
            value = os.getenv(key)
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            return default
