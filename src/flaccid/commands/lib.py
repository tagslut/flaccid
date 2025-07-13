from __future__ import annotations

"""Library management CLI."""

from pathlib import Path

import typer

from flaccid.core import library

app = typer.Typer(help="Manage library indexing")


@app.command()
def scan(
    directory: Path = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True
    ),
    db: Path = typer.Option(Path("library.db"), help="SQLite database path"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch for changes"),
) -> None:
    """Scan *directory* and index metadata in *db*."""

    files = library.scan_directory(directory)
    library.index_changed_files(db, files)
    typer.echo(f"Indexed {len(files)} files")
    if watch:
        typer.echo("Watching for changes...")
        try:
            library.watch_library(directory, db)
        except KeyboardInterrupt:
            typer.echo("Stopped")
