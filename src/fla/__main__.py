import os
import typer

app = typer.Typer(help="FLACCID music downloader CLI")

valid_sources = {"qobuz", "tidal"}  # Define valid sources globally


@app.command()
def get(
    source: str = typer.Argument(
        None, help="Source to download from (e.g., qobuz, tidal)"
    )
):
    """Download tracks from SOURCE."""
    if source is None:
        typer.echo("Error: Missing argument 'source'", err=True)
        raise typer.Exit(code=1)

    if source not in valid_sources:
        typer.echo(f"Unknown source: {source}", err=True)
        raise typer.Exit(code=1)

    # TODO: integrate actual downloader here
    typer.echo(f"Would download from {source}…")


@app.command()
def tag(path: str = typer.Argument(..., help="File or directory to tag")):
    """Tag a file or directory with metadata."""
    if not os.path.exists(path):
        typer.echo(f"Path not found: {path}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Would tag files under {path}…")


@app.command()
def lib(action: str):
    """Perform library management ACTION (e.g., inventory, report)."""
    raise NotImplementedError("`lib` not yet implemented")


if __name__ == "__main__":
    app()
