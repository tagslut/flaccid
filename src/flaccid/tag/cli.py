"""`flaccid tag` command-group (stub)."""

from __future__ import annotations

from pathlib import Path
import asyncio

import click
import typer

from flaccid.plugins.registry import get_provider
from flaccid.shared.metadata_utils import build_search_query, get_existing_metadata
from . import utils
from flaccid.core.metadata import load_metadata
from flaccid.plugins.base import TrackMetadata

app = typer.Typer(help="Metadata-tagging operations")


@app.command("fetch")
def fetch(
    file: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    provider: str = typer.Option(
        "qobuz",
        help="Metadata source",
        show_choices=True,
        case_sensitive=False,
        click_type=click.Choice(
            ["qobuz", "apple", "discogs", "beatport"], case_sensitive=False
        ),
    ),
) -> None:
    """Fetch metadata for *file* from the specified *provider* and print it."""

    async def _search() -> dict:
        plugin_cls = get_provider(provider)
        existing = get_existing_metadata(str(file))
        query = build_search_query(existing)
        async with plugin_cls() as api:
            return await api.search_track(query)

    metadata = asyncio.run(_search())
    typer.echo(metadata)


@app.command("apply")
def apply(
    file: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    metadata_file: Path | None = typer.Option(
        None, exists=True, readable=True, resolve_path=True
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without prompting"),
) -> None:
    """Apply metadata to *file*, optionally using *metadata_file*."""

    if metadata_file:
        data = load_metadata(metadata_file)
        meta = TrackMetadata(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            album=data.get("album", ""),
            track_number=int(data.get("track_number", 0)),
            disc_number=int(data.get("disc_number", 0)),
            year=data.get("year"),
            isrc=data.get("isrc"),
            lyrics=data.get("lyrics"),
        )
    else:
        meta = utils.fallback_fetch(file)

    utils.apply_metadata(file, meta, yes)
    typer.echo("Metadata applied successfully")

