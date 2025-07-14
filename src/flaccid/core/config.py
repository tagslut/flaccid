from __future__ import annotations

"""Dynaconf-based configuration loader."""

from pathlib import Path
from typing import Optional

from dynaconf import Dynaconf
from pydantic import BaseModel


class QobuzSettings(BaseModel):
    """Qobuz related configuration values."""

    app_id: str = ""
    token: str = ""


class AppleSettings(BaseModel):
    """Apple Music related configuration values."""

    developer_token: str = ""
    store: str = "us"


class Settings(BaseModel):
    """Application settings model."""

    qobuz: QobuzSettings = QobuzSettings()
    apple: AppleSettings = AppleSettings()
    discogs_token: str = ""
    beatport_token: str = ""
    tidal_token: str = ""


def _load_dynaconf(settings_file: Optional[Path] = None) -> Dynaconf:
    files = (
        [str(settings_file)]
        if settings_file
        else [
            "settings.toml",
            ".secrets.toml",
            ".env",
        ]
    )
    return Dynaconf(
        envvar_prefix=False,
        settings_files=files,
        load_dotenv=True,
        environments=True,
        env="default",
    )


def load_settings(settings_file: Optional[Path] = None) -> Settings:
    """Load and validate settings from files and environment."""

    raw = _load_dynaconf(settings_file)
    data = {
        "qobuz": {
            "app_id": raw.get("QOBUZ_APP_ID", ""),
            "token": raw.get("QOBUZ_TOKEN", ""),
        },
        "apple": {
            "developer_token": raw.get("APPLE_TOKEN", ""),
            "store": raw.get("APPLE_STORE", "us"),
        },
        "discogs_token": raw.get("DISCOGS_TOKEN", ""),
        "beatport_token": raw.get("BEATPORT_TOKEN", ""),
        "tidal_token": raw.get("TIDAL_TOKEN", ""),
    }
    return Settings.model_validate(data)
