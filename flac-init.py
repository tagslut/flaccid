import subprocess
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def init():
    """Initialize FLACCID CLI: install dependencies and prepare environment."""
    print("🔧 Starting FLACCID setup...")
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        raise typer.Exit("❌ pyproject.toml not found.")

    try:
        subprocess.run(["poetry", "--version"], check=True)
    except subprocess.CalledProcessError:
        typer.echo("📥 Poetry not found. Please install Poetry.")
        raise typer.Exit(1)

    subprocess.run(["poetry", "config", "virtualenvs.in-project", "true"])
    subprocess.run(
        ["poetry", "install", "--sync", "--no-interaction", "--with", "dev"], check=True
    )

    if Path(".pre-commit-config.yaml").exists():
        subprocess.run(["poetry", "run", "pre-commit", "install"])
        subprocess.run(
            ["poetry", "run", "pre-commit", "run", "--all-files"], check=False
        )

    typer.echo("✅ FLACCID setup complete.")


if __name__ == "__main__":
    app()
