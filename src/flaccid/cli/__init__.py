#!/usr/bin/env python3
"""FLACCID console-script entrypoint."""
from __future__ import annotations

import typer

from flaccid.commands.apple import app as apple_app
from flaccid.commands.get import app as new_get_app
from flaccid.commands.lib import app as new_lib_app
from flaccid.commands.settings import app as new_settings_app
from flaccid.commands.tag import app as new_tag_app

from .placeholders import apply_metadata, fetch_metadata, save_paths, store_credentials

__all__ = [
    "app",
    "apply_metadata",
    "fetch_metadata",
    "save_paths",
    "store_credentials",
]

# Add other subcommands as needed

app = typer.Typer(
    help=(
        "FLACCID CLI root app. Provides 'download', 'meta', 'library', and "
        "'settings' commands."
    )
)

# New command group implementations
app.add_typer(new_get_app, name="download")
app.add_typer(new_tag_app, name="meta")
app.add_typer(apple_app, name="apple")
app.add_typer(new_lib_app, name="library")
app.add_typer(new_settings_app, name="settings")
# Add other subcommands as needed

if __name__ == "__main__":
    app()
