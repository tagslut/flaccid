"""FLACCID command‑line interface (Typer)."""
from __future__ import annotations

import typer

# Root Typer instance exported for tests and entry‑points
app = typer.Typer(name="flaccid", help="FLACCID metadata CLI toolkit")


@app.callback()
def _cli_root() -> None:  # noqa: D401
    """FLACCID CLI root command."""
    # Add sub‑commands in dedicated modules later.
    pass


if __name__ == "__main__":  # pragma: no cover
    app()