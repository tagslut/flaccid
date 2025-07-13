from __future__ import annotations

"""Tagging CLI."""

import asyncio
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command()
def apple(
    file: Path = typer.Argument(..., exists=True, resolve_path=True),
    track_id: str = typer.Argument(..., help="Apple Music track ID"),
) -> None:
    """Tag *file* with metadata from Apple Music."""

    async def _run() -> None:
        async with AppleMusicPlugin() as plugin:
            data = await plugin.get_track(track_id)
            await fetch_and_tag(file, data)

    asyncio.run(_run())
    typer.echo("Tagging complete")
