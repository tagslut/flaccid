import typer

app = typer.Typer(name="core", help="Core utilities and tools.")


@app.command("version")
def version():
    """Show FLACCID version information."""
    print("FLACCID v0.1.0")
    print("Modular FLAC CLI Toolkit")


@app.command("config")
def config():
    """Show configuration directory."""
    from pathlib import Path

    config_dir = Path.home() / ".flaccid"
    print(f"Configuration directory: {config_dir}")
    print(f"Database: {config_dir / 'library.db'}")
    print(f"Paths config: {config_dir / 'paths.json'}")


@app.command("help")
def help_command():
    """Show extended help and usage examples."""
    help_text = """
FLACCID: Modular FLAC CLI Toolkit

Usage Examples:
  fla set auth qobuz                    # Set up Qobuz credentials
  fla set path library ~/Music         # Set library path
  fla tag qobuz track file.flac 12345  # Tag file with Qobuz track ID
  fla tag qobuz search file.flac       # Interactive search and tag
  fla lib scan dir ~/Music             # Scan library directory
  fla lib index build ~/Music          # Build library index
  fla lib index search "artist name"   # Search indexed library
  fla get qobuz track 12345            # Download from Qobuz

For more help on specific commands:
  fla [command] --help
    """
    print(help_text)
