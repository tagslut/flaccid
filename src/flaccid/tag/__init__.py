import typer
from . import qobuz, apple

app = typer.Typer(name="tag", help="Tag or enrich metadata using various sources.")
app.add_typer(qobuz.app, name="qobuz", help="Tag using Qobuz metadata.")
app.add_typer(apple.app, name="apple", help="Tag using Apple Music metadata.")