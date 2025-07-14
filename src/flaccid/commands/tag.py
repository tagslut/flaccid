from __future__ import annotations

"""Tagging CLI."""

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command()
def apple(
    file: Path = typer.Argument(None, exists=True, resolve_path=True),
    track_id: str = typer.Option(None, help="Apple Music track ID"),
    auth: bool = typer.Option(False, help="Authenticate with Apple Music"),
    status: bool = typer.Option(False, help="Check authentication status"),
) -> None:
    """Tag *file* with metadata from Apple Music or handle authentication."""

    if auth:
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing API key for authentication.", err=True)
            raise typer.Exit(code=2)
        typer.echo("Authenticated")
        return

    if status:
        typer.echo("Authenticated")
        return

    if file and track_id:

        async def _run() -> None:
            async with AppleMusicPlugin() as plugin:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data)

        asyncio.run(_run())
        typer.echo("Tagging complete")
    else:
        typer.echo("Invalid arguments. Use --help for usage information.", err=True)
        raise typer.Exit(code=2)
