from __future__ import annotations

"""Dynaconf-based configuration loader."""

from pathlib import Path
from typing import Iterable, Optional

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


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
    plugin_precedence: list[str] = Field(
        default_factory=list,
        description="Ordered list of metadata provider plugin names.",
    )


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
        "plugin_precedence": [
            p.strip()
            for p in str(raw.get("PLUGIN_PRECEDENCE", "")).split(",")
            if p.strip()
        ],
    }
    return Settings.model_validate(data)


def get_precedence_order(
    names: Iterable[str] | None = None,
    *,
    settings: Settings | None = None,
) -> list[str]:
    """Return ``names`` ordered by plugin precedence.

    Parameters
    ----------
    names:
        Iterable of provider names to sort. If ``None`` the configured
        precedence list is returned.
    settings:
        Optional :class:`Settings` instance. When omitted, settings are
        loaded from the default locations via :func:`load_settings`.

    Returns
    -------
    list[str]
        Provider names ordered according to configured precedence. Any
        names not present in the precedence list are appended in their
        original order.
    """

    settings = settings or load_settings()
    if names is None:
        return list(settings.plugin_precedence)

    ordered: list[str] = []
    remaining = list(names)
    lower_names = {n.lower(): n for n in names}

    for pref in settings.plugin_precedence:
        pref_lower = pref.lower()
        if pref_lower in lower_names:
            ordered.append(lower_names[pref_lower])
            remaining.remove(lower_names[pref_lower])

    ordered.extend(remaining)
    return ordered
