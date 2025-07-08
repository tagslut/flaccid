import typer

app = typer.Typer(help="FLACCID: Modular FLAC CLI Toolkit")

# Import and add all module subcommands
from . import get, tag, lib, core, shared, set as set_module

app.add_typer(get.app, name="get", help="Download music from various services")
app.add_typer(tag.app, name="tag", help="Tag FLAC files with metadata")
app.add_typer(lib.app, name="lib", help="Manage your local music library")
app.add_typer(core.app, name="core", help="Core utilities and tools")
app.add_typer(shared.app, name="shared", help="Shared utilities and configuration")
app.add_typer(set_module.app, name="set", help="Configure FLACCID settings")

if __name__ == "__main__":
    app()