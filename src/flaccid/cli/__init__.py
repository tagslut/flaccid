#!/usr/bin/env python3
"""FLACCID console-script entrypoint."""
from __future__ import annotations

import typer

from flaccid.commands.get import app as new_get_app
from flaccid.commands.lib import app as new_lib_app
from flaccid.commands.settings import app as new_settings_app
from flaccid.commands.tag import app as new_tag_app
from flaccid.get import app as get_app
from flaccid.lib import app as lib_app
from flaccid.set import app as set_app
from flaccid.tag import app as tag_app

from .placeholders import (
    apply_metadata,
    fetch_metadata,
    save_paths,
    store_credentials,
)

__all__ = [
    "app",
    "apply_metadata",
    "fetch_metadata",
    "save_paths",
    "store_credentials",
]

# Add other subcommands as needed

app = typer.Typer(help="FLACCID CLI root app.")

app.add_typer(get_app, name="get")
app.add_typer(tag_app, name="tag")
app.add_typer(lib_app, name="lib")
app.add_typer(set_app, name="set")
# New command group implementations
app.add_typer(new_get_app, name="download")
app.add_typer(new_tag_app, name="meta")
app.add_typer(new_lib_app, name="library")
app.add_typer(new_settings_app, name="settings")
# Add other subcommands as needed

if __name__ == "__main__":
    app()
