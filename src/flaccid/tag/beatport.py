"""Metadata helpers for Beatport."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from flaccid.core import metadata
from flaccid.plugins import BeatportPlugin, LyricsPlugin
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata


def fetch_metadata(file: Path) -> Dict[str, Any]:
    """Return search results for *file* using :class:`BeatportPlugin`."""

    existing = get_existing_metadata(str(file))
    query = build_search_query(existing)

    async def _search() -> Dict[str, Any]:
        async with BeatportPlugin() as api:
            return await api.search_track(query)

    return asyncio.run(_search())


def tag_from_id(file: Path, track_id: str) -> None:
    """Fetch metadata for ``track_id`` from Beatport and apply it to ``file``."""

    async def _tag() -> None:
        async with BeatportPlugin() as api, LyricsPlugin() as lyr:
            meta = await api.get_track(track_id)
            await metadata.fetch_and_tag(file, meta, lyrics_plugin=lyr)

    asyncio.run(_tag())
