from __future__ import annotations

"""Plugin registry utilities."""

from .apple import AppleMusicPlugin
from .beatport import BeatportPlugin
from .discogs import DiscogsPlugin
from .lyrics import LyricsPlugin
from .qobuz import QobuzPlugin
from .tidal import TidalPlugin
from .base import MetadataProviderPlugin

# Mapping of provider names to plugin classes
PLUGINS: dict[str, type[MetadataProviderPlugin]] = {
    "apple": AppleMusicPlugin,
    "beatport": BeatportPlugin,
    "discogs": DiscogsPlugin,
    "lyrics": LyricsPlugin,
    "qobuz": QobuzPlugin,
    "tidal": TidalPlugin,
}


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
    try:
        return PLUGINS[name.lower()]
    except KeyError as exc:  # pragma: no cover - error path
        raise ValueError(f"Unknown provider: {name}") from exc

