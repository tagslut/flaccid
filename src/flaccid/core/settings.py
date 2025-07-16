#!/usr/bin/env python3
"""
Settings management for the FLACCID CLI.

This module provides functionality for loading and storing configuration settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import keyring
import yaml
from pydantic import BaseModel


class QobuzSettings(BaseModel):
    """Qobuz-specific settings."""

    app_id: str = ""
    token: str = ""


class Settings(BaseModel):
    """Global application settings."""

    library_path: str = ""
    cache_path: str = ""
    qobuz: QobuzSettings = QobuzSettings()


def get_settings_path() -> Path:
    """Get the path to the settings file.

    Returns:
        Path to the settings file
    """
    config_dir = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(config_dir) / "flaccid" / "settings.yaml"


def load_settings() -> Settings:
    """Load settings from the settings file.

    Returns:
        Settings object
    """
    path = get_settings_path()
    if not path.exists():
        return Settings()

    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return Settings.parse_obj(data)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return Settings()


def save_settings(settings: Settings) -> None:
    """Save settings to the settings file.

    Args:
        settings: Settings object
    """
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w") as f:
            yaml.dump(settings.dict(), f)
    except Exception as e:
        print(f"Error saving settings: {e}")


def store_token(service: str, token: str) -> None:
    """Store a service token in the system keyring.

    Args:
        service: Service name (e.g., "qobuz")
        token: Authentication token
    """
    try:
        keyring.set_password(f"flaccid_{service}", "token", token)
    except Exception as e:
        print(f"Error storing token in keyring: {e}")


def get_token(service: str) -> Optional[str]:
    """Get a service token from the system keyring.

    Args:
        service: Service name (e.g., "qobuz")

    Returns:
        Authentication token or None if not found
    """
    try:
        return keyring.get_password(f"flaccid_{service}", "token")
    except Exception as e:
        print(f"Error retrieving token from keyring: {e}")
        return None
