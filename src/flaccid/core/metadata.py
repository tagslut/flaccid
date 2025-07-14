from __future__ import annotations

"""Metadata tagging utilities."""

from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC, Picture

from flaccid.plugins.base import LyricsProviderPlugin, TrackMetadata


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


def write_tags(path: Path, metadata: TrackMetadata, art: bytes | None = None) -> None:
    """Write *metadata* and optional album *art* to the FLAC file at *path*."""

    audio = FLAC(str(path))
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

    audio.save()


async def fetch_and_tag(
    path: Path,
    metadata: TrackMetadata,
    lyrics_plugin: Optional[LyricsProviderPlugin] = None,
    art_data: bytes | None = None,
) -> None:
    """Fetch lyrics using *lyrics_plugin* (if provided) and write tags."""

    if lyrics_plugin and not metadata.lyrics:
        metadata.lyrics = await lyrics_plugin.get_lyrics(
            metadata.artist, metadata.title
        )

    write_tags(path, metadata, art=art_data)
