"""
CLI entry point for the FLACCID toolkit.
"""
import typer

# Root Typer instance exported for tests and entry-points
app = typer.Typer(name="flaccid", help="FLACCID metadata CLI toolkit")

@app.callback()
def _cli_root() -> None:
    """FLACCID CLI root command."""
    pass

@app.command()
def tag(path: str):
    """Tag a FLAC file with metadata."""
    import os
    if not os.path.exists(path):
        typer.echo("Path not found", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Tagging file: {path}")
