from __future__ import annotations

"""Download utilities CLI."""

import asyncio
from pathlib import Path

import typer

from flaccid.get.qobuz import download_track as qobuz_download
from flaccid.plugins.beatport import BeatportPlugin
from flaccid.plugins.tidal import TidalPlugin

app = typer.Typer(help="Download music from supported services")


@app.command()
def qobuz(
    track_id: str = typer.Argument(..., help="Qobuz track ID"),
    output: Path = typer.Argument(..., help="Where to save"),
) -> None:
    """Download a track from Qobuz."""

    success = qobuz_download(track_id, output)
    if not success:
        typer.echo("Download failed", err=True)
        raise typer.Exit(1)

    typer.echo(f"Saved to {output}")


@app.command()
def tidal(
    track_id: str = typer.Argument(..., help="Tidal track ID"),
    output: Path = typer.Argument(..., help="Where to save"),
) -> None:
    """Download a track from Tidal."""

    async def _run() -> None:
        async with TidalPlugin() as plugin:
            await plugin.authenticate()
            await plugin.download_track(track_id, output)

    asyncio.run(_run())
    typer.echo(f"Saved to {output}")


@app.command()
def beatport(
    track_id: str = typer.Argument(..., help="Beatport track ID"),
    output: Path = typer.Argument(..., help="Where to save"),
) -> None:
    """Download a track from Beatport."""

    async def _run() -> None:
        async with BeatportPlugin() as plugin:
            await plugin.authenticate()
            await plugin.download_track(track_id, output)

    asyncio.run(_run())
    typer.echo(f"Saved to {output}")
