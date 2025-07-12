from __future__ import annotations

"""Helper functions used by the CLI commands."""

import asyncio
import json
from pathlib import Path

import keyring
from mutagen.flac import FLAC
from typer import confirm

from flaccid.plugins import BeatportPlugin, DiscogsPlugin
from flaccid.shared.apple_api import AppleAPI
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata
from flaccid.shared.qobuz_api import QobuzAPI


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
        if provider.lower() == "qobuz":
            async with QobuzAPI() as api:
                return await api.search(query)
        if provider.lower() == "apple":
            async with AppleAPI() as api:
                return await api._itunes_search(query)
        if provider.lower() == "discogs":
            async with DiscogsPlugin() as api:
                return await api.search_track(query)
        if provider.lower() == "beatport":
            async with BeatportPlugin() as api:
                return await api.search_track(query)
        raise ValueError(f"Unsupported provider: {provider}")

    return asyncio.run(_search())


def apply_metadata(file: Path, metadata_file: Path | None, yes: bool) -> None:
    """Apply metadata from *metadata_file* to *file*.

    If ``yes`` is ``False`` the user will be prompted for confirmation before
    tags are written.
    """
    if metadata_file is None:
        raise ValueError("metadata_file is required")

    with metadata_file.open("r", encoding="utf-8") as fh:
        metadata: dict = json.load(fh)

    if not yes and not confirm("Apply metadata?"):
        return

    audio = FLAC(str(file))
    for key, value in metadata.items():
        if isinstance(value, list):
            audio[key] = [str(v) for v in value]
        else:
            audio[key] = str(value)
    audio.save()


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
