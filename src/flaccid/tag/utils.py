"""Utility helpers for metadata tagging."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

from typer import confirm

from flaccid.core import metadata
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.lyrics import LyricsPlugin


def apply_metadata(file: Path, metadata_file: Path | None, yes: bool) -> None:
    """Apply metadata from *metadata_file* to *file*."""

    if metadata_file is None:
        raise ValueError("metadata_file is required")

    with metadata_file.open("r", encoding="utf-8") as fh:
        data: dict = json.load(fh)

    if not yes and not confirm("Apply metadata?"):
        return

    track_meta = TrackMetadata(
        title=data.get("title", ""),
        artist=data.get("artist", ""),
        album=data.get("album", ""),
        track_number=int(data.get("track_number", 0)),
        disc_number=int(data.get("disc_number", 0)),
        year=data.get("year"),
        isrc=data.get("isrc"),
        lyrics=data.get("lyrics"),
    )

    async def _apply() -> None:
        if not track_meta.lyrics:
            async with LyricsPlugin() as lyr:
                track_meta.lyrics = (
                    await lyr.get_lyrics(track_meta.artist, track_meta.title) or None
                )

        metadata.write_tags(file, track_meta)

    asyncio.run(_apply())
