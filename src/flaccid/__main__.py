"""Package entry‑point so that both

    $ python -m flaccid
    $ poetry run flaccid …

work consistently."""

from __future__ import annotations

from flaccid import cli

# ---------------------------------------------------------------------------
# Expose the Typer application expected by the console‑script declaration
# (`flaccid = "flaccid.__main__:app"` in pyproject.toml).
# ---------------------------------------------------------------------------

app = cli.app  # Console script looks for this symbol


def main() -> None:  # pragma: no cover
    """Run the CLI when executed as a module."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
