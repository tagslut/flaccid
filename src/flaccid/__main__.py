"""
`python -m flaccid` / `fla` entry-point.
"""
from flaccid.cli import app   # ← import the real Typer app

if __name__ == "__main__":
    app()                     # Hand off to Typer
