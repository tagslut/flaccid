"""
Thin compatibility layer so legacy code/tests that do `import fla`
continue to work even though the real package is `flaccid`.
"""

from __future__ import annotations
import importlib, sys as _sys

# Re‑export the canonical package as *this* module
_mod = importlib.import_module("flaccid")
_sys.modules[__name__] = _mod

# Make `from fla import app` (or fla.app) resolve
from flaccid.cli import app           # noqa: E402  (circular but harmless)
setattr(_mod, "app", app)

# ------------------------------------------------------------------
#  expose the standalone “shared” namespace under fla.shared
#  so tests can import `fla.shared.qobuz_api`, etc.
# ------------------------------------------------------------------
try:
    _shared = importlib.import_module("shared")
    _sys.modules.setdefault("fla.shared", _shared)
    for _name, _m in list(_sys.modules.items()):
        if _name.startswith("shared."):
            _sys.modules.setdefault(f"fla.{_name}", _m)
except ModuleNotFoundError:
    pass
