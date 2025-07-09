from __future__ import annotations

from pathlib import Path


def fetch_metadata(file: Path, provider: str) -> dict:
    """Placeholder: fetch metadata from provider."""
    return {"___": "stub"}


def apply_metadata(file: Path, metadata_file: Path | None, yes: bool) -> None:
    """Placeholder: apply metadata to file."""
    ...


def store_credentials(provider: str, api_key: str) -> None:
    """Placeholder: save API credentials."""
    ...


def save_paths(library: Path | None, cache: Path | None) -> None:
    """Placeholder: save configured library and cache paths."""
    ...
