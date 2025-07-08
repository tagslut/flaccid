import typer
from . import auth, path

app = typer.Typer(name="set", help="Configure FLACCID settings.")
app.add_typer(auth.app, name="auth", help="Manage authentication credentials.")
app.add_typer(path.app, name="path", help="Configure directory paths.")
