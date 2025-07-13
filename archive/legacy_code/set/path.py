from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Configure FLACCID paths and directories.")

# Default config location
DEFAULT_CONFIG_DIR = Path.home() / ".flaccid"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "paths.json"


class PathConfig:
    """Manages path configuration."""

    def __init__(self, config_file: Path = DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                console.print(f"❌ Error loading config: {e}", style="red")
                return {}
        return {}

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            console.print(f"❌ Error saving config: {e}", style="red")
            return False

    def set_path(self, path_type: str, path_value: str) -> bool:
        """Set a path in the configuration."""
        expanded_path = Path(path_value).expanduser().resolve()

        # Create directory if it doesn't exist
        try:
            expanded_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"❌ Error creating directory: {e}", style="red")
            return False

        self.config[path_type] = str(expanded_path)
        return self.save_config()

    def get_path(self, path_type: str) -> Optional[str]:
        """Get a path from the configuration."""
        return self.config.get(path_type)

    def get_all_paths(self) -> dict:
        """Get all configured paths."""
        return self.config.copy()

    def remove_path(self, path_type: str) -> bool:
        """Remove a path from the configuration."""
        if path_type in self.config:
            del self.config[path_type]
            return self.save_config()
        return False


# Path type definitions
PATH_TYPES = {
    "library": {
        "name": "Music Library",
        "description": "Main music library directory",
        "default": "~/Music/Library",
    },
    "downloads": {
        "name": "Downloads",
        "description": "Directory for downloaded music files",
        "default": "~/Downloads/Music",
    },
    "temp": {
        "name": "Temporary Files",
        "description": "Directory for temporary files during processing",
        "default": "~/.flaccid/temp",
    },
    "cache": {
        "name": "Cache",
        "description": "Directory for cached metadata and thumbnails",
        "default": "~/.flaccid/cache",
    },
    "exports": {
        "name": "Exports",
        "description": "Directory for exported playlists and metadata",
        "default": "~/Documents/FLACCID/Exports",
    },
    "backups": {
        "name": "Backups",
        "description": "Directory for configuration and database backups",
        "default": "~/.flaccid/backups",
    },
}


def get_config(config_file: Optional[str] = None) -> PathConfig:
    """Get PathConfig instance."""
    if config_file:
        return PathConfig(Path(config_file))
    return PathConfig()


@app.command("library")
def set_library(
    path: str = typer.Argument(..., help="Path to music library directory")
):
    """
    Set the music library path.

    Args:
        path: Path to the music library directory
    """
    config = get_config()

    if config.set_path("library", path):
        console.print(f"✅ Library path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set library path.", style="red")
        raise typer.Exit(1)


@app.command("downloads")
def set_downloads(path: str = typer.Argument(..., help="Path to downloads directory")):
    """
    Set the downloads path.

    Args:
        path: Path to the downloads directory
    """
    config = get_config()

    if config.set_path("downloads", path):
        console.print(f"✅ Downloads path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set downloads path.", style="red")
        raise typer.Exit(1)


@app.command("temp")
def set_temp(path: str = typer.Argument(..., help="Path to temporary files directory")):
    """
    Set the temporary files path.

    Args:
        path: Path to the temporary files directory
    """
    config = get_config()

    if config.set_path("temp", path):
        console.print(f"✅ Temporary files path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set temporary files path.", style="red")
        raise typer.Exit(1)


@app.command("cache")
def set_cache(path: str = typer.Argument(..., help="Path to cache directory")):
    """
    Set the cache path.

    Args:
        path: Path to the cache directory
    """
    config = get_config()

    if config.set_path("cache", path):
        console.print(f"✅ Cache path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set cache path.", style="red")
        raise typer.Exit(1)


@app.command("exports")
def set_exports(path: str = typer.Argument(..., help="Path to exports directory")):
    """
    Set the exports path.

    Args:
        path: Path to the exports directory
    """
    config = get_config()

    if config.set_path("exports", path):
        console.print(f"✅ Exports path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set exports path.", style="red")
        raise typer.Exit(1)


@app.command("backups")
def set_backups(path: str = typer.Argument(..., help="Path to backups directory")):
    """
    Set the backups path.

    Args:
        path: Path to the backups directory
    """
    config = get_config()

    if config.set_path("backups", path):
        console.print(f"✅ Backups path set to: {path}", style="green")
    else:
        console.print("❌ Failed to set backups path.", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_paths():
    """List all configured paths."""
    config = get_config()
    paths = config.get_all_paths()

    console.print("[bold]Configured Paths:[/bold]")

    table = Table()
    table.add_column("Path Type", style="cyan")
    table.add_column("Description", style="yellow")
    table.add_column("Current Path", style="green")
    table.add_column("Status", style="white")

    for path_type, path_info in PATH_TYPES.items():
        current_path = paths.get(path_type)

        if current_path:
            path_obj = Path(current_path)
            status = "✅ Exists" if path_obj.exists() else "❌ Missing"
            table.add_row(
                path_info["name"], path_info["description"], current_path, status
            )
        else:
            table.add_row(
                path_info["name"],
                path_info["description"],
                "Not set",
                "❌ Not configured",
            )

    console.print(table)


@app.command("check")
def check_paths():
    """Check if all configured paths exist and are accessible."""
    config = get_config()
    paths = config.get_all_paths()

    console.print("🔍 Checking configured paths...")

    issues = []

    for path_type, path_value in paths.items():
        path_obj = Path(path_value)
        path_info = PATH_TYPES.get(path_type, {"name": path_type.title()})

        console.print(f"  📁 {path_info['name']}: {path_value}")

        if not path_obj.exists():
            issues.append(f"❌ {path_info['name']} does not exist: {path_value}")
        elif not path_obj.is_dir():
            issues.append(f"❌ {path_info['name']} is not a directory: {path_value}")
        elif not os.access(path_value, os.R_OK):
            issues.append(f"❌ {path_info['name']} is not readable: {path_value}")
        elif not os.access(path_value, os.W_OK):
            issues.append(f"⚠️  {path_info['name']} is not writable: {path_value}")
        else:
            console.print("     ✅ OK")

    if issues:
        console.print("\n[bold red]Issues Found:[/bold red]")
        for issue in issues:
            console.print(f"  {issue}")
        raise typer.Exit(1)
    else:
        console.print("\n✅ All paths are accessible.", style="green")


@app.command("reset")
def reset_paths(
    path_type: str = typer.Argument(
        None, help="Specific path type to reset (optional)"
    ),
    all: bool = typer.Option(False, "--all", help="Reset all paths to defaults"),
):
    """
    Reset path configuration to defaults.

    Args:
        path_type: Specific path type to reset (optional)
        all: Reset all paths to defaults
    """
    config = get_config()

    if all:
        if not typer.confirm("Reset ALL paths to defaults?"):
            console.print("Cancelled.", style="yellow")
            return

        console.print("🔄 Resetting all paths to defaults...")

        for path_type, path_info in PATH_TYPES.items():
            default_path = path_info["default"]
            if config.set_path(path_type, default_path):
                console.print(f"  ✅ {path_info['name']}: {default_path}")
            else:
                console.print(f"  ❌ Failed to reset {path_info['name']}")

        console.print("✅ All paths reset to defaults.", style="green")

    elif path_type:
        if path_type not in PATH_TYPES:
            console.print(f"❌ Unknown path type: {path_type}", style="red")
            console.print(f"Available types: {', '.join(PATH_TYPES.keys())}")
            raise typer.Exit(1)

        path_info = PATH_TYPES[path_type]
        default_path = path_info["default"]

        if not typer.confirm(f"Reset {path_info['name']} to default ({default_path})?"):
            console.print("Cancelled.", style="yellow")
            return

        if config.set_path(path_type, default_path):
            console.print(
                f"✅ {path_info['name']} reset to: {default_path}", style="green"
            )
        else:
            console.print(f"❌ Failed to reset {path_info['name']}", style="red")
            raise typer.Exit(1)

    else:
        console.print(
            "❌ Specify a path type or use --all to reset all paths.", style="red"
        )
        raise typer.Exit(1)


@app.command("remove")
def remove_path(path_type: str = typer.Argument(..., help="Path type to remove")):
    """
    Remove a configured path.

    Args:
        path_type: Path type to remove
    """
    if path_type not in PATH_TYPES:
        console.print(f"❌ Unknown path type: {path_type}", style="red")
        console.print(f"Available types: {', '.join(PATH_TYPES.keys())}")
        raise typer.Exit(1)

    config = get_config()
    path_info = PATH_TYPES[path_type]

    current_path = config.get_path(path_type)
    if not current_path:
        console.print(f"❌ {path_info['name']} is not configured.", style="red")
        return

    if not typer.confirm(f"Remove {path_info['name']} configuration ({current_path})?"):
        console.print("Cancelled.", style="yellow")
        return

    if config.remove_path(path_type):
        console.print(f"✅ {path_info['name']} configuration removed.", style="green")
    else:
        console.print(
            f"❌ Failed to remove {path_info['name']} configuration.", style="red"
        )
        raise typer.Exit(1)


@app.command("init")
def init_paths():
    """Initialize all paths with default values."""
    config = get_config()

    console.print("🚀 Initializing FLACCID paths with defaults...")

    for path_type, path_info in PATH_TYPES.items():
        current_path = config.get_path(path_type)

        if current_path:
            console.print(
                f"  ⏭️  {path_info['name']} already configured: {current_path}"
            )
            continue

        default_path = path_info["default"]

        if config.set_path(path_type, default_path):
            console.print(f"  ✅ {path_info['name']}: {default_path}")
        else:
            console.print(f"  ❌ Failed to initialize {path_info['name']}")

    console.print("✅ Path initialization complete.", style="green")


@app.command("export")
def export_paths(
    output: str = typer.Option("flaccid-paths.json", help="Output file path")
):
    """
    Export path configuration to a file.

    Args:
        output: Output file path
    """
    config = get_config()
    paths = config.get_all_paths()

    if not paths:
        console.print("❌ No paths configured to export.", style="red")
        return

    export_data = {
        "exported_at": str(Path.cwd()),
        "paths": paths,
        "path_types": PATH_TYPES,
    }

    output_path = Path(output)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)

        console.print(f"✅ Paths exported to: {output_path}", style="green")
    except Exception as e:
        console.print(f"❌ Error exporting paths: {e}", style="red")
        raise typer.Exit(1)


@app.command("import")
def import_paths(input_file: str = typer.Argument(..., help="Input file path")):
    """
    Import path configuration from a file.

    Args:
        input_file: Input file path
    """
    input_path = Path(input_file)

    if not input_path.exists():
        console.print(f"❌ File not found: {input_file}", style="red")
        raise typer.Exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            import_data = yaml.safe_load(f)

        paths = import_data.get("paths", {})

        if not paths:
            console.print("❌ No paths found in import file.", style="red")
            return

        console.print(f"📂 Importing {len(paths)} paths from {input_file}...")

        config = get_config()

        for path_type, path_value in paths.items():
            if path_type in PATH_TYPES:
                if config.set_path(path_type, path_value):
                    console.print(f"  ✅ {PATH_TYPES[path_type]['name']}: {path_value}")
                else:
                    console.print(
                        f"  ❌ Failed to import {PATH_TYPES[path_type]['name']}"
                    )
            else:
                console.print(f"  ⚠️  Unknown path type: {path_type}", style="yellow")

        console.print("✅ Path import complete.", style="green")

    except Exception as e:
        console.print(f"❌ Error importing paths: {e}", style="red")
        raise typer.Exit(1)


@app.command("usage")
def path_usage():
    """Show disk usage for configured paths."""
    config = get_config()
    paths = config.get_all_paths()

    if not paths:
        console.print("❌ No paths configured.", style="red")
        return

    console.print("💾 Disk usage for configured paths:")

    table = Table()
    table.add_column("Path Type", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Files", style="blue")

    for path_type, path_value in paths.items():
        path_obj = Path(path_value)
        path_info = PATH_TYPES.get(path_type, {"name": path_type.title()})

        if path_obj.exists():
            try:
                total_size = 0
                file_count = 0

                for item in path_obj.rglob("*"):
                    if item.is_file():
                        total_size += item.stat().st_size
                        file_count += 1

                # Format size
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if total_size < 1024.0:
                        size_str = f"{total_size:.1f}{unit}"
                        break
                    total_size /= 1024.0

                table.add_row(path_info["name"], path_value, size_str, str(file_count))

            except Exception as e:
                table.add_row(path_info["name"], path_value, "Error", f"Error: {e}")
        else:
            table.add_row(path_info["name"], path_value, "N/A", "Path not found")

    console.print(table)
