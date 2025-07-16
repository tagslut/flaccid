"""Plugin registry utilities."""

from __future__ import annotations

import os
from pathlib import Path

from .base import MetadataProviderPlugin
from .loader import PluginLoader

# Mapping of provider names to plugin classes
paths = [Path(__file__).parent]
extra = os.getenv("FLACCID_PLUGIN_PATH")
if extra:
    paths.extend(Path(p) for p in extra.split(os.pathsep))

_loader = PluginLoader(*paths)
PLUGINS: dict[str, type[MetadataProviderPlugin]] = {}


def load_plugins() -> None:
    """Discover and cache available plugins."""
    if not PLUGINS:
        PLUGINS.update(_loader.discover())


def get_provider(name: str) -> type[MetadataProviderPlugin]:
    """Return the plugin class registered for ``name``.

    Parameters
    ----------
    name:
        Provider name. Lookup is case-insensitive.

    Returns
    -------
    type[MetadataProviderPlugin]
        The plugin class corresponding to ``name``.

    Raises
    ------
    ValueError
        If ``name`` is not a known provider.
    """
    load_plugins()
    try:
        return PLUGINS[name.lower()]
    except KeyError as exc:  # pragma: no cover - error path
        raise ValueError(f"Unknown provider: {name}") from exc
