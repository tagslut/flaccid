"""`flaccid set` command-group (stub)."""

from __future__ import annotations

import typer

app = typer.Typer(help="Configuration & preferences")


@app.command("auth")
def auth(
    provider: str = typer.Argument(..., help="e.g. qobuz, apple"),
) -> None:
    """
    🚧  Stub implementation – will be fleshed out later.

    Store or update credentials for *PROVIDER*.
    """
    typer.echo(f"[stub] would configure credentials for {provider}")
