"""
Entrypoint so `python -m flaccid` works.
"""

from __future__ import annotations

import typer

from flaccid import cli


def main() -> None:
    """Wrapper for ``typer.run()``."""
    typer.run(cli.app)


if __name__ == "__main__":
    main()
