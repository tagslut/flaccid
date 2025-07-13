"""`flaccid tag` command-group (stub)."""

from __future__ import annotations

from pathlib import Path

import click
import typer

from . import apple, beatport, discogs, qobuz, utils

PROVIDERS = {
    "qobuz": qobuz,
    "apple": apple,
    "discogs": discogs,
    "beatport": beatport,
}

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

    provider_mod = PROVIDERS.get(provider.lower())
    if provider_mod is None:
        raise typer.BadParameter(f"Unsupported provider: {provider}")

    metadata = provider_mod.fetch_metadata(file)
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

    utils.apply_metadata(file, metadata_file, yes)
    typer.echo("Metadata applied successfully")
