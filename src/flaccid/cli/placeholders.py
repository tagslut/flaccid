from __future__ import annotations

"""Helper functions used by the CLI commands."""

import asyncio
import json
from pathlib import Path

import keyring
from typer import confirm

from flaccid.core.metadata import write_tags
from flaccid.plugins import LyricsPlugin
from flaccid.plugins.base import TrackMetadata
from flaccid.plugins.registry import get_provider
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata


def fetch_metadata(file: Path, provider: str) -> dict:
    """Return metadata for *file* from *provider*.

    Parameters
    ----------
    file:
        FLAC file to inspect for existing metadata to build a search query.
    provider:
        Name of the provider to query (``qobuz``, ``apple``, ``discogs``, or ``beatport``).
    """
    existing = get_existing_metadata(str(file))
    query = build_search_query(existing)

    async def _search() -> dict:
        plugin_cls = get_provider(provider)
        async with plugin_cls() as api:
            return await api.search_track(query)

    return asyncio.run(_search())


def apply_metadata(file: Path, metadata_file: Path | None, yes: bool) -> None:
    """Apply metadata from *metadata_file* to *file*.

    The metadata file should contain a JSON mapping compatible with
    :class:`~flaccid.plugins.base.TrackMetadata`. If lyrics are not provided,
    they will be fetched using :class:`~flaccid.plugins.lyrics.LyricsPlugin`.

    If ``yes`` is ``False`` the user will be prompted for confirmation before
    tags are written.
    """
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

        print(f"Debug: file={file}, track_meta={track_meta}")
        await write_tags(file, track_meta)

    asyncio.run(_apply())


def store_credentials(provider: str, api_key: str) -> None:
    """Save ``api_key`` for ``provider`` using the system keyring."""
    keyring.set_password("flaccid", provider, api_key)


def save_paths(library: Path | None, cache: Path | None) -> dict:
    """Persist configured ``library`` and ``cache`` directories."""
    config_dir = Path.home() / ".flaccid"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "paths.json"

    data: dict = {}
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text())
        except Exception:
            data = {}

    if library is not None:
        data["library"] = str(library.resolve())
    if cache is not None:
        data["cache"] = str(cache.resolve())

    config_file.write_text(json.dumps(data, indent=2))
    return data
