"""
Re-exports the shared modules from the canonical `flaccid` package.
"""

from __future__ import annotations

from flaccid.shared.apple_api import AppleAPI
from flaccid.shared.config import Config
from flaccid.shared.metadata_utils import (
    build_search_query,
    get_existing_metadata,
    validate_flac_file,
)
from flaccid.shared.qobuz_api import QobuzAPI

__all__ = [
    "AppleAPI",
    "Config",
    "QobuzAPI",
    "build_search_query",
    "get_existing_metadata",
    "validate_flac_file",
]
