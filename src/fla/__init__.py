"""
Compatibility alias: importing `fla` returns the real `flaccid` package.
"""
import importlib, sys as _sys

_mod = importlib.import_module("flaccid")   # load canonical package
_sys.modules[__name__] = _mod               # register alias