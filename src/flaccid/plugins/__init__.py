"""Plugin registry."""

from __future__ import annotations

from .registry import PLUGINS, get_provider, load_plugins
from .lyrics import LyricsPlugin

# Export discovered plugin classes for convenience
load_plugins()
_classes = PLUGINS.values()

for _cls in _classes:
    globals()[_cls.__name__] = _cls

__all__ = [
    "PLUGINS",
    "get_provider",
    "LyricsPlugin",
    *[cls.__name__ for cls in _classes],
]
