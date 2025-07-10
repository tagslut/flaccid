from __future__ import annotations

import typer

app = typer.Typer()


@app.callback()
def lib() -> None:
    """Library command group root."""
    ...
