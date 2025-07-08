"""
Configuration management for FLACCID.

This module handles loading configuration from environment variables and .env files.
"""

import os
from pathlib import Path
from typing import Optional

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except ImportError:
    _HAS_DOTENV = False

class Config:
    """Configuration manager for FLACCID."""

    def __init__(self):
        self._loaded = False
        self._load_config()

    def _load_config(self):
        """Load configuration from .env file and environment variables."""
        if self._loaded:
            return

        # Look for .env file in current directory and parent directories
        current_dir = Path.cwd()
        for path in [current_dir] + list(current_dir.parents):
            env_file = path / ".env"
            if env_file.exists() and _HAS_DOTENV:
                load_dotenv(env_file)
                break

        self._loaded = True

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value from environment."""
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key, str(default))
        return value.lower() in ("true", "1", "yes", "on")

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        try:
            return int(self.get(key, str(default)))
        except (ValueError, TypeError):
            return default

    # Service-specific configuration
    @property
    def qobuz_app_id(self) -> str:
        return self.get("QOBUZ_APP_ID", "your_app_id_here")

    @property
    def qobuz_token(self) -> str:
        return self.get("QOBUZ_TOKEN", "your_auth_token_here")

    @property
    def apple_token(self) -> str:
        return self.get("APPLE_TOKEN", "your_developer_token")

    @property
    def apple_store(self) -> str:
        return self.get("APPLE_STORE", "us")

    @property
    def tidal_token(self) -> str:
        return self.get("TIDAL_TOKEN", "your_tidal_token_here")

    @property
    def spotify_client_id(self) -> str:
        return self.get("SPOTIFY_CLIENT_ID", "your_client_id_here")

    @property
    def spotify_client_secret(self) -> str:
        return self.get("SPOTIFY_CLIENT_SECRET", "your_client_secret_here")

    # General configuration
    @property
    def log_level(self) -> str:
        return self.get("FLACCID_LOG_LEVEL", "INFO")

    @property
    def cache_dir(self) -> Path:
        cache_dir = self.get("FLACCID_CACHE_DIR", "~/.flaccid/cache")
        return Path(cache_dir).expanduser()

    @property
    def config_dir(self) -> Path:
        config_dir = self.get("FLACCID_CONFIG_DIR", "~/.flaccid/config")
        return Path(config_dir).expanduser()

# Global config instance
config = Config()
