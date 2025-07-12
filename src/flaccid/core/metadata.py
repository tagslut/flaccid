from __future__ import annotations

"""Metadata tagging utilities."""

from dataclasses import fields
from pathlib import Path
from typing import Optional, TypeVar

from mutagen.flac import FLAC, Picture

from flaccid.plugins.base import AlbumMetadata, TrackMetadata

T = TypeVar("T", TrackMetadata, AlbumMetadata)


def cascade(*sources: T) -> T:
    """Merge multiple metadata objects.

    Parameters
    ----------
    *sources:
        :class:`TrackMetadata` or :class:`AlbumMetadata` instances ordered by
        precedence. Earlier objects take priority for non-empty values.

    Returns
    -------
    T
        A new metadata object containing the first non-empty value for each
        field.
    """

    if not sources:
        raise ValueError("at least one source required")

    cls = type(sources[0])
    if not all(isinstance(src, cls) for src in sources):
        raise TypeError("all sources must be of the same metadata type")

    data = {}
    for f in fields(cls):
        value = None
        for src in sources:
            candidate = getattr(src, f.name)
            if candidate is not None and candidate != "":
                value = candidate
                break
        data[f.name] = value

    return cls(**data)  # type: ignore[arg-type]


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
        pic.mime = "image/jpeg"
        pic.data = art
        audio.add_picture(pic)

    audio.save()


async def fetch_and_tag(
    path: Path,
    metadata: TrackMetadata,
    *extra: TrackMetadata,
    lyrics_plugin: Optional[object] = None,
    art_data: bytes | None = None,
) -> None:
    """Fetch lyrics using *lyrics_plugin* and write tags."""

    merged = cascade(metadata, *extra)
    # propagate merged values back to the first source for callers relying on
    # in-place updates
    for f in fields(type(metadata)):
        setattr(metadata, f.name, getattr(merged, f.name))

    if lyrics_plugin and not merged.lyrics:
        get_lyrics = getattr(lyrics_plugin, "get_lyrics", None)
        if callable(get_lyrics):
            merged.lyrics = await get_lyrics(merged)
            metadata.lyrics = merged.lyrics
    write_tags(path, merged, art=art_data)
