from __future__ import annotations

import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def get(
    source: str = typer.Argument(None, help="The source to get from (e.g. qobuz)")
) -> None:
    if source is None:
        typer.echo("Missing argument: SOURCE", err=True)
        raise typer.Exit(1)
    if source != "qobuz":
        typer.echo("Unknown source", err=True)
        raise typer.Exit(1)
