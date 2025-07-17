"""Utility commands for plugin development."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, Set

import typer

app = typer.Typer(help="Utilities for managing plugins")


def _import_aliases(tree: ast.Module) -> dict[str, str]:
    """Return mapping of local names to plugin base names."""
    mapping: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "flaccid.plugins.base":
            for alias in node.names:
                if alias.name in {"MetadataProviderPlugin", "LyricsProviderPlugin"}:
                    mapping[alias.asname or alias.name] = alias.name
    return mapping


def _base_names(bases: Iterable[ast.expr], aliases: dict[str, str]) -> Set[str]:
    names: Set[str] = set()
    for base in bases:
        if isinstance(base, ast.Name):
            names.add(aliases.get(base.id, base.id))
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)
    return names


def _method_names(body: Iterable[ast.stmt]) -> Set[str]:
    """Return a set of method names defined in *body*."""
    return {
        n.name
        for n in body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


REQUIRED_METADATA = {
    "open",
    "close",
    "authenticate",
    "search_track",
    "get_track",
    "get_album",
}
REQUIRED_LYRICS = {"open", "close", "get_lyrics"}


@app.command()
def validate(file: Path) -> None:
    """Validate provider plugins defined in *file*."""

    source = file.read_text()
    tree = ast.parse(source, filename=str(file))
    aliases = _import_aliases(tree)

    found = False
    errors: list[str] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node.bases, aliases)
        methods = _method_names(node.body)
        if "MetadataProviderPlugin" in bases:
            found = True
            missing = sorted(REQUIRED_METADATA - methods)
            if missing:
                errors.append(f"{node.name}: missing {', '.join(missing)}")
            else:
                typer.echo(f"{node.name}: OK")
        elif "LyricsProviderPlugin" in bases:
            found = True
            missing = sorted(REQUIRED_LYRICS - methods)
            if missing:
                errors.append(f"{node.name}: missing {', '.join(missing)}")
            else:
                typer.echo(f"{node.name}: OK")

    if not found:
        typer.echo("No plugin classes found", err=True)
        raise typer.Exit(1)

    if errors:
        for msg in errors:
            typer.echo(msg, err=True)
        raise typer.Exit(1)

    typer.echo("All plugins valid!")


@app.command("scaffold-tests")
def scaffold_tests(plugin: Path) -> None:
    """Create basic pytest scaffolding for *plugin*.

    The command detects the plugin class within ``plugin`` and writes a test
    file under ``tests/plugins`` with simple mocks for ``search_track`` and
    ``get_track`` as well as error handling. The generated path is printed on
    success.
    """

    source = plugin.read_text()
    tree = ast.parse(source, filename=str(plugin))
    aliases = _import_aliases(tree)

    plugin_class = None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node.bases, aliases)
        if "MetadataProviderPlugin" in bases or "LyricsProviderPlugin" in bases:
            plugin_class = node.name
            break

    if not plugin_class:
        typer.echo("No plugin class found", err=True)
        raise typer.Exit(1)

    module = plugin.with_suffix("").as_posix().replace("/", ".")
    if module.startswith("src."):
        module = module[4:]

    dest_dir = Path("tests/plugins")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"test_{plugin.stem}.py"

    content = f"""import pytest
from unittest.mock import AsyncMock

from {module} import {plugin_class}


@pytest.mark.asyncio
async def test_search_track(monkeypatch):
    plugin = {plugin_class}()
    monkeypatch.setattr(plugin, "search_track", AsyncMock(return_value={{}}))
    result = await plugin.search_track("query")
    assert result == {{}}


@pytest.mark.asyncio
async def test_get_track(monkeypatch):
    plugin = {plugin_class}()
    monkeypatch.setattr(plugin, "get_track", AsyncMock(return_value=None))
    result = await plugin.get_track("id")
    assert result is None


@pytest.mark.asyncio
async def test_get_track_error(monkeypatch):
    plugin = {plugin_class}()
    monkeypatch.setattr(plugin, "get_track", AsyncMock(side_effect=Exception))
    with pytest.raises(Exception):
        await plugin.get_track("id")
"""

    dest.write_text(content)
    typer.echo(str(dest))


__all__ = ["app"]
