from __future__ import annotations

"""Subcommands for manipulating metadata tags."""

from pathlib import Path

import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def tag(
    path: Path = typer.Argument(
        None, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    )
) -> None:
    if path is None:
        typer.echo("Missing argument: PATH", err=True)
        raise typer.Exit(1)
    if not path.exists():
        typer.echo("Path not found", err=True)
        raise typer.Exit(1)
