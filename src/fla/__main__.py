"""
Allows `python -m fla` and keeps `from fla.__main__ import app` working.
"""
from flaccid.__main__ import app    # Typer root command

if __name__ == "__main__":
    app()
