from __future__ import annotations

"""Settings CLI."""

import keyring
import typer
from pathlib import Path

app = typer.Typer(help="Manage credentials")


@app.command()
def store(
    service: str = typer.Argument(..., help="Service name"),
    token: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    """Store *token* in keyring under *service*."""

    keyring.set_password("flaccid", service, token)
    typer.echo("Stored")


@app.command()
def precedence(
    order: str = typer.Argument(..., help="Comma-separated plugin names"),
    file: Path = typer.Option(Path("settings.toml"), "--file", help="Config file"),
) -> None:
    """Set plugin precedence order in the settings file."""

    names = [n.strip() for n in order.split(",") if n.strip()]
    if not file.exists():
        file.write_text("[default]\n")
    lines = [ln for ln in file.read_text().splitlines() if not ln.startswith("PLUGIN_PRECEDENCE")]
    lines.append(f"PLUGIN_PRECEDENCE = '{','.join(names)}'")
    file.write_text("\n".join(lines) + "\n")
    typer.echo("Plugin precedence updated")
