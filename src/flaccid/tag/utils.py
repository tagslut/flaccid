"""Utility helpers for metadata tagging."""

from __future__ import annotations

import asyncio
from pathlib import Path

from typer import confirm

from flaccid.plugins.registry import get_provider
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata

from flaccid.core import metadata
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.lyrics import LyricsPlugin


DEFAULT_PROVIDER = "qobuz"


def fallback_fetch(path: Path) -> TrackMetadata:
    """Fetch track metadata for ``path`` using the default provider."""

    existing = get_existing_metadata(str(path))
    query = build_search_query(existing)
    plugin_cls = get_provider(DEFAULT_PROVIDER)

    async def _fetch() -> TrackMetadata:
        async with plugin_cls() as api:
            result = await api.search_track(query)
            if isinstance(result, TrackMetadata):
                return result

            track_id: str | None = None
            if isinstance(result, dict):
                if "id" in result:
                    track_id = str(result["id"])
                else:
                    tracks = result.get("tracks") or result.get("items")
                    if isinstance(tracks, list) and tracks:
                        first = tracks[0]
                        track_id = str(first.get("id"))

            if not track_id:
                raise ValueError("No track found")

            return await api.get_track(track_id)

    return asyncio.run(_fetch())


def apply_metadata(file: Path, meta: TrackMetadata, yes: bool) -> None:
    """Apply ``meta`` to ``file``."""

    if not yes and not confirm("Apply metadata?"):
        return

    async def _apply() -> None:
        if not meta.lyrics:
            async with LyricsPlugin() as lyr:
                meta.lyrics = await lyr.get_lyrics(meta.artist, meta.title) or None

        await metadata.write_tags(str(file), meta)

    asyncio.run(_apply())
