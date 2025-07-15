#!/usr/bin/env python3
"""FLACCID command‑line interface package.

This module defines the root Typer application (`app`) and wires up each
sub‑command group (download, meta, apple, library, settings).  It should not
contain any test code ― tests live exclusively under the *tests/* tree.
"""

from __future__ import annotations

import typer

# Sub‑command groups
from flaccid.commands.apple import app as apple_app
from flaccid.commands.get import app as get_app
from flaccid.commands.lib import app as lib_app
from flaccid.commands.settings import app as settings_app
from flaccid.commands.tag import app as tag_app

# --------------------------------------------------------------------------- #
# Root application
# --------------------------------------------------------------------------- #

app = typer.Typer(
    help=(
        "FLACCID CLI root application.  Provides 'download', 'meta', 'apple', "
        "'library', and 'settings' sub‑commands."
    )
)

# Attach sub‑commands
app.add_typer(get_app, name="download")
app.add_typer(tag_app, name="meta")
app.add_typer(apple_app, name="apple")
app.add_typer(lib_app, name="library")
app.add_typer(settings_app, name="settings")

# What we intend to export when someone does: `from flaccid.cli import *`
__all__: list[str] = [
    "app",
]
