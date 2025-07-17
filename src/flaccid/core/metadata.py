#!/usr/bin/env python3
"""
Metadata handling utilities for audio files.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import logging

from flaccid.utils.audio import get_file_hash

from mutagen.flac import FLAC, Picture
from flaccid.plugins.base import (
    LyricsProviderPlugin,
    MetadataProviderPlugin,
    TrackMetadata,
)
from flaccid.core.config import Settings, get_precedence_order

logger = logging.getLogger(__name__)
"""Module logger used for metadata operations."""


def load_metadata(file_path: Path) -> Dict[str, Any]:
    """Load metadata from a JSON file.

    Args:
        file_path: Path to the metadata JSON file

    Returns:
        Metadata dictionary
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load metadata: {e}") from e


def save_metadata(metadata: Dict[str, Any], file_path: Path) -> Path:
    """Save metadata to a JSON file.

    Args:
        metadata: Metadata dictionary
        file_path: Path to save the metadata to
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Failed to save metadata: {e}") from e
    return file_path


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing illegal characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove illegal characters
    sanitized = re.sub(r'[\\/:*?"<>|]', "", filename)
    # Trim whitespace
    sanitized = sanitized.strip()
    # Replace multiple spaces with a single space
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized


def generate_filename(metadata: Dict[str, Any]) -> Optional[str]:
    """Generate a filename from metadata.

    Args:
        metadata: Metadata dictionary

    Returns:
        Generated filename or None if required fields are missing
    """
    artist = metadata.get("artist")
    title = metadata.get("title")

    if not artist or not title:
        return None

    return sanitize_filename(f"{artist} - {title}.flac")


def lyrics_cache_dir() -> Path:
    """Return the path to the persistent lyrics cache directory."""

    root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    cache = root / "flaccid" / "lyrics"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def get_cached_lyrics(key: str) -> Optional[str]:
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


def _set_common_tags(audio: FLAC, meta: TrackMetadata) -> None:
    """Apply basic tags from *meta* to *audio*."""

    audio["title"] = meta.title
    audio["artist"] = meta.artist
    audio["album"] = meta.album
    audio["tracknumber"] = str(meta.track_number)
    audio["discnumber"] = str(meta.disc_number)
    if meta.year:
        audio["date"] = str(meta.year)
    if meta.isrc:
        audio["isrc"] = meta.isrc
    if meta.lyrics:
        audio["lyrics"] = meta.lyrics


def cascade(
    *sources: TrackMetadata,
    strategies: dict[str, str] | None = None,
) -> TrackMetadata:
    """Merge metadata objects using optional per-field strategies.

    ``strategies`` maps field names to one of ``"append"``, ``"prefer"``, or
    ``"replace"``. ``prefer`` is the default behaviour.
    """

    if not sources:
        raise ValueError("at least one metadata object is required")

    merged = TrackMetadata(**asdict(sources[0]))
    strategies = strategies or {}
    for src in sources[1:]:
        for field in fields(TrackMetadata):
            val = getattr(merged, field.name)
            other = getattr(src, field.name)
            if other in (None, ""):
                continue

            strategy = strategies.get(field.name, "prefer")

            if strategy == "replace":
                setattr(merged, field.name, other)
            elif strategy == "append":
                if val in (None, ""):
                    setattr(merged, field.name, other)
                elif isinstance(val, str) and isinstance(other, str):
                    setattr(merged, field.name, val + other)
            else:  # prefer
                if val in (None, ""):
                    setattr(merged, field.name, other)
    return merged


def cascade_with_provenance(
    *sources: TrackMetadata,
    strategies: dict[str, str] | None = None,
) -> tuple[TrackMetadata, dict[str, str]]:
    """Merge ``sources`` and record the provider for each field."""

    merged = cascade(*sources, strategies=strategies)
    provenance: dict[str, str] = {}
    strategies = strategies or {}
    for field in fields(TrackMetadata):
        for src in reversed(sources):
            val = getattr(src, field.name)
            if val in (None, ""):
                continue
            provenance[field.name] = src.source or "unknown"
            strategy = strategies.get(field.name, "prefer")
            if strategy == "append" and provenance.get(field.name) != src.source:
                prev = provenance[field.name]
                provenance[field.name] = f"{prev}+{src.source or 'unknown'}"
            break
    return merged, provenance


def merge_by_precedence(
    results: dict[str, TrackMetadata],
    *,
    strategies: dict[str, str] | None = None,
    settings: Settings | None = None,
) -> TrackMetadata:
    """Merge ``results`` respecting configured plugin precedence."""

    order = get_precedence_order(results.keys(), settings=settings)
    ordered = [results[name] for name in order]
    return cascade(*ordered, strategies=strategies)


def validate_field_retention(
    merged: TrackMetadata, sources: Iterable[TrackMetadata]
) -> None:
    """Ensure no populated field from ``sources`` was dropped during merging.

    Parameters
    ----------
    merged:
        The final merged metadata object.
    sources:
        The list of original metadata sources that were merged. If any of these
        contain a non-empty value for a field, ``merged`` must also contain a
        non-empty value for that field.  A :class:`ValueError` is raised if this
        check fails.
    """

    for field in fields(TrackMetadata):
        had_value = any(getattr(src, field.name) not in (None, "") for src in sources)
        if had_value and getattr(merged, field.name) in (None, ""):
            raise ValueError(f"Field {field.name} lost during merge")


async def write_tags(
    path: Path,
    metadata: TrackMetadata,
    *,
    art: bytes | None = None,
    plugin: MetadataProviderPlugin | None = None,
    lyrics_plugin: LyricsProviderPlugin | None = None,
    filename_template: str | None = None,
    export_lrc: bool = False,
) -> Path:
    """Write ``metadata`` and optional art to ``path``.

    Lyrics are cached on success. If ``export_lrc`` is ``True`` and lyrics are
    available, a simple ``.lrc`` file will be written next to the FLAC file.
    """

    if not art and plugin and metadata.art_url:
        try:
            art = await plugin.fetch_cover_art(metadata.art_url)
        except Exception:
            art = None

    if lyrics_plugin and not metadata.lyrics:
        try:
            metadata.lyrics = await lyrics_plugin.get_lyrics(
                metadata.artist,
                metadata.title,
            )
        except Exception:
            metadata.lyrics = None

    if metadata.lyrics:
        set_cached_lyrics(lyrics_cache_key(path, metadata), metadata.lyrics)

    if not path.exists():
        raise FileNotFoundError(f"write_tags: File does not exist at {path}")
    logger.debug("write_tags: File exists at %s", path)

    audio = FLAC(path)
    if not audio:
        raise ValueError(f"write_tags: Failed to initialize FLAC object for {path}")
    logger.debug("write_tags: Initialized FLAC object for %s", path)

    _set_common_tags(audio, metadata)

    if art:
        pic = Picture()
        pic.type = 3  # front cover
        # Try to detect MIME type from image header
        if art[:3] == b"\xff\xd8\xff":
            pic.mime = "image/jpeg"
        elif art[:8] == b"\x89PNG\r\n\x1a\n":
            pic.mime = "image/png"
        else:
            pic.mime = "image/jpeg"  # fallback
        pic.data = art
        audio.add_picture(pic)

    try:
        audio.save()
        logger.info("write_tags: Saved metadata for %s", path)
    except Exception as e:
        logger.error("write_tags: Failed to save metadata for %s: %s", path, e)
        raise

    if export_lrc and metadata.lyrics:
        lrc_path = path.with_suffix(".lrc")
        lrc_path.write_text(generate_lrc(metadata.lyrics), encoding="utf-8")

    if filename_template:
        try:
            new_name = filename_template.format(
                artist=metadata.artist,
                title=metadata.title,
                album=metadata.album,
                track_number=f"{metadata.track_number:02d}",
                disc_number=f"{metadata.disc_number}",
            )
            new_path = path.with_name(new_name)
            path.rename(new_path)
            logger.info("write_tags: Renamed file to %s", new_path)
            return new_path
        except Exception as e:
            logger.error(
                "write_tags: Failed to rename file %s to %s: %s", path, new_name, e
            )
            raise

    logger.debug("write_tags: Returning original path %s", path)
    return path


async def fetch_and_tag(
    path: Path,
    base: TrackMetadata,
    *extras: TrackMetadata,
    strategies: dict[str, str] | None = None,
    lyrics_plugin: Optional[LyricsProviderPlugin] = None,
    art_data: bytes | None = None,
    plugin: MetadataProviderPlugin | None = None,
    filename_template: str | None = None,
    export_lrc: bool = False,
) -> Path:
    """Merge metadata via :func:`cascade` and apply tags.

    Parameters
    ----------
    path:
        Location of the FLAC file to tag.
    base:
        Base metadata object.
    *extras:
        Additional metadata objects whose fields will cascade onto ``base``.
    strategies:
        Optional per-field cascade strategies. Keys correspond to
        :class:`TrackMetadata` fields and values must be ``"append"``,
        ``"prefer"``, or ``"replace"``.
    lyrics_plugin:
        Optional lyrics provider used if ``base`` and ``extras`` lack lyrics.
    art_data:
        Raw image bytes to embed as cover art.
    plugin:
        Provider plugin used to fetch cover art if ``art_data`` is not
        supplied.
    filename_template:
        Template used to rename the file after tagging.
    export_lrc:
        If ``True``, write an accompanying ``.lrc`` file when lyrics are
        available.
    """

    merged, provenance = cascade_with_provenance(base, *extras, strategies=strategies)
    validate_field_retention(merged, [base, *extras])
    new_path = await write_tags(
        path,
        merged,
        art=art_data,
        plugin=plugin,
        lyrics_plugin=lyrics_plugin,
        filename_template=filename_template,
        export_lrc=export_lrc,
    )
    try:
        new_path.with_suffix(".sources.json").write_text(
            json.dumps(provenance, indent=2), encoding="utf-8"
        )
    except Exception as e:  # pragma: no cover - best effort
        logger.warning("Failed to write provenance for %s: %s", new_path, e)
    return new_path
