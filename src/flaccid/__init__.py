"""FLACCID command‑line interface (Typer)."""
from __future__ import annotations
import importlib
import sys as _sys
import typer  # Added to resolve undefined variable error

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

# ------------------------------------------------------------------
# Legacy “fla” test‑suite expectations
# ------------------------------------------------------------------

# a)  expose the CLI module (with .app) as fla.__main__
import importlib as _il, sys as _s
_s.modules.setdefault("fla.__main__", _il.import_module("flaccid.cli"))

# b)  forward every sub‑module of top‑level `shared` so
#     `from fla.shared.xyz import …` works.
try:
    _shared_pkg = _il.import_module("shared")
    _s.modules.setdefault("fla.shared", _shared_pkg)
    for _name, _mod in list(_s.modules.items()):
        if _name.startswith("shared.") and "." not in _name[len("shared.") :]:
            # register as fla.shared.<submodule>
            _s.modules.setdefault(f"fla.{_name}", _mod)
except ModuleNotFoundError:
    pass
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