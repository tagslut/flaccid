"""Metadata tagging utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC, Picture

from .audit import (
    generate_lrc,
    get_cached_lyrics,
    lyrics_cache_dir,
    lyrics_cache_key,
    set_cached_lyrics,
)
from .cascade import cascade, cascade_with_provenance, merge_by_precedence
from .templates import generate_filename, load_metadata, sanitize_filename, save_metadata
from .validators import validate_field_retention
from flaccid.plugins.base import (
    LyricsProviderPlugin,
    MetadataProviderPlugin,
    TrackMetadata,
)
import logging

logger = logging.getLogger(__name__)

__all__ = [
    "load_metadata",
    "save_metadata",
    "sanitize_filename",
    "generate_filename",
    "lyrics_cache_dir",
    "get_cached_lyrics",
    "set_cached_lyrics",
    "generate_lrc",
    "lyrics_cache_key",
    "cascade",
    "cascade_with_provenance",
    "merge_by_precedence",
    "validate_field_retention",
    "write_tags",
    "fetch_and_tag",
]


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
    """Write ``metadata`` and optional art to ``path``."""

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
        if art[:3] == b"\xff\xd8\xff":
            pic.mime = "image/jpeg"
        elif art[:8] == b"\x89PNG\r\n\x1a\n":
            pic.mime = "image/png"
        else:
            pic.mime = "image/jpeg"
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
    """Merge metadata via :func:`cascade` and apply tags."""

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
            __import__("json").dumps(provenance, indent=2), encoding="utf-8"
        )
    except Exception as e:  # pragma: no cover - best effort
        logger.warning("Failed to write provenance for %s: %s", new_path, e)
    return new_path
