import os

import typer

app = typer.Typer(help="Apple Music CLI commands.")


@app.command()
def auth():
    """Authenticate with Apple Music."""
    api_key = os.getenv("APPLE_MUSIC_API_KEY")
    if not api_key:
        typer.echo("Missing API key for authentication.", err=True)
        raise typer.Exit(code=2)
    typer.echo("Authenticated")


@app.command()
def status():
    """Check authentication status."""
    typer.echo("Authenticated")
