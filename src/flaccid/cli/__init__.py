#!/usr/bin/env python3
"""FLACCID command‑line interface package.

This module defines the root Typer application (`app`) and wires up each
sub‑command group (download, meta, apple, library, settings, duplicates,
plugins).
It should not contain any test code ― tests live exclusively under the *tests/* tree.
"""

from __future__ import annotations

import typer

# Sub‑command groups
from flaccid.commands.apple import app as apple_app
from flaccid.commands.duplicates import app as duplicates_app
from flaccid.commands.get import app as get_app
from flaccid.commands.lib import app as lib_app
from flaccid.commands.settings import app as settings_app
from flaccid.commands.tag import app as tag_app
from flaccid.commands.plugins import app as plugins_app

# --------------------------------------------------------------------------- #
# Root application
# --------------------------------------------------------------------------- #

app = typer.Typer(
    help=(
        "FLACCID CLI root application.  Provides 'download', 'meta', 'apple', "
        "'library', 'duplicates', 'settings', and 'plugins' sub‑commands."
    )
)

# Attach sub‑commands
app.add_typer(get_app, name="download")
app.add_typer(tag_app, name="meta")
app.add_typer(apple_app, name="apple")
app.add_typer(lib_app, name="library")
app.add_typer(settings_app, name="settings")
app.add_typer(duplicates_app, name="duplicates")
app.add_typer(plugins_app, name="plugins")

# What we intend to export when someone does: `from flaccid.cli import *`
__all__: list[str] = [
    "app",
]


@app.command()
def version() -> None:
    """Show the version of the FLACCID CLI."""
    try:
        from importlib import metadata

        from rich.console import Console

        console = Console()
        version = metadata.version("flaccid")
        console.print(f"FLACCID CLI version: [bold]{version}[/bold]")
    except Exception:
        console.print("FLACCID CLI version: [bold]development[/bold]")


def main() -> int:
    """Entry point for the CLI."""
    try:
        app()
        return 0
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
