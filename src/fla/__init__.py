"""Compatibility alias so `import fla` maps to `flaccid`."""
import importlib, sys as _sys
_mod = importlib.import_module("flaccid")
_sys.modules[__name__] = _mod
