#!/usr/bin/env python3
"""Tag commands for the FLACCID CLI."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer

from flaccid.core.metadata import fetch_and_tag
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


@app.command("authenticate")
def authenticate(
    provider: str = typer.Argument(..., help="The provider to authenticate with")
) -> None:
    """Authenticate with a provider."""
    if provider.lower() == "apple":
        typer.echo("Authenticating with Apple Music")
        # Implementation would go here
        typer.echo("Authenticated")
    else:
        typer.echo(f"Provider {provider} not supported")


@app.command("fetch")
def fetch(
    file_path: str = typer.Argument(..., help="Path to the audio file"),
    provider: str = typer.Option(
        "apple", "--provider", "-p", help="The metadata provider to use"
    ),
) -> None:
    """Fetch metadata for an audio file."""
    typer.echo(f"Fetching metadata for {file_path} from {provider}")


@app.command("apply")
def apply(
    file_path: Path = typer.Argument(..., help="Path to the audio file", exists=True),
    metadata_file: Path = typer.Option(
        ..., help="Path to the metadata file", exists=True
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Apply metadata to an audio file."""
    typer.echo(f"Applying metadata from '{metadata_file}' to '{file_path}'")
    if not yes:
        typer.echo("Use --yes to skip confirmation")


@app.command()
def apple(
    file: Path = typer.Argument(
        ..., exists=True, resolve_path=True, help="Path to the audio file to tag."
    ),
    track_id: str = typer.Option(
        ..., help="Apple Music track ID (from iTunes Store URL)."
    ),
    auth: bool = typer.Option(
        False, "--auth", help="Authenticate with Apple Music (placeholder)."
    ),
    status: bool = typer.Option(
        False, "--status", help="Check authentication status (placeholder)."
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        help="Rename file using this filename template after tagging.",
    ),
) -> None:
    """Tag a file with metadata from Apple Music."""
    if auth:
        # NOTE: The current plugin uses an API that doesn't need auth.
        # This is a placeholder for a future implementation.
        api_key = os.getenv("APPLE_MUSIC_API_KEY")
        if not api_key:
            typer.echo("Missing APPLE_MUSIC_API_KEY environment variable.", err=True)
            raise typer.Exit(code=1)
        typer.echo("Authentication successful (placeholder).")
        return

    if status:
        typer.echo("Authentication status: OK (placeholder).")
        return

    async def _run() -> None:
        async with AppleMusicPlugin() as plugin:
            try:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(file, data, filename_template=template)
                typer.echo(f"✅ Successfully tagged '{file.name}'")
            except ValueError as e:
                typer.echo(f"❌ Error: {e}", err=True)
                raise typer.Exit(1) from e
            except Exception as e:
                typer.echo(f"❌ An unexpected error occurred: {e}", err=True)
                raise typer.Exit(1) from e

    asyncio.run(_run())
