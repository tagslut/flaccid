"""
Legacy *alias* package so that existing code/tests written for the old
namespace ``fla`` continue to work.  It simply re‑exports the canonical
``flaccid`` package at the same module path and mirrors a few frequently
imported sub‑modules (``__main__``, ``shared``).
"""

from __future__ import annotations

import importlib
import sys as _sys
from types import ModuleType as _ModuleType

# Import real package and assign it to this alias entry
_pkg: _ModuleType = importlib.import_module("flaccid")
_sys.modules.setdefault(__name__, _pkg)

# Expose common sub‑modules under the alias, too
for _sub in ("__main__", "shared"):
    try:
        _mod = importlib.import_module(f"flaccid.{_sub}")
    except ModuleNotFoundError:
        continue
    _sys.modules[f"{__name__}.{_sub}"] = _mod

# Explicit re‑export for `from fla import app` patterns
if hasattr(_pkg, "app"):
    app = _pkg.app  # type: ignore[attr-defined]
