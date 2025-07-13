"""`flaccid set` command-group (stub)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import json
import keyring
import typer

app = typer.Typer(help="Configuration & preferences")


def _save_paths(library: Path | None, cache: Path | None) -> Dict[str, str]:
    """Persist configured ``library`` and ``cache`` directories."""

    config_dir = Path.home() / ".flaccid"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "paths.json"

    data: Dict[str, str] = {}
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text())
        except Exception:
            data = {}

    if library is not None:
        data["library"] = str(library.resolve())
    if cache is not None:
        data["cache"] = str(cache.resolve())

    config_file.write_text(json.dumps(data, indent=2))
    return data


@app.command("auth")
def auth(
    provider: str = typer.Argument(..., help="e.g. qobuz, apple"),
) -> None:
    """Store credentials for the given music service."""

    api_key = typer.prompt("API key", hide_input=True)
    keyring.set_password("flaccid", provider, api_key)
    typer.echo("Credentials saved.")


@app.command("path")
def path(
    *,
    library: Path | None = typer.Option(None, help="Library directory"),
    cache: Path | None = typer.Option(None, help="Cache directory"),
) -> None:
    """Configure default library and cache paths."""

    settings: Any = _save_paths(library, cache)  # type: ignore[func-returns-value]
    typer.echo(settings)
