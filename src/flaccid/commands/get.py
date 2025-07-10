from __future__ import annotations

"""Download utilities CLI."""

import asyncio
from pathlib import Path

import typer

from flaccid.plugins.qobuz import QobuzPlugin

app = typer.Typer(help="Download music from supported services")


@app.command()
def qobuz(
    track_id: str = typer.Argument(..., help="Qobuz track ID"),
    output: Path = typer.Argument(..., help="Where to save"),
) -> None:
    """Download a track from Qobuz (placeholder implementation)."""

    async def _run() -> None:
        async with QobuzPlugin() as plugin:
            await plugin.authenticate()
            meta = await plugin.get_track(track_id)
            output.write_text(f"Downloaded {meta.title}")

    asyncio.run(_run())
    typer.echo(f"Saved to {output}")
