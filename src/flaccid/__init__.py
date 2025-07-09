"""FLACCID command‑line interface (Typer)."""
from __future__ import annotations
import importlib
import sys as _sys

# preload common sub-packages if they exist
for _sub in ("shared", "tag", "get", "lib", "core", "set"):
    try:
        importlib.import_module(f"{__name__}.{_sub}", package=__name__)
    except ModuleNotFoundError:
        pass

# ------------------------------------------------------------------
# compatibility aliases
_sys.modules.setdefault("fla", _sys.modules[__name__])          # import fla → flaccid
_sys.modules.setdefault("fla.__main__", importlib.import_module("flaccid.cli"))
# ------------------------------------------------------------------

__all__ = ["shared", "tag", "get", "lib", "core", "set"]

# Root Typer instance exported for tests and entry‑points
app = typer.Typer(name="flaccid", help="FLACCID metadata CLI toolkit")


@app.callback()
def _cli_root() -> None:  # noqa: D401
    """FLACCID CLI root command."""
    # Add sub‑commands in dedicated modules later.
    pass


if __name__ == "__main__":  # pragma: no cover
    app()