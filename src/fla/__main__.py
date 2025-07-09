"""
Entrypoint so `python -m fla` works.
"""

import typer
from flaccid import cli

if __name__ == "__main__":
    typer.run(cli.app)
