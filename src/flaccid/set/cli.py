"""\`flaccid set\` command-group (stub)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from flaccid.cli.placeholders import save_paths, store_credentials

app = typer.Typer(help="Configuration & preferences")


@app.command("auth")
def auth(
    provider: str = typer.Argument(..., help="e.g. qobuz, apple"),
) -> None:
    """Store credentials for the given music service."""

    api_key = typer.prompt("API key", hide_input=True)
    api_secret = typer.prompt("API secret", hide_input=True)
    store_credentials(provider, api_key, api_secret)
    typer.echo("Credentials saved.")


@app.command("path")
def path(
    *,
    library: Path | None = typer.Option(None, help="Library directory"),
    cache: Path | None = typer.Option(None, help="Cache directory"),
) -> None:
    """Configure default library and cache paths."""

    settings: Any = save_paths(library, cache)  # type: ignore[func-returns-value]
    typer.echo(settings)
