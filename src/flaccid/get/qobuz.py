import typer

app = typer.Typer(help="Qobuz downloader")

@app.command()
def track(id: str):
    """
    Download a track by Qobuz track ID.
    """
    print(f"🔻 Simulated download for Qobuz track ID: {id}")
