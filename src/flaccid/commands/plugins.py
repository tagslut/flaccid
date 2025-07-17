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


__all__ = ["app"]
