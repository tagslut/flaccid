"""Utilities for caching lyrics and generating LRC files."""

from __future__ import annotations

import os
from pathlib import Path

from flaccid.utils.audio import get_file_hash
from flaccid.plugins.base import TrackMetadata

__all__ = [
    "lyrics_cache_dir",
    "get_cached_lyrics",
    "set_cached_lyrics",
    "generate_lrc",
    "lyrics_cache_key",
]


def lyrics_cache_dir() -> Path:
    """Return the path to the persistent lyrics cache directory."""
    root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    cache = root / "flaccid" / "lyrics"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def get_cached_lyrics(key: str) -> str | None:
    """Retrieve lyrics from the persistent cache."""
    path = lyrics_cache_dir() / f"{key}.txt"
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def set_cached_lyrics(key: str, lyrics: str) -> Path:
    """Store ``lyrics`` in the persistent cache and return the path."""
    path = lyrics_cache_dir() / f"{key}.txt"
    path.write_text(lyrics, encoding="utf-8")
    return path


def generate_lrc(lyrics: str, step: float = 5.0) -> str:
    """Return a basic LRC representation of ``lyrics``."""
    lines = [ln.strip() for ln in lyrics.splitlines() if ln.strip()]
    time = 0.0
    output: list[str] = []
    for line in lines:
        minutes = int(time // 60)
        seconds = time % 60
        output.append(f"[{minutes:02d}:{seconds:05.2f}]{line}")
        time += step
    return "\n".join(output)


def lyrics_cache_key(path: Path, meta: TrackMetadata) -> str:
    """Return cache key based on ISRC or file hash."""
    return meta.isrc or get_file_hash(path)
