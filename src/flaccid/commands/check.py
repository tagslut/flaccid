"""Diagnostic checks for plugin imports, tokens and paths."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import typer
from typer import Context

from flaccid.core.config import load_settings
from flaccid.plugins.loader import PluginLoader

app = typer.Typer(help="Run environment checks", invoke_without_command=True)


@app.callback(invoke_without_command=True)
def _default(ctx: typer.Context) -> None:
    """Run ``run`` when no sub-command is given."""
    if ctx.invoked_subcommand is None:
        run()


def _check_plugin_imports() -> List[str]:
    """Return a list of plugin import error messages."""
    from flaccid.plugins import registry

    paths = list(registry.paths)
    extra = os.getenv("FLACCID_PLUGIN_PATH")
    if extra:
        paths.extend(Path(p) for p in extra.split(os.pathsep))
    loader = PluginLoader(*paths)
    errors: List[str] = []
    for base in loader.paths:
        if not base.exists():
            errors.append(f"Missing plugin path: {base}")
            continue
        skip = {"loader", "registry", "__init__", "base"}
        for file in base.glob("*.py"):
            if file.stem in skip or file.name.startswith("_"):
                continue
            try:  # noqa: PERF203 - best effort diagnostics
                loader._load_module(file)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - error path
                errors.append(f"{file.name}: {exc}")
    return errors


def _check_tokens() -> List[str]:
    """Return a list of missing credential messages."""
    settings = load_settings()
    errors: List[str] = []
    if not settings.qobuz.app_id or not settings.qobuz.token:
        errors.append("Qobuz credentials missing")
    if not settings.apple.developer_token:
        errors.append("Apple token missing")
    if not settings.discogs_token:
        errors.append("Discogs token missing")
    if not settings.beatport_token:
        errors.append("Beatport token missing")
    if not settings.tidal_token:
        errors.append("Tidal token missing")
    return errors


def _check_paths() -> List[str]:
    """Return a list of path related error messages."""
    config = Path.home() / ".flaccid" / "paths.json"
    if not config.exists():
        return ["Paths configuration not found"]
    try:
        data = json.loads(config.read_text())
    except Exception:  # pragma: no cover - error path
        return ["Paths configuration unreadable"]
    errors: List[str] = []
    lib = data.get("library")
    cache = data.get("cache")
    if not lib or not Path(lib).exists():
        errors.append("Library path missing")
    if not cache or not Path(cache).exists():
        errors.append("Cache path missing")
    return errors


@app.command()
def run() -> None:
    """Run diagnostic checks and print a summary."""
    plugin_errors = _check_plugin_imports()
    token_errors = _check_tokens()
    path_errors = _check_paths()

    if not plugin_errors and not token_errors and not path_errors:
        typer.echo("✅ All checks passed!")
        return

    if plugin_errors:
        typer.echo("Plugin issues:")
        for err in plugin_errors:
            typer.echo(f"  - {err}")
    if token_errors:
        typer.echo("Token issues:")
        for err in token_errors:
            typer.echo(f"  - {err}")
    if path_errors:
        typer.echo("Path issues:")
        for err in path_errors:
            typer.echo(f"  - {err}")
    raise typer.Exit(1)


__all__ = ["app"]
