import typer
from flaccid import get

app = typer.Typer(help="FLACCID CLI Toolkit")
app.add_typer(get.app, name="get")

if __name__ == "__main__":
    app()
