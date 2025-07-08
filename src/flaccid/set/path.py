import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
import os

console = Console()
app = typer.Typer(help="Configure directory paths.")

# Default configuration
DEFAULT_PATHS = {
    "cache": "~/.flaccid/cache",
    "config": "~/.flaccid/config",
    "music": "~/Music",
    "downloads": "~/Downloads/FLACCID"
}

@app.command("set")
def set_path(
    name: str = typer.Argument(..., help="Path name (cache, config, music, downloads)"),
    path: str = typer.Argument(..., help="Directory path")
):
    """
    Set a directory path configuration.

    Args:
        name: The path name to configure
        path: The directory path
    """
    if name not in DEFAULT_PATHS:
        console.print(f"❌ Unknown path name: {name}", style="red")
        console.print(f"Valid names: {', '.join(DEFAULT_PATHS.keys())}")
        raise typer.Exit(1)

    expanded_path = Path(path).expanduser().resolve()

    # Create directory if it doesn't exist
    try:
        expanded_path.mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Set {name} path to: {expanded_path}", style="green")
    except Exception as e:
        console.print(f"❌ Error setting path: {e}", style="red")
        raise typer.Exit(1)

@app.command("list")
def list_paths():
    """List all configured directory paths."""
    table = Table(title="Directory Paths")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="yellow")

    for name, default_path in DEFAULT_PATHS.items():
        expanded_path = Path(default_path).expanduser()
        status = "✅ Exists" if expanded_path.exists() else "❌ Missing"

        table.add_row(
            name,
            str(expanded_path),
            status
        )

    console.print(table)

@app.command("create")
def create_paths():
    """Create all default directories."""
    created_count = 0

    for name, default_path in DEFAULT_PATHS.items():
        expanded_path = Path(default_path).expanduser()

        if not expanded_path.exists():
            try:
                expanded_path.mkdir(parents=True, exist_ok=True)
                console.print(f"✅ Created {name}: {expanded_path}", style="green")
                created_count += 1
            except Exception as e:
                console.print(f"❌ Error creating {name}: {e}", style="red")
        else:
            console.print(f"📁 {name} already exists: {expanded_path}", style="dim")

    if created_count > 0:
        console.print(f"\n🎉 Created {created_count} directories", style="bold green")
    else:
        console.print("\n✨ All directories already exist", style="bold blue")
