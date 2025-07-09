"""
Common FLAC metadata operations.
"""

import os


def normalize_artist(artist_name: str) -> str:
    """Normalize artist name for consistent metadata."""
    return artist_name.strip().lower()


def validate_flac_file(file_path: str) -> bool:
    """Validate if the given file is a valid FLAC file."""
    return os.path.isfile(file_path) and file_path.endswith(".flac")


def build_search_query(metadata: dict) -> str:
    """Build a search query from metadata."""
    artist = metadata.get("artist", "").strip()
    title = metadata.get("title", "").strip()
    return f"{artist} {title}".strip()


def get_existing_metadata(file_path: str) -> dict:
    """Retrieve existing metadata from a FLAC file."""
    if not os.path.isfile(file_path):
        return {}
    # Placeholder implementation for actual metadata extraction
    return {"artist": "Unknown Artist", "title": "Unknown Title"}


def extract_isrc_from_flac(file_path: str) -> str:
    """Extract the ISRC (International Standard Recording Code) from a FLAC file."""
    # Placeholder implementation
    return "UNKNOWN-ISRC"
