import typer

app = typer.Typer(help="FLACCID music downloader CLI")


@app.command()
def get(source: str):
    """Download tracks from SOURCE (e.g., Qobuz)."""
    raise NotImplementedError("`get` not yet implemented")


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
