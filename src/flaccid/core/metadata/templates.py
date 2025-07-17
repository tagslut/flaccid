"""Helpers for naming files and handling metadata JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

__all__ = [
    "load_metadata",
    "save_metadata",
    "sanitize_filename",
    "generate_filename",
]


def load_metadata(file_path: Path) -> Dict[str, Any]:
    """Load metadata from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load metadata: {e}") from e


def save_metadata(metadata: Dict[str, Any], file_path: Path) -> Path:
    """Save metadata to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Failed to save metadata: {e}") from e
    return file_path


def sanitize_filename(filename: str) -> str:
    """Return ``filename`` stripped of invalid characters."""
    sanitized = re.sub(r'[\\/:*?"<>|]', "", filename)
    sanitized = sanitized.strip()
    return re.sub(r"\s+", " ", sanitized)


def generate_filename(metadata: Dict[str, Any]) -> Optional[str]:
    """Generate a filename from ``metadata`` if possible."""
    artist = metadata.get("artist")
    title = metadata.get("title")
    if not artist or not title:
        return None
    return sanitize_filename(f"{artist} - {title}.flac")
