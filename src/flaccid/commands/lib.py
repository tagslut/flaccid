"""Library management CLI."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from flaccid.core import library

app = typer.Typer(help="Manage library indexing")
watch_app = typer.Typer(help="Manage continuous library watching")
app.add_typer(watch_app, name="watch")


@app.command()
def scan(
    directory: List[Path] = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True
    ),
    db: Path = typer.Option(Path("library.db"), help="SQLite database path"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch for changes"),
) -> None:
    """Scan *directory* and index metadata in *db*."""

    files: List[Path] = []
    for d in directory:
        files.extend(library.scan_directory(d))
    library.index_changed_files(db, files)
    typer.echo(f"Indexed {len(files)} files")
    if watch:
        typer.echo("Watching for changes...")
        try:
            library.watch_library(directory, db)
        except KeyboardInterrupt:
            typer.echo("Stopped")


@watch_app.command("start")
def watch_start(
    directory: List[Path] = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True
    ),
    db: Path = typer.Option(Path("library.db"), help="SQLite database path"),
) -> None:
    """Start watching *directory* and update *db* on changes."""

    library.start_watching(directory, db)
    typer.echo(f"Watching {', '.join(map(str, directory))}")


@watch_app.command("stop")
def watch_stop(
    directory: List[Path] = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True
    )
) -> None:
    """Stop watching *directory* if active."""

    library.stop_watching(directory)
    typer.echo(f"Stopped watching {', '.join(map(str, directory))}")


@app.command("search")
def search(
    db: Path = typer.Option(Path("library.db"), help="SQLite database path"),
    filter: str = typer.Option("", "--filter", "-f", help="Search query"),
    sort: str | None = typer.Option(None, "--sort", "-s", help="Sort column"),
    limit: int | None = typer.Option(None, "--limit", "-l", help="Max results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset results"),
) -> None:
    """Query the library database."""

    rows = library.search_library(db, filter, sort=sort, limit=limit, offset=offset)
    for row in rows:
        typer.echo(row["path"])


@app.command("missing")
def report_missing(
    db: Path = typer.Option(Path("library.db"), help="SQLite database path"),
) -> None:
    """List tracks missing basic metadata fields."""

    rows = library.report_missing_metadata(db)
    for row in rows:
        typer.echo(row["path"])
