from __future__ import annotations

"""Metadata tagging utilities."""

from dataclasses import asdict, fields
from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC, Picture

from flaccid.plugins.base import (
    LyricsProviderPlugin,
    MetadataProviderPlugin,
    TrackMetadata,
)


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


def cascade(*sources: TrackMetadata) -> TrackMetadata:
    """Merge ``TrackMetadata`` objects, filling missing fields left-to-right."""

    if not sources:
        raise ValueError("at least one metadata object is required")

    merged = TrackMetadata(**asdict(sources[0]))
    for src in sources[1:]:
        for field in fields(TrackMetadata):
            val = getattr(merged, field.name)
            other = getattr(src, field.name)
            if (val is None or val == "") and other not in (None, ""):
                setattr(merged, field.name, other)
    return merged


async def write_tags(
    path: str,
    metadata: TrackMetadata,
    *,
    art: bytes | None = None,
    plugin: MetadataProviderPlugin | None = None,
    lyrics_plugin: LyricsProviderPlugin | None = None,
    filename_template: str | None = None,
) -> str:
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

    if not path.exists():
        raise FileNotFoundError(f"write_tags: File does not exist at {path}")
    print(f"write_tags: File exists at {path}")

    audio = FLAC(str(path))
    if not audio:
        raise ValueError(f"write_tags: Failed to initialize FLAC object for {path}")
    print(f"write_tags: Initialized FLAC object for {path}")

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
        print(f"write_tags: Saved metadata for {path}")
    except Exception as e:
        print(f"write_tags: Failed to save metadata for {path}: {e}")
        raise

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
            print(f"write_tags: Renamed file to {new_path}")
            return new_path
        except Exception as e:
            print(f"write_tags: Failed to rename file {path} to {new_name}: {e}")
            raise

    print(f"write_tags: Returning original path {path}")
    return path


async def fetch_and_tag(
    path: Path,
    base: TrackMetadata,
    *extras: TrackMetadata,
    lyrics_plugin: Optional[LyricsProviderPlugin] = None,
    art_data: bytes | None = None,
    plugin: MetadataProviderPlugin | None = None,
    filename_template: str | None = None,
) -> None:
    """Merge metadata via :func:`cascade` and apply tags."""

    merged = cascade(base, *extras)
    await write_tags(
        path,
        merged,
        art=art_data,
        plugin=plugin,
        lyrics_plugin=lyrics_plugin,
        filename_template=filename_template,
    )
