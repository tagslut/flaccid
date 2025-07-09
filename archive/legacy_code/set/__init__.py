import typer

from . import auth, path

app = typer.Typer(name="set", help="Configure FLACCID authentication and paths.")
app.add_typer(auth.app, name="auth", help="Store auth credentials for services.")
app.add_typer(path.app, name="path", help="Configure download and library folders.")
