"""Utility helpers for metadata tagging."""

from __future__ import annotations

import asyncio
from pathlib import Path

from typer import confirm

from flaccid.core import metadata
from flaccid.plugins.base import (
    MetadataProviderPlugin,
    LyricsProviderPlugin,
    TrackMetadata,
)
from flaccid.plugins.lyrics import LyricsPlugin
from flaccid.plugins.registry import get_provider
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata


async def write_tags(path: Path, meta: TrackMetadata) -> Path:
    """Wrapper around :func:`flaccid.core.metadata.write_tags`."""
    return await metadata.write_tags(str(path), meta)


def fallback_fetch(path: Path) -> TrackMetadata:
    """Fetch metadata for ``path`` using the default provider."""

    existing = get_existing_metadata(str(path))
    query = build_search_query(existing)

    async def _fetch() -> TrackMetadata:
        plugin_cls = get_provider("qobuz")
        async with plugin_cls() as api:
            result = await api.search_track(query)
            if isinstance(result, TrackMetadata):
                return result
            track_id = None
            if isinstance(result, dict):
                if "id" in result:
                    track_id = result["id"]
                elif result.get("results"):
                    first = result["results"][0]
                    track_id = first.get("id") or first.get("trackId")
            if not track_id:
                raise ValueError("Unable to extract track id from provider response")
            return await api.get_track(str(track_id))

    return asyncio.run(_fetch())


def apply_metadata(file: Path, meta: TrackMetadata, yes: bool) -> None:
    """Apply ``meta`` to ``file``."""

    if not yes and not confirm("Apply metadata?"):
        return

    track_meta = meta

    async def _apply() -> None:
        if not track_meta.lyrics:
            async with LyricsPlugin() as lyr:
                track_meta.lyrics = (
                    await lyr.get_lyrics(track_meta.artist, track_meta.title) or None
                )

        await metadata.write_tags(str(file), track_meta)

    asyncio.run(_apply())


async def write_tags(
    file: Path,
    meta: TrackMetadata,
    *,
    art: bytes | None = None,
    plugin: MetadataProviderPlugin | None = None,
    lyrics_plugin: LyricsProviderPlugin | None = None,
    filename_template: str | None = None,
) -> Path:
    """Proxy to :func:`flaccid.core.metadata.write_tags`."""

    return await metadata.write_tags(
        file,
        meta,
        art=art,
        plugin=plugin,
        lyrics_plugin=lyrics_plugin,
        filename_template=filename_template,
    )
