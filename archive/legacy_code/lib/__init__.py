import typer

from . import index, scan

app = typer.Typer(name="lib", help="Manage and index your local music library.")
app.add_typer(scan.app, name="scan", help="Scan directories and extract metadata.")
app.add_typer(
    index.app, name="index", help="Build or query the music library database."
)
