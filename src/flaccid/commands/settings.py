from __future__ import annotations

"""Settings CLI."""

import keyring
import typer

app = typer.Typer(help="Manage credentials")


@app.command()
def store(
    service: str = typer.Argument(..., help="Service name"),
    token: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    """Store *token* in keyring under *service*."""

    keyring.set_password("flaccid", service, token)
    typer.echo("Stored")
