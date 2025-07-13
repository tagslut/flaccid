from __future__ import annotations

"""CLI commands related to library management."""

import typer

app = typer.Typer()


@app.callback()
def lib() -> None:
    """Library command group root."""
    ...
