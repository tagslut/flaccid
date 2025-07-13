"""
Thin façade that re-exports service-specific helper classes
used by the legacy test-suite.
"""

from importlib import import_module as _imp


# Lazy-proxy to keep test imports working; extend as real code is added
def __getattr__(name: str):
    return _imp(f"flaccid.shared.{name}")
