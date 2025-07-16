#!/usr/bin/env python3
"""Module so `python -m flaccid` works.

It simply delegates to the Typer application defined in
`flaccid.cli.__init__`.
"""

from flaccid.cli import app


def main():
    """Entry point for the CLI when installed via pip/poetry."""
    app()


if __name__ == "__main__":
    main()
