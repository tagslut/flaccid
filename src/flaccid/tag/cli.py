"""`flaccid tag` command-group (stub)."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(help="Metadata-tagging operations")


@app.command("fetch")
def fetch(
    file: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    provider: str = typer.Option("qobuz", help="Metadata source (qobuz, apple, …)"),
) -> None:
    """
    🚧  Stub implementation – will be fleshed out next.

    Fetch fresh tags for *FILE* from the chosen *PROVIDER* and print them.
    """
    typer.echo(f"[stub] would fetch metadata for {file} using {provider}")
