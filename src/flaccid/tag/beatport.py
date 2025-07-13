"""Metadata helpers for Beatport."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from flaccid.plugins import BeatportPlugin
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata


def fetch_metadata(file: Path) -> Dict[str, Any]:
    """Return search results for *file* using :class:`BeatportPlugin`."""

    existing = get_existing_metadata(str(file))
    query = build_search_query(existing)

    async def _search() -> Dict[str, Any]:
        async with BeatportPlugin() as api:
            return await api.search_track(query)

    return asyncio.run(_search())
