#!/usr/bin/env python3
"""Tag commands for the FLACCID CLI."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re

import typer

from flaccid.core.metadata import fetch_and_tag
from rich.console import Console
from rich.table import Table
from flaccid.plugins.apple import AppleMusicPlugin

app = typer.Typer(help="Tag files with metadata")


def _parse_strategy_options(args: list[str]) -> dict[str, str]:
    """Return ``--strategy.FIELD`` options parsed from ``args``."""

    pattern = re.compile(r"^--strategy\.(?P<field>[\w_]+)$")
    strategies: dict[str, str] = {}
    i = 0
    while i < len(args):
        match = pattern.match(args[i])
        if match:
            field = match.group("field")
            if i + 1 >= len(args):
                raise typer.BadParameter(f"Missing value for {args[i]}")
            strategies[field] = args[i + 1]
            i += 2
        else:
            i += 1
    return strategies


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


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
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
    ctx: typer.Context = typer.Option(None),
) -> None:
    """Tag a file with metadata from Apple Music.

    ``--strategy.FIELD`` options may be provided to control field merge
    behaviour when multiple metadata sources are used.
    """
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

    strategies = _parse_strategy_options(ctx.args)

    async def _run() -> None:
        async with AppleMusicPlugin() as plugin:
            try:
                data = await plugin.get_track(track_id)
                await fetch_and_tag(
                    file,
                    data,
                    strategies=strategies,
                    filename_template=template,
                )
                typer.echo(f"✅ Successfully tagged '{file.name}'")
            except ValueError as e:
                typer.echo(f"❌ Error: {e}", err=True)
                raise typer.Exit(1) from e
            except Exception as e:
                typer.echo(f"❌ An unexpected error occurred: {e}", err=True)
                raise typer.Exit(1) from e

    asyncio.run(_run())


@app.command("audit")
def audit(file: Path = typer.Argument(..., exists=True, resolve_path=True)) -> None:
    """Show provenance information for tagged fields."""

    sources_file = file.with_suffix(".sources.json")
    if not sources_file.exists():
        typer.echo("No provenance data found", err=True)
        raise typer.Exit(1)

    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - unlikely
        typer.echo(f"Failed to read provenance: {exc}", err=True)
        raise typer.Exit(1)

    table = Table(title=f"Provenance for {file.name}")
    table.add_column("Field")
    table.add_column("Provider")
    for key, provider in data.items():
        table.add_row(key, provider)
    Console().print(table)
