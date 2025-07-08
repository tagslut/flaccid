import typer
from . import qobuz

app = typer.Typer(name="get", help="Download music from supported services.")
app.add_typer(qobuz.app, name="qobuz", help="Download music from Qobuz.")
