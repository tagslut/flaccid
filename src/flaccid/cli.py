#!/usr/bin/env python3
"""
Main CLI entry point for the FLACCID CLI.

This module defines the main CLI command and imports subcommands.
"""

from __future__ import annotations

import sys
from importlib import metadata
from typing import Optional

import typer
from rich.console import Console

from flaccid.commands import tag

# Create main app
app = typer.Typer(
    help="FLACCID CLI Toolkit for downloading and tagging FLAC files",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(tag.app, name="tag", help="Tag files with metadata")

console = Console()


@app.callback()
def callback() -> None:
    """FLACCID CLI Toolkit for downloading and tagging FLAC files."""
    pass


@app.command()
def version() -> None:
    """Show the version of the FLACCID CLI."""
    try:
        version = metadata.version("flaccid")
        console.print(f"FLACCID CLI version: [bold]{version}[/bold]")
    except metadata.PackageNotFoundError:
        console.print("FLACCID CLI version: [bold]development[/bold]")


def main() -> int:
    """Entry point for the CLI."""
    try:
        app()
        return 0
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
