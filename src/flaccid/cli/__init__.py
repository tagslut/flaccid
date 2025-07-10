#!/usr/bin/env python3
"""FLACCID console-script entrypoint."""
from __future__ import annotations

import typer

from flaccid.get import app as get_app
from flaccid.lib import app as lib_app
from flaccid.set import app as set_app
from flaccid.tag import app as tag_app

# Add other subcommands as needed

app = typer.Typer(help="FLACCID CLI root app.")

app.add_typer(get_app, name="get")
app.add_typer(tag_app, name="tag")
app.add_typer(lib_app, name="lib")
app.add_typer(set_app, name="set")
# Add other subcommands as needed

if __name__ == "__main__":
    app()
