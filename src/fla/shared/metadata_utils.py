"""Utility helpers for FLAC metadata used in the :mod:`fla` namespace."""

from __future__ import annotations

import os
from typing import Any, Dict


def normalize_artist(artist_name: str) -> str:
    """Return a normalized artist name."""
    return artist_name.strip().lower()


def validate_flac_file(file_path: str) -> bool:
    """Return ``True`` if *file_path* looks like a FLAC file."""
    return os.path.isfile(file_path) and file_path.endswith(".flac")


def build_search_query(metadata: Dict[str, Any]) -> str:
    """Create a search string from partial *metadata*."""
    artist = metadata.get("artist", "").strip()
    title = metadata.get("title", "").strip()
    return f"{artist} {title}".strip()


def get_existing_metadata(file_path: str) -> Dict[str, str]:
    """Return placeholder metadata from *file_path* if it exists."""
    if not os.path.isfile(file_path):
        return {}
    # Real extraction not implemented here
    return {"artist": "Unknown Artist", "title": "Unknown Title"}


def extract_isrc_from_flac(file_path: str) -> str:
    """Extract the ISRC value from a FLAC file if present."""
    # Placeholder that would parse metadata using mutagen
    return "UNKNOWN-ISRC"
