"""Metadata helpers for Discogs."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from flaccid.plugins import DiscogsPlugin
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata


def fetch_metadata(file: Path) -> Dict[str, Any]:
    """Return search results for *file* using :class:`DiscogsPlugin`."""

    existing = get_existing_metadata(str(file))
    query = build_search_query(existing)

    async def _search() -> Dict[str, Any]:
        async with DiscogsPlugin() as api:
            return await api.search_track(query)

    return asyncio.run(_search())
