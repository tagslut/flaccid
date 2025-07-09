"""
Canonical FLACCID package.

Exposes sub‑packages lazily and provides a legacy `fla` import‑alias so
the existing test‑suite (`import fla`) keeps working.
"""
from __future__ import annotations

import importlib
import sys as _sys
from types import ModuleType as _ModuleType

__all__ = ["shared", "tag", "get", "lib", "core", "set"]

# ------------------------------------------------------------------
# Lazy‑loader: `from flaccid import shared` will auto‑import the sub‑package
# ------------------------------------------------------------------
def __getattr__(name: str):  # type: ignore[override]
    if name in __all__:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(name)


# ------------------------------------------------------------------
# Legacy alias ‑‑ users/tests do `import fla` and expect the same module
# ------------------------------------------------------------------

_sys.modules.setdefault("fla", _sys.modules[__name__])

# ------------------------------------------------------------------
# Bridge to the *top‑level* `shared` package that already exists in
# the repository root.  This satisfies imports such as
# `from flaccid.shared.qobuz_api import QobuzAPI` used by the test‑suite
# without duplicating code.  If the external package is missing we
# simply ignore the error so the project can evolve.
# ------------------------------------------------------------------
try:
    _sys.modules.setdefault(f"{__name__}.shared", importlib.import_module("shared"))
except ModuleNotFoundError:
    # No standalone `shared` package present – tests will stub it later.
    pass


# ------------------------------------------------------------------
# Mirror key sub‑modules under the *alias* top‑level package `fla`
# so import statements like `from fla.__main__ import app` resolve.
# ------------------------------------------------------------------
_alias = _sys.modules["fla"]  # we registered this alias earlier

# List of sub‑modules frequently imported by the legacy tests
_legacy_subs = ["__main__", "shared"]

for _name in _legacy_subs:
    try:
        _mod: _ModuleType = importlib.import_module(f"{__name__}.{_name}")
    except ModuleNotFoundError:
        # e.g. shared might not exist yet; skip silently
        continue
    _sys.modules.setdefault(f"fla.{_name}", _mod)
