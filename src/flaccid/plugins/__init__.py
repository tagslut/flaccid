"""Plugin registry."""

from __future__ import annotations

from .registry import PLUGINS, get_provider

# Export discovered plugin classes for convenience
_classes = PLUGINS.values()

for _cls in _classes:
    globals()[_cls.__name__] = _cls

__all__ = [
    "PLUGINS",
    "get_provider",
    *[cls.__name__ for cls in _classes],
]
