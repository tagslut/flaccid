"""
Root Typer application for the flaccid CLI.
"""

from __future__ import annotations

import typer

# Import subcommand applications
from flaccid.get import app as get_app
from flaccid.lib import app as lib_app
from flaccid.tag import app as tag_app

# Define the root Typer app
app = typer.Typer()

# Add subcommands to the root app
app.add_typer(get_app, name="get")
app.add_typer(lib_app, name="lib")
app.add_typer(tag_app, name="tag")
