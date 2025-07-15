"""Subcommands for manipulating metadata tags."""

from __future__ import annotations

from pathlib import Path

import typer

from .utils import write_tags

__all__ = ["write_tags"]

app = typer.Typer()


@app.callback(invoke_without_command=True)
def tag(
    path: Path | None = typer.Argument(
        None, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    ),
) -> None:
    """Manage metadata tags for local audio files."""
    if path is None:
        typer.echo("Missing argument: PATH", err=True)
        raise typer.Exit(1)
    if not path.exists():
        typer.echo("Path not found", err=True)
        raise typer.Exit(1)
