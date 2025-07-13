"""Async configuration utilities for the legacy :mod:`fla` package."""

from __future__ import annotations

import os


class Config:
    """Simple wrapper around environment variables."""

    def __init__(self) -> None:
        # Mirror flaccid.shared.Config behaviour
        self._loaded = True

    def get(self, key: str, default: str | None = None) -> str | None:
        """Return the value for *key* from the environment."""
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Return *key* interpreted as a boolean."""
        value = os.getenv(key, str(default)).lower()
        return value in {"1", "true", "yes"}

    def get_int(self, key: str, default: int = 0) -> int:
        """Return *key* converted to ``int`` if possible."""
        try:
            return int(os.getenv(key, default))
        except ValueError:
            return default
