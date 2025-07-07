import typer

app = typer.Typer(help="FLACCID music downloader CLI")


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
def tag(path: str):
    """Tag a file or directory at PATH with metadata."""
    raise NotImplementedError("`tag` not yet implemented")


@app.command()
def lib(action: str):
    """Perform library management ACTION (e.g., inventory, report)."""
    raise NotImplementedError("`lib` not yet implemented")


if __name__ == "__main__":
    app()
