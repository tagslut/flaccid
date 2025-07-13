"""Async equivalents of :mod:`flaccid.shared` for the legacy :mod:`fla` namespace."""

from __future__ import annotations

from .apple_api import AppleAPI
from .config import Config
from .metadata_utils import (
    build_search_query,
    get_existing_metadata,
    validate_flac_file,
)
from .qobuz_api import QobuzAPI

__all__ = [
    "AppleAPI",
    "Config",
    "QobuzAPI",
    "build_search_query",
    "get_existing_metadata",
    "validate_flac_file",
]
